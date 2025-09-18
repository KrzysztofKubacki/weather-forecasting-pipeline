from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from pathlib import Path
from .config import DB_URL

def get_engine() -> Engine:
    return create_engine(DB_URL, future=True)

def init_schema():
    sql = Path(__file__).with_name("schemas.sql").read_text(encoding="utf-8")
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    engine = get_engine()
    with engine.begin() as con:
        for stmt in statements:
            con.execute(text(stmt + ";"))
