from datetime import datetime, timezone
from typing import Dict, Any, List

def _to_dt(ts_unix: int):
    return datetime.fromtimestamp(ts_unix, tz=timezone.utc).replace(tzinfo=None)

def normalize_current(city_id: int, j: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "city_id": city_id,
        "ts_utc": _to_dt(j["dt"]),
        "temp_c": j["main"]["temp"],
        "feels_like_c": j["main"].get("feels_like"),
        "humidity_pct": j["main"].get("humidity"),
        "pressure_hpa": j["main"].get("pressure"),
        "wind_speed_ms": j.get("wind", {}).get("speed"),
        "wind_deg": j.get("wind", {}).get("deg"),
        "clouds_pct": j.get("clouds", {}).get("all"),
        "weather_main": (j.get("weather") or [{}])[0].get("main"),
        "weather_desc": (j.get("weather") or [{}])[0].get("description"),
    }

def normalize_forecast(city_id: int, j: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for it in j.get("list", []):
        out.append({
            "city_id": city_id,
            "ts_forecast_utc": _to_dt(it["dt"]),
            "temp_c": it["main"]["temp"],
            "temp_min_c": it["main"].get("temp_min"),
            "temp_max_c": it["main"].get("temp_max"),
            "humidity_pct": it["main"].get("humidity"),
            "pressure_hpa": it["main"].get("pressure"),
            "wind_speed_ms": it.get("wind", {}).get("speed"),
            "wind_deg": it.get("wind", {}).get("deg"),
            "clouds_pct": it.get("clouds", {}).get("all"),
            "weather_main": (it.get("weather") or [{}])[0].get("main"),
            "weather_desc": (it.get("weather") or [{}])[0].get("description"),
        })
    return out
