.PHONY: setup generate-data etl dbt forecast chatbot all

setup:
	pip install -r requirements.txt

generate-data:
	python data_pipeline/generate_data.py

etl:
	python data_pipeline/etl_pipeline.py

dbt:
	cd dbt_project && dbt deps && dbt run && dbt test

forecast:
	python ml_model/demand_forecasting.py

chatbot:
	streamlit run chatbot/app.py

all: setup generate-data etl dbt forecast
