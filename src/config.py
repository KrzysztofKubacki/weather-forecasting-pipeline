import os
from dotenv import load_dotenv

load_dotenv()

OWM_API_KEY = os.getenv("OWM_API_KEY")
DB_URL = os.getenv("DB_URL")
DEFAULT_UNITS = os.getenv("DEFAULT_UNITS", "metric")
DEFAULT_LANG = os.getenv("DEFAULT_LANG", "pl")

if not OWM_API_KEY:
    raise RuntimeError("Brak OWM_API_KEY w .env")
if not DB_URL:
    raise RuntimeError("Brak DB_URL w .env")
