# Weather Forecasting Pipeline (ETL + SQL + ML + Analytics)

## Opis projektu
Projekt demonstruje kompletny pipeline **Data Engineering + Data Science** na darmowych danych pogodowych.  
Celem jest przewidywanie temperatury w wybranych miastach na horyzoncie **+3h** i **+6h**, a następnie analiza biznesowa (alerty pogodowe, KPI jakości modelu).  

Projekt łączy:
- **ETL** – pobieranie danych z API OpenWeather i zapis do bazy PostgreSQL,
- **SQL** – model danych i obsługa predykcji,
- **Python + ML** – trenowanie modeli XGBoost, generowanie prognoz,
- **Analytics** – porównanie prognoz z rzeczywistością, eksport CSV do Power BI.

---

## Architektura

OpenWeather API → ETL (Python) → PostgreSQL
↓
Features (SQL + Pandas)
↓
ML (XGBoost +3h, +6h models)
↓
Predictions → weather_predictions
↓
Business analytics (KPI, Alerts) → CSV → Power BI


## Stack technologiczny
- **Python 3.10+**
  - `pandas`, `numpy`, `sqlalchemy`, `python-dotenv`
  - `xgboost`, `scikit-learn`, `joblib`
- **PostgreSQL + pgAdmin**
- **Power BI / Excel** (wizualizacje)
- **Windows Task Scheduler** (automatyzacja ETL)

---

## Struktura projektu
```bash
src/
├── etl/
│   └── run_etl.py          # pobieranie danych z OpenWeather i zapis do DB
├── ml/
│   ├── features.py         # budowa datasetu dla ML
│   ├── train_model.py      # model +3h
│   ├── train_model_6h.py   # model +6h
│   └── predict.py          # zapis prognoz (+3h, +6h)
└── analytics/
    └── business_case.py    # KPI, alerty, eksport CSV
```


## Instrukcja uruchomienia

### 1. Klon repozytorium i instalacja zależności
```bash
conda create -n weather python=3.10
conda activate weather
pip install -r requirements.txt

```

### 2. Ustaw zmienne środowiskowe w .env
```ini
DB_URL=postgresql+psycopg2://postgres:haslo@localhost:5432/weather

API_KEY=twoj_klucz_openweather
```
---

### 3. Pobierz dane do bazy
```bash
python -m src.etl.run_etl
```
--- 

### 4. Wytrenuj modele
```bash
python -m src.ml.train_model       # model +3h
python -m src.ml.train_model_6h    # model +6h
```
---

### 5. Wygeneruj prognozy
```bash
python -m src.ml.predict
```
---
### 6. Analiza biznesowa i eksport CSV
```bash
python -m src.analytics.business_case
```
Pliki CSV znajdziesz w:

```bash
powerbi/exports/
 ├── kpi_forecast_accuracy.csv
 ├── alerts_by_day.csv
 └── pred_vs_actual_detailed.csv
 ```
 ### KPI modelu
Plik kpi_forecast_accuracy.csv zawiera m.in.:

liczba prognoz (n_pred),

liczba prognoz z rzeczywistymi wartościami (n_with_actual),

MAE (średni błąd absolutny),

MAPE (średni błąd procentowy).

---

 ### Alerty biznesowe
Plik alerts_by_day.csv – agregacja godzin upału/mrozu:

heat_hours – ile godzin prognozowanych z temp ≥ 28°C,

cold_hours – ile godzin prognozowanych z temp ≤ 0°C.

---

 ### Automatyzacja
ETL skonfigurowano w Windows Task Scheduler co 10 minut.

Predykcje i analizy można odpalać ręcznie lub dodać jako kolejne zadania.

Dzięki temu pipeline działa jak w realnym środowisku produkcyjnym.

---

 ### Wartość biznesowa
Retail/E-commerce → planowanie obłożenia sklepów w dni upalne/zimne.

Energetyka → szacunek zapotrzebowania na ogrzewanie/klimatyzację.

Logistyka → wczesne ostrzeżenie o ryzyku mrozu / upałów.

Projekt pokazuje pełny cykl Data Engineering + Data Science z elementami MLOps i Business Intelligence.

---

 Autor
Projekt stworzony jako portfolio / CV project przez [Twoje Imię].