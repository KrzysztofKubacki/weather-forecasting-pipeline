# src/analytics/business_case.py
import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
engine = create_engine(os.getenv("DB_URL"), future=True)

OUT_DIR = "powerbi/exports"
os.makedirs(OUT_DIR, exist_ok=True)

# progi „biznesowe” – dopasuj do case’u
HEAT_ALERT = 28.0   # potencjalnie większy ruch/zużycie energii
COLD_ALERT = 0.0    # mróz -> ryzyka operacyjne

def load_data() -> pd.DataFrame:
    sql = """
    WITH preds AS (
      SELECT city_id, ts_utc, horizon_h, pred_temp_c, model_name, created_at
      FROM weather_predictions
    ),
    actuals AS (
      SELECT city_id, ts_utc, temp_c AS actual_temp_c
      FROM weather_current
    )
    SELECT
      p.city_id,
      p.ts_utc,
      p.horizon_h,
      p.pred_temp_c,
      p.model_name,
      a.actual_temp_c
    FROM preds p
    LEFT JOIN actuals a
      ON a.city_id = p.city_id
     AND a.ts_utc = p.ts_utc + (p.horizon_h || ' hours')::interval
    ORDER BY p.city_id, p.ts_utc, p.horizon_h;
    """
    df = pd.read_sql(sql, engine)
    return df

def kpi(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # Bezpieczne rzutowanie na float
    out["pred_temp_c"] = pd.to_numeric(out["pred_temp_c"], errors="coerce")
    out["actual_temp_c"] = pd.to_numeric(out["actual_temp_c"], errors="coerce")

    m_has_actual = out["actual_temp_c"].notna()

    out["abs_err"] = np.nan
    out.loc[m_has_actual, "abs_err"] = (out.loc[m_has_actual, "actual_temp_c"]
                                        - out.loc[m_has_actual, "pred_temp_c"]).abs()

    m_nonzero = m_has_actual & (out["actual_temp_c"] != 0)
    out["ape"] = np.nan
    out.loc[m_nonzero, "ape"] = out.loc[m_nonzero, "abs_err"] / out.loc[m_nonzero, "actual_temp_c"].abs()

    agg = out.groupby(["city_id", "horizon_h"], as_index=False).agg(
        n_pred=("pred_temp_c", "count"),
        n_with_actual=("actual_temp_c", "count"),
        mae=("abs_err", "mean"),
        mape=("ape", "mean"),
    )

    agg["mae"] = agg["mae"].round(2)
    agg["mape"] = (agg["mape"] * 100).round(1)  # w %
    return agg

def alerts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agregacja „alertów” biznesowych na podstawie predykcji: ile godzin upału / mrozu dziennie.
    """
    out = df.dropna(subset=["pred_temp_c"]).copy()
    out["pred_temp_c"] = pd.to_numeric(out["pred_temp_c"], errors="coerce")

    out["heat_alert"] = (out["pred_temp_c"] >= HEAT_ALERT).astype(int)
    out["cold_alert"] = (out["pred_temp_c"] <= COLD_ALERT).astype(int)

    out["date"] = pd.to_datetime(out["ts_utc"]).dt.date
    ag = out.groupby(["city_id", "date", "horizon_h"], as_index=False).agg(
        heat_hours=("heat_alert", "sum"),
        cold_hours=("cold_alert", "sum"),
        avg_pred_temp=("pred_temp_c", "mean"),
    )
    ag["avg_pred_temp"] = ag["avg_pred_temp"].round(2)
    return ag

def run():
    df = load_data()
    if df.empty:
        print("Brak danych do analizy.")
        return

    kpi_df = kpi(df)
    al_df  = alerts(df)

    kpi_df.to_csv(f"{OUT_DIR}/kpi_forecast_accuracy.csv", index=False, encoding="utf-8")
    al_df.to_csv(f"{OUT_DIR}/alerts_by_day.csv", index=False, encoding="utf-8")
    df.to_csv(f"{OUT_DIR}/pred_vs_actual_detailed.csv", index=False, encoding="utf-8")

    print("Zapisano:")
    print(" - powerbi/exports/kpi_forecast_accuracy.csv   (MAE/MAPE per miasto i horyzont; tylko tam, gdzie są 'actuals')")
    print(" - powerbi/exports/alerts_by_day.csv           (liczba godzin upału/mrozu dziennie per miasto/horyzont)")
    print(" - powerbi/exports/pred_vs_actual_detailed.csv (pełna tabela predykcji + ewentualne actuals)")
    print(f"Progi alertów: HEAT≥{HEAT_ALERT}°C, COLD≤{COLD_ALERT}°C")
    print("Uwaga: KPI będą się uzupełniać dopiero, gdy pojawią się rzeczywiste wartości dla ts_utc + horyzont.")
    
if __name__ == "__main__":
    run()
