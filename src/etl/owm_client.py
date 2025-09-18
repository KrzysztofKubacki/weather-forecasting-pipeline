import requests
from typing import Dict, Any
from ..config import OWM_API_KEY, DEFAULT_UNITS, DEFAULT_LANG

BASE = "https://api.openweathermap.org/data/2.5"

def _params(lat: float, lon: float):
    return {
        "lat": lat,
        "lon": lon,
        "appid": OWM_API_KEY,
        "units": DEFAULT_UNITS,
        "lang": DEFAULT_LANG
    }

def fetch_current(lat: float, lon: float) -> Dict[str, Any]:
    r = requests.get(f"{BASE}/weather", params=_params(lat, lon), timeout=20)
    r.raise_for_status()
    return r.json()

def fetch_forecast(lat: float, lon: float) -> Dict[str, Any]:
    r = requests.get(f"{BASE}/forecast", params=_params(lat, lon), timeout=20)
    r.raise_for_status()
    return r.json()
