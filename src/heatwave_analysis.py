import os
import pandas as pd
import matplotlib.pyplot as plt
from src.db import get_engine

os.makedirs("powerbi", exist_ok=True)

engine = get_engine()
query = """
SELECT 
    ts_utc::date AS day,
    city_id,
    COUNT(*) FILTER (WHERE temp_c > 30) AS hot_hours,
    ROUND(AVG(temp_c)::numeric, 2) AS avg_temp
FROM weather_current
GROUP BY day, city_id
ORDER BY day, city_id;
"""
df = pd.read_sql(query, engine)

df.to_csv("powerbi/heatwave_daily_city.csv", index=False)

plt.figure(figsize=(10,5))
for cid, g in df.groupby("city_id"):
    plt.plot(g["day"], g["avg_temp"], marker="o", label=f"city_id {cid}")
plt.axhline(30, linestyle="--", label="próg upału 30°C")
plt.title("Średnia temperatura dzienna – wykrywanie dni upalnych")
plt.xlabel("Dzień")
plt.ylabel("Śr. temp [°C]")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("powerbi/heatwave_trend.png", dpi=150)
print("Zapisano: powerbi/heatwave_daily_city.csv i powerbi/heatwave_trend.png")
