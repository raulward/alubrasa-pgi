import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

excel_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'ncms_por_desc.xlsx')
df = pd.read_excel(excel_path)

# >>> FIX AQUI: renomeia 'desc' -> 'ncm_desc'
df = df.rename(columns={'desc': 'ncm_desc', 'ncm': 'ncm_code'})

# garante formato do NCM
df['ncm_code'] = (
    df['ncm_code'].astype(str).str.extract(r'(\d+)', expand=False).str.zfill(8)
)
df = df[['ncm_code', 'ncm_desc']].dropna().drop_duplicates(subset=['ncm_code'])

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

df.to_sql(
    name='ncm_desc',
    con=engine,
    schema='ref',
    if_exists='append',   # cuidado: sem upsert; pode dar conflito se houver PK/unique
    index=False,
    method='multi',
    chunksize=1000,
)

print("Carga concluída com sucesso!")
