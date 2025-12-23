
import csv
import io
from typing import List
from uuid import UUID

from src.domain.entities.construction import ItemPlanejado
from src.use_cases.ports.construction_repository import ConstructionRepositoryInterface

class ImportConstructionItemsUseCase:
    def __init__(self, repository: ConstructionRepositoryInterface):
        self.repository = repository

    async def execute(self, obra_id: UUID, file_content: bytes, filename: str) -> dict:
        """
        Parses a CSV file and creates construction items.
        Supports 'PERFIS.csv' and 'ACESSÓRIOS.csv' layouts.
        """
        decoded_content = file_content.decode('utf-8-sig') # Handle potential BOM
        csv_reader = csv.DictReader(io.StringIO(decoded_content), delimiter=';') # Assuming Excel CSV export usually uses ; in BR

        # Fallback to comma if keys look weird or single column
        if csv_reader.fieldnames and len(csv_reader.fieldnames) <= 1:
             csv_reader = csv.DictReader(io.StringIO(decoded_content), delimiter=',')

        items_to_create = []
        errors = []

        # Guess Category based on filename or content
        is_profile = 'PERFIL' in filename.upper() or 'PERFIS' in filename.upper()
        default_category = 'PERFIL' if is_profile else 'COMPONENTE'

        for index, row in enumerate(csv_reader):
            try:
                # Normalize keys (strip whitespace, lowercase)
                row = {k.strip().lower(): v for k, v in row.items() if k}

                # Check required fields
                # "PERFIS.csv": Grupo, Código, Descrição, Cor, Qtd Total, Qtd Entregue, Preços
                # "ACESSÓRIOS.csv": Grupo, Código, Descrição, Unidade, Cor, Qtd, Preços, NFs

                codigo = row.get('código') or row.get('codigo')
                if not codigo:
                    continue # Skip empty lines

                descricao = row.get('descrição') or row.get('descricao')
                grupo = row.get('grupo')
                cor = row.get('cor')
                unidade = row.get('unidade')

                # Quantity
                qtd_raw = row.get('qtd total') or row.get('qtd') or row.get('quantidade') or '0'
                qtd = self._parse_float(qtd_raw)

                # Price
                preco_raw = row.get('preços') or row.get('precos') or row.get('preco') or '0'
                preco = self._parse_float(preco_raw)

                # Qtd Entregue (Migration of legacy data?)
                qtd_entregue_raw = row.get('qtd entregue') or '0'
                qtd_entregue_legacy = self._parse_float(qtd_entregue_raw)

                item = ItemPlanejado(
                    obra_id=obra_id,
                    codigo_item=codigo,
                    descricao=descricao,
                    grupo=grupo,
                    cor=cor,
                    unidade=unidade,
                    quantidade_total=qtd,
                    preco_venda_unitario=preco,
                    categoria=default_category
                )

                # If there's already delivered qty in CSV, we might handle it later or ignore
                # as ItemPlanejado doesn't have 'qtd_entregue', it's calculated from 'entregas'.
                # But requirement said "Realizar o de-para", implying strict structure mapping.
                # If we want to keep the legacy 'entregue' count without creating delivery records,
                # we'd need a field 'legacy_delivered' or create a dummy delivery.
                # For now, sticking to the Item definition.

                items_to_create.append(item)

            except Exception as e:
                errors.append(f"Row {index}: {str(e)}")

        if items_to_create:
            await self.repository.create_items_bulk(items_to_create)

        return {
            "total_processed": len(items_to_create),
            "errors": errors
        }

    def _parse_float(self, value: str) -> float:
        if not value:
            return 0.0
        try:
            # Handle Brazilian number format '1.234,56' -> '1234.56'
            if ',' in value and '.' in value:
                 value = value.replace('.', '').replace(',', '.')
            elif ',' in value:
                 value = value.replace(',', '.')
            return float(value)
        except ValueError:
            return 0.0
