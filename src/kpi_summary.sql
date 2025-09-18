WITH daily AS (
  SELECT ts_utc::date AS day, city_id,
         COUNT(*) FILTER (WHERE temp_c > 30) AS hot_hours
  FROM weather_current
  GROUP BY day, city_id
)
SELECT city_id,
       COUNT(*) FILTER (WHERE hot_hours >= 3) AS hot_days
FROM daily
GROUP BY city_id
ORDER BY hot_days DESC;

WITH last7 AS (
  SELECT * FROM weather_current
  WHERE ts_utc >= NOW() - INTERVAL '7 days'
)
SELECT city_id,
       ROUND(AVG(temp_c)::numeric,2) AS avg_temp_7d
FROM last7
GROUP BY city_id
ORDER BY avg_temp_7d DESC;
