import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy.types import Text, Numeric, Boolean
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("Defina a url para o Database")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

excel_path = "../../data/table_final.xlsx"
df_ncms = pd.read_excel(excel_path, sheet_name="NCMS")
df_cfops = pd.read_excel(excel_path, sheet_name="CFOPS")


def to_bool(x):
    if pd.isna(x):
        return None
    if isinstance(x, (int, float)):
        return bool(int(x))

if "st" in df_ncms.columns:
    df_ncms["st"] = df_ncms["st"].map(to_bool)

def norm_cst(v):
    if pd.isna(v):
        return None
    s = str(v).strip()
    # tira “.0”, espaços e qualquer coisa não-numérica
    s = "".join(ch for ch in s if ch.isdigit())
    if s == "":
        return None
    # garante sempre 3 dígitos: 0 -> 000, 60 -> 060
    return s.zfill(3)

if "cst" in df_ncms.columns:
    df_ncms["cst"] = df_ncms["cst"].apply(norm_cst)

to_sql_mode = "append"

df_ncms.to_sql(
    "mapeamento_ncms",
    engine,
    if_exists=to_sql_mode,
    index = False,
    chunksize = 1000,
    method = "multi",
    dtype = {
        "ncm": Text(),
        "aliquota": Numeric(5, 2),
        "st": Boolean(),
        "cst": Text(),
        "cest": Text(),
    }
)

df_cfops.to_sql(
    "mapeamento_cfop",
    engine,
    if_exists=to_sql_mode,
    index=False,
    chunksize=1000,
    method="multi",
    dtype={
        "cfop": Text(),
        "descricao": Text(),
        "operacao": Text(),
        "estado": Text(),
    },
)


print("Carga concluída com sucesso!")
