import pandas as pd
from pathlib import Path
from sqlalchemy import text
from ..db import init_schema, get_engine
from .owm_client import fetch_current, fetch_forecast
from .transform import normalize_current, normalize_forecast
from .load import upsert_dataframe

def seed_cities_if_empty():
    engine = get_engine()
    with engine.begin() as con:
        exists = con.execute(text("SELECT COUNT(*) FROM cities")).scalar()
        if exists == 0:
            df = pd.read_csv(Path(__file__).with_name("cities_seed.csv"))
            df.to_sql("cities", con, if_exists="append", index=False)

def run():
    init_schema()
    seed_cities_if_empty()

    engine = get_engine()
    cities = pd.read_sql("SELECT city_id, lat, lon FROM cities WHERE is_active", engine)

    curr_rows, fc_rows = [], []

    for _, row in cities.iterrows():
        jcur = fetch_current(row.lat, row.lon)
        jfc  = fetch_forecast(row.lat, row.lon)

        curr_rows.append(normalize_current(row.city_id, jcur))
        fc_rows.extend(normalize_forecast(row.city_id, jfc))

    upsert_dataframe(pd.DataFrame(curr_rows), "weather_current", ["city_id", "ts_utc"])
    upsert_dataframe(pd.DataFrame(fc_rows),   "weather_forecast", ["city_id", "ts_forecast_utc"])

if __name__ == "__main__":
    run()
