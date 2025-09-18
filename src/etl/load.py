import pandas as pd
from sqlalchemy import text
from ..db import get_engine

def upsert_dataframe(df: pd.DataFrame, table: str, conflict_cols: list):
    if df is None or df.empty:
        return
    engine = get_engine()
    with engine.begin() as con:
        tmp = "_stg_" + table
        df.to_sql(tmp, con, if_exists="replace", index=False)
        cols = ", ".join(df.columns)
        conflict = ", ".join(conflict_cols)
        updates = ", ".join([f"{c}=EXCLUDED.{c}" for c in df.columns if c not in conflict_cols])
        con.execute(text(f"""
            INSERT INTO {table} ({cols})
            SELECT {cols} FROM {tmp}
            ON CONFLICT ({conflict}) DO UPDATE SET {updates};
        """))
        con.execute(text(f"DROP TABLE {tmp};"))
