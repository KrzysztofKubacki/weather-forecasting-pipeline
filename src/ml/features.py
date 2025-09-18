# src/ml/features.py
from sqlalchemy import create_engine
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DB_URL"), future=True)

def build_dataset(horizon_h: int = 3) -> pd.DataFrame:
    sql = f"""
    WITH curr AS (
      SELECT city_id, ts_utc,
             temp_c, humidity_pct, pressure_hpa, wind_speed_ms, clouds_pct
      FROM weather_current
    )
    SELECT
      c.city_id,
      c.ts_utc,
      c.temp_c,
      c.humidity_pct,
      c.pressure_hpa,
      c.wind_speed_ms,
      c.clouds_pct,
      f.target_temp AS target_temp_plus_h
    FROM curr c
    JOIN LATERAL (
        SELECT wf.temp_c AS target_temp
        FROM weather_forecast wf
        WHERE wf.city_id = c.city_id
        ORDER BY ABS(EXTRACT(EPOCH FROM (
            wf.ts_forecast_utc - (c.ts_utc + INTERVAL '{horizon_h} hours')
        )))
        LIMIT 1
    ) f ON TRUE
    ORDER BY c.city_id, c.ts_utc;
    """
    df = pd.read_sql(sql, engine)
    df.dropna(inplace=True)
    return df
