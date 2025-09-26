# utils/migrations/crtl_orc_migration.py
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Row
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# CONFIG — ajuste aqui para casar com SEU schema/tabela já existentes
# =============================================================================
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não definido no .env")

DEST_SCHEMA = os.getenv("ORC_SCHEMA", "public")         # ajuste se necessário
DEST_TABLE  = os.getenv("ORC_TABLE", "orcamentos_ctrl") # ajuste se necessário

# Arquivo esperado em <repo>/data/controle_orc_final.xlsx (pode ser .csv/.xls)
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_CANDIDATES = [
    BASE_DIR / "data" / "controle_orc_final.xlsx",
    BASE_DIR / "data" / "controle_orc_final.csv",
    BASE_DIR / "data" / "controle_orc_final.xls",
    BASE_DIR / "controle_orc_final.xlsx",
    BASE_DIR / "controle_orc_final.csv",
    BASE_DIR / "controle_orc_final.xls",
]

# Colunas de NEGÓCIO que planejamos levar ao destino (podem existir ou não no destino)
EXPECTED_COLS = [
    "codigo_proposta","nr_revisao","cliente_nome","obra_nome",
    "dt_competencia","dt_entrada","dt_inicio_tecnico","dt_prazo_tecnico",
    "dt_conclusao_tecnico","dt_envio_comercial","st_comercial","st_levantamento",
    "solicitante","tecnico","fornecedor","valor_orcamento","peso_kg","area_m2",
    "observacoes"
]

# Mapeamento baseado nos NOMES REAIS da planilha (conforme prints)
RENAME_MAP = {
    "codigo": "codigo_proposta",
    "revisao": "nr_revisao",
    "cliente": "cliente_nome",
    "obra": "obra_nome",
    "mes": "dt_competencia",
    "dt_entrada": "dt_entrada",
    "dt_inicio": "dt_inicio_tecnico",
    "dt_prazo_depto_tecnico": "dt_prazo_tecnico",
    "dt_conclusao_depto_tecnico": "dt_conclusao_tecnico",
    "dt_enviado_ao_comercial": "dt_envio_comercial",
    "st_status_comercial": "st_comercial",
    "st_status_do_levantamento_tecnico": "st_levantamento",
    "solicitante": "solicitante",
    "tecnico": "tecnico",
    "fornecedor": "fornecedor",
    "valor_orcamento_r": "valor_orcamento",
    "peso_kg": "peso_kg",
    "area_m2": "area_m2",
    # "observacoes" não existe na planilha → criaremos nula
}

# =============================================================================
# HELPERS
# =============================================================================
def find_data_path() -> Path:
    for p in DATA_CANDIDATES:
        if p.exists():
            return p
    raise FileNotFoundError(
        f"Arquivo não encontrado. Coloque em {DATA_CANDIDATES[0].parent} "
        f"com nome controle_orc_final.xlsx (ou .csv/.xls)."
    )

def load_tabular(file_path: Path) -> pd.DataFrame:
    ext = file_path.suffix.lower()
    if ext in [".xlsx", ".xlsm"]:
        try:
            return pd.read_excel(file_path, engine="openpyxl", dtype=str)
        except Exception as e:
            print(f"[WARN] Falha lendo como .xlsx ({type(e).__name__}: {e}). Tentando fallback…")
    if ext == ".xls":
        try:
            return pd.read_excel(file_path, engine="xlrd", dtype=str)  # xlrd<=1.2.0 pode ser necessário
        except Exception as e:
            print(f"[WARN] Falha lendo como .xls ({type(e).__name__}: {e}).")
    if ext == ".csv":
        try:
            return pd.read_csv(file_path, dtype=str)
        except Exception:
            return pd.read_csv(file_path, dtype=str, sep=";")
    try:
        return pd.read_excel(file_path, engine="openpyxl", dtype=str)
    except Exception:
        try:
            return pd.read_csv(file_path, dtype=str)
        except Exception:
            return pd.read_csv(file_path, dtype=str, sep=";")

def clean_strings(df: pd.DataFrame) -> pd.DataFrame:
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].map(lambda x: x.strip() if isinstance(x, str) else x)
    return df.replace({"": None, "NULL": None, "null": None, "-": None})

def ensure_staging(engine: Engine) -> None:
    sql = """
    create schema if not exists tmp;

    create table if not exists tmp.orcamentos_ctrl_stg (
      row_id bigserial primary key,
      codigo_proposta text,
      nr_revisao text,
      cliente_nome text,
      obra_nome text,
      dt_competencia text,
      dt_entrada text,
      dt_inicio_tecnico text,
      dt_prazo_tecnico text,
      dt_conclusao_tecnico text,
      dt_envio_comercial text,
      st_comercial text,
      st_levantamento text,
      solicitante text,
      tecnico text,
      fornecedor text,
      valor_orcamento text,
      peso_kg text,
      area_m2 text,
      observacoes text,
      loaded_at timestamp default now()
    );
    """
    with engine.begin() as con:
        con.execute(text(sql))

def install_sql_helpers(engine: Engine) -> None:
    sql = """
    create schema if not exists ref;

    create or replace function ref.parse_date_flex(s text)
    returns date language sql immutable as $$
      select coalesce(
        to_date(nullif(s,''), 'YYYY-MM-DD'),
        to_date(nullif(s,''), 'DD/MM/YYYY'),
        to_date(nullif(s,''), 'DD/MM/YY')
      )
    $$;

    create or replace function ref.parse_numeric(s text)
    returns numeric language plpgsql immutable as $$
    declare t text;
    begin
      if s is null then return null; end if;
      t := replace(replace(s, '.', ''), ',', '.');
      return nullif(t,'')::numeric;
    end;
    $$;
    """
    with engine.begin() as con:
        con.execute(text(sql))

def table_exists(engine: Engine, schema: str, table: str) -> bool:
    q = text("""
        select 1
        from information_schema.tables
        where table_schema = :schema and table_name = :table
        limit 1
    """)
    with engine.connect() as con:
        r = con.execute(q, {"schema": schema, "table": table}).first()
        return r is not None

def get_table_columns(engine: Engine, schema: str, table: str) -> List[str]:
    q = text("""
        select column_name
        from information_schema.columns
        where table_schema = :schema and table_name = :table
        order by ordinal_position
    """)
    with engine.connect() as con:
        rows = con.execute(q, {"schema": schema, "table": table}).fetchall()
    return [r[0] for r in rows]

def has_unique_on_codigo_revisao(engine: Engine, schema: str, table: str) -> bool:
    q = text("""
        select 1
        from pg_indexes
        where schemaname = :schema
          and tablename = :table
          and indexdef ilike '%unique%'
          and indexdef ilike '%(codigo_proposta, nr_revisao)%'
        limit 1
    """)
    with engine.connect() as con:
        r = con.execute(q, {"schema": schema, "table": table}).first()
        return r is not None

def build_select_expressions(dest_cols: List[str]) -> Dict[str, str]:
    """
    Constrói expressões SELECT para cada coluna de destino suportada,
    aplicando as conversões do plano (datas, numéricos, fallbacks controlados).
    Só retornamos expressões para colunas que existirem no destino.
    """
    expr: Dict[str, str] = {}

    # Texto/base
    if "codigo_proposta" in dest_cols:
        expr["codigo_proposta"] = "coalesce(nullif(trim(s.codigo_proposta), ''), 'SEM_CODIGO')"
    if "nr_revisao" in dest_cols:
        expr["nr_revisao"] = "coalesce(nullif(trim(s.nr_revisao), ''), '0')::int"

    for c in ["cliente_nome","obra_nome","st_comercial","st_levantamento",
              "solicitante","tecnico","fornecedor","observacoes"]:
        if c in dest_cols:
            expr[c] = f"nullif(trim(s.{c}), '')"

    # Datas
    for c in ["dt_entrada","dt_inicio_tecnico","dt_prazo_tecnico",
              "dt_conclusao_tecnico","dt_envio_comercial"]:
        if c in dest_cols:
            expr[c] = f"ref.parse_date_flex(s.{c})"

    if "dt_competencia" in dest_cols:
        expr["dt_competencia"] = """
            coalesce(
              ref.parse_date_flex(s.dt_competencia),
              ref.parse_date_flex(s.dt_entrada),
              date_trunc('month', now())::date
            )
        """

    # Numéricos
    if "valor_orcamento" in dest_cols:
        expr["valor_orcamento"] = "ref.parse_numeric(s.valor_orcamento)::numeric(18,2)"
    if "peso_kg" in dest_cols:
        expr["peso_kg"] = "ref.parse_numeric(s.peso_kg)::numeric(18,4)"
    if "area_m2" in dest_cols:
        expr["area_m2"] = "ref.parse_numeric(s.area_m2)::numeric(18,4)"

    # Timestamps de auditoria (se existirem no destino)
    if "created_at" in dest_cols:
        expr["created_at"] = "now()"
    if "updated_at" in dest_cols:
        expr["updated_at"] = "now()"

    # ID (se existir no destino e aceitar default, NÃO setamos; se exigir valor, ajuste aqui)
    # -> não definimos "id" propositalmente para respeitar default/sequence existente.

    return expr

def insert_or_upsert(engine: Engine, schema: str, table: str) -> None:
    # Colunas reais do destino
    dest_cols = get_table_columns(engine, schema, table)

    # Monta expressões só para as colunas que o destino contém
    select_exprs = build_select_expressions(dest_cols)
    if not select_exprs:
        raise RuntimeError(f"Nenhuma coluna mapeável encontrada em {schema}.{table}.")

    cols_sql = ", ".join(select_exprs.keys())
    vals_sql = ",\n      ".join(select_exprs.values())

    # Verifica se há unique(codigo_proposta, nr_revisao) para upsert
    can_upsert = {"codigo_proposta","nr_revisao"}.issubset(set(dest_cols)) and \
                 has_unique_on_codigo_revisao(engine, schema, table)

    if can_upsert:
        update_assignments = ",\n      ".join(
            f"{col} = excluded.{col}"
            for col in select_exprs.keys()
            if col not in {"codigo_proposta","nr_revisao"}  # chaves naturais não são atualizadas
        )
        sql = f"""
        insert into {schema}.{table} (
          {cols_sql}
        )
        select
          {vals_sql}
        from tmp.orcamentos_ctrl_stg s
        on conflict (codigo_proposta, nr_revisao)
        do update set
          {update_assignments};
        """
    else:
        # Insert simples (não mexe em constraints/tabela)
        sql = f"""
        insert into {schema}.{table} (
          {cols_sql}
        )
        select
          {vals_sql}
        from tmp.orcamentos_ctrl_stg s;
        """

    with engine.begin() as con:
        con.execute(text(sql))

# =============================================================================
# PIPELINE
# =============================================================================
def main(truncate_staging: bool = False, load_to_dest: bool = True) -> None:
    data_path = find_data_path()
    print(f"Usando arquivo: {data_path}")

    # 1) Carregar arquivo "como veio" e padronizar strings
    df_raw = load_tabular(data_path)
    df_raw = clean_strings(df_raw)

    # 2) Renomear colunas (do arquivo -> nomes de negócio do staging)
    df = df_raw.rename(columns=RENAME_MAP).copy()

    # 3) Garantir todas colunas esperadas no staging (criando nulas se faltar)
    if "observacoes" not in df.columns:
        df["observacoes"] = None
    for col in EXPECTED_COLS:
        if col not in df.columns:
            df[col] = None
    df = df[EXPECTED_COLS]

    # 4) Conexão
    engine = create_engine(DATABASE_URL)

    # 5) Garantir staging e (opcional) truncar
    ensure_staging(engine)
    if truncate_staging:
        with engine.begin() as con:
            con.execute(text("truncate table tmp.orcamentos_ctrl_stg;"))
        print("Staging truncada.")

    # 6) Escrever no staging
    with engine.begin() as con:
        df.to_sql("orcamentos_ctrl_stg", con=con, schema="tmp", if_exists="append", index=False)
    print(f"OK! {len(df)} linhas carregadas em tmp.orcamentos_ctrl_stg")

    # 7) Funções auxiliares (parse de datas/números) — não mexe na tabela destino
    install_sql_helpers(engine)

    # 8) Checagem da tabela destino (não cria, não altera)
    if not table_exists(engine, DEST_SCHEMA, DEST_TABLE):
        # Mostra o que encontramos no catálogo para te orientar, sem tocar na estrutura
        with engine.connect() as con:
            found = con.execute(text("""
                select table_schema, table_name
                from information_schema.tables
                where table_name ilike :t
                order by 1,2
            """), {"t": f"%{DEST_TABLE}%"}).fetchall()
        suggestions = "\n".join([f"- {r[0]}.{r[1]}" for r in found]) or "(nenhuma sugestão encontrada)"
        raise RuntimeError(
            f"Tabela destino {DEST_SCHEMA}.{DEST_TABLE} não existe.\n"
            f"Verifique o nome conforme seus prints e ajuste DEST_SCHEMA/DEST_TABLE.\n"
            f"Sugestões com nome parecido no catálogo:\n{suggestions}"
        )

    # 9) Inserção (ou upsert, se o seu índice único existir). Sem alterar sua tabela.
    if load_to_dest:
        insert_or_upsert(engine, DEST_SCHEMA, DEST_TABLE)
        print(f"Carga concluída em {DEST_SCHEMA}.{DEST_TABLE}")
    else:
        print("Carga na tabela destino foi pulada (load_to_dest=False).")

if __name__ == "__main__":
    # staging somente: main(truncate_staging=False, load_to_dest=False)
    main(truncate_staging=False, load_to_dest=True)
