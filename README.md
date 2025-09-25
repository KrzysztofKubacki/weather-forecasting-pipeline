# Weather Forecasting Pipeline (ETL + SQL + ML + Analytics)

---

## Project Description

This project demonstrates a complete **Data Engineering + Data Science pipeline** using free weather data.  
The goal is to forecast temperature in selected cities for a horizon of **+3h** and **+6h**, followed by business analysis (weather alerts, model quality KPIs).  

The project combines:  
- **ETL** – retrieving data from the OpenWeather API and storing it in a PostgreSQL database,  
- **SQL** – data model and prediction handling,  
- **Python + ML** – training XGBoost models, generating forecasts,  
- **Analytics** – comparing forecasts with actuals, exporting CSVs to Power BI.  

---

## Architecture

OpenWeather API → ETL (Python) → PostgreSQL  
↓  
Features (SQL + Pandas)  
↓  
ML (XGBoost +3h, +6h models)  
↓  
Predictions → weather_predictions  
↓  
Business analytics (KPI, Alerts) → CSV → Power BI  

---

## Tech Stack

- **Python 3.10+**  
  - `pandas`, `numpy`, `sqlalchemy`, `python-dotenv`  
  - `xgboost`, `scikit-learn`, `joblib`  
- **PostgreSQL + pgAdmin**  
- **Power BI / Excel** (visualizations)  
- **Windows Task Scheduler** (ETL automation)  

---

## Project Structure
```bash
src/
├── etl/
│   └── run_etl.py          # fetches data from OpenWeather and stores it in DB
├── ml/
│   ├── features.py         # builds dataset for ML
│   ├── train_model.py      # +3h model
│   ├── train_model_6h.py   # +6h model
│   └── predict.py          # saves forecasts (+3h, +6h)
└── analytics/
    └── business_case.py    # KPIs, alerts, CSV export

```


## How to Run
### 1. Clone repository and install dependencies
```bash
conda create -n weather python=3.10
conda activate weather
pip install -r requirements.txt

```

### 2. Set environment variables in .env
```ini
DB_URL=postgresql+psycopg2://postgres:password@localhost:5432/weather

API_KEY=your_api_key_openweather
```
---

### 3. Load data into the database
```bash
python -m src.etl.run_etl
```
--- 

### 4. Train models
```bash
python -m src.ml.train_model       # model +3h
python -m src.ml.train_model_6h    # model +6h
```
---

### 5. Generate forecasts
```bash
python -m src.ml.predict
```
---
### 6. Business analytics and CSV export
```bash
python -m src.analytics.business_case
```
Output files in:

```bash
powerbi/exports/
 ├── kpi_forecast_accuracy.csv
 ├── alerts_by_day.csv
 └── pred_vs_actual_detailed.csv
 ```

---

 ### KPI Metrics
- File kpi_forecast_accuracy.csv includes:
- number of forecasts (n_pred),
- forecasts with actual values (n_with_actual),
- MAE (Mean Absolute Error),
- MAPE (Mean Absolute Percentage Error).

---

 ### Business Alerts
- File alerts_by_day.csv aggregates extreme conditions:
- heat_hours – forecasted hours with temp ≥ 28°C,
- cold_hours – forecasted hours with temp ≤ 0°C.

---

### Automation
ETL is scheduled in Windows Task Scheduler every 10 minutes.
Predictions and analytics can be run manually or added as additional scheduled jobs.

This makes the pipeline operate similarly to a real production environment.

---

 ### Business Value
- Retail/E-commerce &rarr; plan store capacity on hot/cold days.
- Energy sector &rarr; estimate heating/AC demand.
- Logistics &rarr; early alerts on frost/heat risks.
 
The project demonstrates a full Data Engineering + Data Science cycle with elements of MLOps and Business Intelligence.

---

 ### Author
Project created as a portfolio / CV project by Krzysztof Kubacki
