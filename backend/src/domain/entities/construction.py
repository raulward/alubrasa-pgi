
import uuid
from datetime import date
from typing import List, Optional
from sqlalchemy import Column, String, Float, Date, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.frameworks.db.base import Base

class Obra(Base):
    __tablename__ = 'obras'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String, nullable=True) # Assuming simple Obra model for now to satisfy FK

    # Relationships
    itens_planejados = relationship("ItemPlanejado", back_populates="obra", lazy="selectin")


class ItemPlanejado(Base):
    __tablename__ = 'items_planejados'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    obra_id = Column(UUID(as_uuid=True), ForeignKey('obras.id'), nullable=False)

    codigo_item = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    unidade = Column(String, nullable=True)
    quantidade_total = Column(Float, nullable=False, default=0.0)
    preco_venda_unitario = Column(Float, nullable=False, default=0.0)
    categoria = Column(String, nullable=True) # Enum: 'PERFIL', 'COMPONENTE', 'VIDRO' - Using String for simplicity or Enum/Check constraint if preferred

    # Relationships
    obra = relationship("Obra", back_populates="itens_planejados")
    entregas = relationship("EntregaRealizada", back_populates="item_planejado", lazy="selectin")


class EntregaRealizada(Base):
    __tablename__ = 'entregas_realizadas'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_planejado_id = Column(UUID(as_uuid=True), ForeignKey('items_planejados.id'), nullable=False)

    numero_nf = Column(String, nullable=True)
    data_faturamento = Column(Date, nullable=False)
    quantidade_entregue = Column(Float, nullable=False, default=0.0)

    # Relationships
    item_planejado = relationship("ItemPlanejado", back_populates="entregas")
