CREATE TABLE IF NOT EXISTS cities (
    city_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (name, country)
);

CREATE TABLE IF NOT EXISTS weather_current (
    id BIGSERIAL PRIMARY KEY,
    city_id INT REFERENCES cities(city_id),
    ts_utc TIMESTAMP NOT NULL,
    temp_c DOUBLE PRECISION,
    feels_like_c DOUBLE PRECISION,
    humidity_pct INT,
    pressure_hpa INT,
    wind_speed_ms DOUBLE PRECISION,
    wind_deg INT,
    clouds_pct INT,
    weather_main TEXT,
    weather_desc TEXT,
    UNIQUE (city_id, ts_utc)
);

CREATE TABLE IF NOT EXISTS weather_forecast (
    id BIGSERIAL PRIMARY KEY,
    city_id INT REFERENCES cities(city_id),
    ts_forecast_utc TIMESTAMP NOT NULL,
    temp_c DOUBLE PRECISION,
    temp_min_c DOUBLE PRECISION,
    temp_max_c DOUBLE PRECISION,
    humidity_pct INT,
    pressure_hpa INT,
    wind_speed_ms DOUBLE PRECISION,
    wind_deg INT,
    clouds_pct INT,
    weather_main TEXT,
    weather_desc TEXT,
    UNIQUE (city_id, ts_forecast_utc)
);

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