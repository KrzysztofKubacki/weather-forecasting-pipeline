# src/ml/predict.py
import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.getenv("DB_URL"), future=True)

LAST_PER_CITY = 12

FEATURES = [
    "temp_c", "humidity_pct", "pressure_hpa", "wind_speed_ms", "clouds_pct",
    "hour_sin", "hour_cos", "dow_sin", "dow_cos"
]

HORIZONS_H = [3, 6]

def fetch_recent_features(last_per_city: int = LAST_PER_CITY) -> pd.DataFrame:
    sql = f"""
    WITH ranked AS (
      SELECT
        city_id, ts_utc,
        temp_c, humidity_pct, pressure_hpa, wind_speed_ms, clouds_pct,
        ROW_NUMBER() OVER (PARTITION BY city_id ORDER BY ts_utc DESC) AS rn
      FROM weather_current
    )
    SELECT
      city_id, ts_utc,
      temp_c, humidity_pct, pressure_hpa, wind_speed_ms, clouds_pct
    FROM ranked
    WHERE rn <= {last_per_city}
    ORDER BY city_id, ts_utc DESC;
    """
    df = pd.read_sql(sql, engine)
    if df.empty:
        return df

    df["ts_utc"] = pd.to_datetime(df["ts_utc"])
    df["hour"] = df["ts_utc"].dt.hour.astype(int)
    df["dow"]  = df["ts_utc"].dt.dayofweek.astype(int)
    df["hour_sin"] = np.sin(2*np.pi*df["hour"]/24)
    df["hour_cos"] = np.cos(2*np.pi*df["hour"]/24)
    df["dow_sin"]  = np.sin(2*np.pi*df["dow"]/7)
    df["dow_cos"]  = np.cos(2*np.pi*df["dow"]/7)
    return df

def upsert_predictions(df_feats: pd.DataFrame, preds: np.ndarray, horizon_h: int, model_name: str):
    out = df_feats[["city_id", "ts_utc"]].copy()
    out["horizon_h"]   = horizon_h
    out["pred_temp_c"] = preds
    out["model_name"]  = model_name
    out["created_at"]  = datetime.utcnow()

    with engine.begin() as con:
        out.to_sql("_stg_weather_predictions", con, if_exists="replace", index=False)
        con.execute(text("""
            CREATE TABLE IF NOT EXISTS weather_predictions (
              id BIGSERIAL PRIMARY KEY,
              city_id INT REFERENCES cities(city_id),
              ts_utc TIMESTAMP NOT NULL,
              horizon_h SMALLINT NOT NULL,
              pred_temp_c DOUBLE PRECISION,
              model_name TEXT,
              created_at TIMESTAMP NOT NULL DEFAULT NOW(),
              UNIQUE (city_id, ts_utc, horizon_h, model_name)
            );
        """))
        con.execute(text("""
            INSERT INTO weather_predictions
              (city_id, ts_utc, horizon_h, pred_temp_c, model_name, created_at)
            SELECT city_id, ts_utc, horizon_h, pred_temp_c, model_name, created_at
            FROM _stg_weather_predictions
            ON CONFLICT (city_id, ts_utc, horizon_h, model_name)
            DO UPDATE SET pred_temp_c = EXCLUDED.pred_temp_c,
                          created_at  = EXCLUDED.created_at;
        """))
        con.execute(text("DROP TABLE _stg_weather_predictions;"))

def run():
    feats = fetch_recent_features(LAST_PER_CITY)
    if feats.empty:
        print("Brak danych w weather_current.")
        return

    X = feats[FEATURES].copy()

    total_saved = 0
    for H in HORIZONS_H:
        model_path = f"model_xgb_temp_{H}h.joblib"
        model_name = f"xgb_temp_{H}h_v1"

        if not os.path.exists(model_path):
            print(f"Brak modelu dla +{H}h ({model_path}). Ten horyzont zostaje pominięty.")
            continue

        model = joblib.load(model_path)
        preds = model.predict(X)
        upsert_predictions(feats, preds, H, model_name)
        print(f"Zapisano {len(preds)} predykcji dla horyzontu +{H}h.")
        total_saved += len(preds)

    if total_saved == 0:
        print("Nie zapisano żadnych predykcji (brak dostępnych modeli).")
    else:
        print(f"Razem zapisano: {total_saved} predykcji (horyzonty: {HORIZONS_H}).")

if __name__ == "__main__":
    run()
