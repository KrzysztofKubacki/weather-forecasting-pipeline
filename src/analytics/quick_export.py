import os, pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
engine = create_engine(os.getenv("DB_URL"), future=True)

sql_detailed = """
SELECT 'current' AS source, c.name AS city, c.country, wc.ts_utc AS ts,
       wc.temp_c, wc.feels_like_c, wc.humidity_pct, wc.pressure_hpa,
       wc.wind_speed_ms, wc.wind_deg, wc.clouds_pct, wc.weather_main, wc.weather_desc
FROM weather_current wc
JOIN cities c USING(city_id)
UNION ALL
SELECT 'forecast', c.name, c.country, wf.ts_forecast_utc,
       wf.temp_c, wf.temp_min_c, wf.temp_max_c, wf.humidity_pct, wf.pressure_hpa,
       wf.wind_speed_ms, wf.wind_deg, wf.clouds_pct, wf.weather_main, wf.weather_desc
FROM weather_forecast wf
JOIN cities c USING(city_id)
ORDER BY ts;
"""
pd.read_sql(sql_detailed, engine).to_csv("export_weather_detailed.csv", index=False)
print("export_weather_detailed.csv")

sql_daily = """
SELECT c.name AS city, DATE(wf.ts_forecast_utc) AS day,
       ROUND(AVG(wf.temp_c)::numeric,2) AS avg_temp,
       ROUND(MIN(wf.temp_c)::numeric,2) AS min_temp,
       ROUND(MAX(wf.temp_c)::numeric,2) AS max_temp,
       ROUND(AVG(wf.humidity_pct)::numeric,2) AS avg_humidity
FROM weather_forecast wf
JOIN cities c USING(city_id)
GROUP BY c.name, DATE(wf.ts_forecast_utc)
ORDER BY day;
"""
pd.read_sql(sql_daily, engine).to_excel("export_weather_daily.xlsx", index=False)
print("export_weather_daily.xlsx")

sql_wind = """
SELECT c.name AS city, wf.ts_forecast_utc AS ts, wf.wind_speed_ms, wf.wind_deg
FROM weather_forecast wf
JOIN cities c USING(city_id)
ORDER BY wf.wind_speed_ms DESC
LIMIT 10;
"""
pd.read_sql(sql_wind, engine).to_csv("export_weather_wind.csv", index=False)
print("export_weather_wind.csv")

sql_pred = """
SELECT c.name AS city, p.ts_utc AS ts_base, p.horizon_h, p.pred_temp_c, p.model_name, p.created_at
FROM weather_predictions p
JOIN cities c USING(city_id)
ORDER BY p.created_at DESC, c.name;
"""
pd.read_sql(sql_pred, engine).to_csv("export_weather_predictions.csv", index=False)
print("export_weather_predictions.csv")

print("Wszystkie eksporty zapisane w folderze projektu.")
