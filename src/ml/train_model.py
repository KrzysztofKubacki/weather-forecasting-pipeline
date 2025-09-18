# src/ml/train_model.py
import os
import json
import math
import joblib
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import TimeSeriesSplit
from xgboost import XGBRegressor
from .features import build_dataset

load_dotenv()
ENGINE = create_engine(os.getenv("DB_URL"), future=True)

MODEL_PATH = "model_xgb_temp_3h.joblib"
METRICS_PATH = "metrics_xgb_temp_3h.json"
MODEL_NAME = "xgb_temp_3h_v1"
HORIZON_H = 3


def _add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ts_utc"] = pd.to_datetime(out["ts_utc"])
    out["hour"] = out["ts_utc"].dt.hour.astype(int)
    out["dow"] = out["ts_utc"].dt.dayofweek.astype(int)
    out["hour_sin"] = np.sin(2 * np.pi * out["hour"] / 24)
    out["hour_cos"] = np.cos(2 * np.pi * out["hour"] / 24)
    out["dow_sin"] = np.sin(2 * np.pi * out["dow"] / 7)
    out["dow_cos"] = np.cos(2 * np.pi * out["dow"] / 7)
    return out


def _chronological_split(df: pd.DataFrame, test_size: float = 0.2):
    n = len(df)
    n_test = max(1, int(math.floor(n * test_size)))
    n_train = n - n_test
    return df.iloc[:n_train], df.iloc[n_train:]


def train():
    df = build_dataset(horizon_h=HORIZON_H)
    if df.empty or len(df) < 100:
        print("Za mało danych do sensownego treningu (min ~100 wierszy).")
        return

    df = df.sort_values(["city_id", "ts_utc"]).reset_index(drop=True)
    df = _add_time_features(df)

    FEATURES = [
        "temp_c", "humidity_pct", "pressure_hpa", "wind_speed_ms", "clouds_pct",
        "hour_sin", "hour_cos", "dow_sin", "dow_cos"
    ]
    TARGET = "target_temp_plus_h"

    X = df[FEATURES]
    y = df[TARGET]

    df_train, df_test = _chronological_split(df, test_size=0.2)
    X_train, y_train = df_train[FEATURES], df_train[TARGET]
    X_test, y_test = df_test[FEATURES], df_test[TARGET]

    # TimeSeries CV
    tscv = TimeSeriesSplit(n_splits=5)
    cv_maes = []
    for fold, (tr_idx, val_idx) in enumerate(tscv.split(X_train), start=1):
        X_tr, X_val = X_train.iloc[tr_idx], X_train.iloc[val_idx]
        y_tr, y_val = y_train.iloc[tr_idx], y_train.iloc[val_idx]

        model_cv = XGBRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=3,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_lambda=1.0,
            reg_alpha=0.1,
            objective="reg:squarederror",
            eval_metric="mae",
            random_state=42
        )
        model_cv.fit(X_tr, y_tr, eval_set=[(X_val, y_val)], verbose=False)
        pred_val = model_cv.predict(X_val)
        mae_val = float(mean_absolute_error(y_val, pred_val))
        cv_maes.append(mae_val)

    cv_mae_mean = float(np.mean(cv_maes))
    cv_mae_std = float(np.std(cv_maes))

    # Finalny model
    model = XGBRegressor(
        n_estimators=500,
        learning_rate=0.03,
        max_depth=3,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_lambda=1.5,
        reg_alpha=0.2,
        objective="reg:squarederror",
        eval_metric="mae",
        random_state=42
    )
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

    y_pred_test = model.predict(X_test)
    mae_test = float(mean_absolute_error(y_test, y_pred_test))

    joblib.dump(model, MODEL_PATH)
    metrics = {
        "model_name": MODEL_NAME,
        "horizon_h": HORIZON_H,
        "n_samples_total": int(len(df)),
        "n_train": int(len(df_train)),
        "n_test": int(len(df_test)),
        "features": FEATURES,
        "cv_mae_mean": cv_mae_mean,
        "cv_mae_std": cv_mae_std,
        "test_mae": mae_test,
    }
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print("✅ Wyniki:")
    print(f"   CV MAE: {cv_mae_mean:.2f} ± {cv_mae_std:.2f} °C")
    print(f"   TEST MAE: {mae_test:.2f} °C")
    print(f"💾 Model zapisany → {MODEL_PATH}")
    print(f"💾 Metryki zapisane → {METRICS_PATH}")


if __name__ == "__main__":
    train()
