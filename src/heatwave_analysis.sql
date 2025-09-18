SELECT 
    ts_utc::date AS day,
    city_id,
    COUNT(*) FILTER (WHERE temp_c > 30) AS hot_hours,
    ROUND(AVG(temp_c)::numeric, 2) AS avg_temp
FROM weather_current
GROUP BY day, city_id
ORDER BY day DESC, city_id;
