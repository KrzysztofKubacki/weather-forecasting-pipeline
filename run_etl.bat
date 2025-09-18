@echo off
CALL %UserProfile%\anaconda3\Scripts\activate.bat weather
cd /d C:\Users\krzys\Downloads\weather-pipeline
python -m src.etl.run_etl
