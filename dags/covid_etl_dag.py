"""Airflow DAG for the COVID ETL pipeline with separate extract, transform, and load data."""

from datetime import datetime, timedelta
import sys
import os
from pendulum import timezone

# Add path to data_processing/ code
sys.path.append(os.path.join(os.path.dirname(__file__), '../data_processing'))

from airflow import DAG
from airflow.operators.python import PythonOperator

# Import functions from the pipeline
from extract import run as extract_data
from transform import run as transform_data
from load import run as load_data

bogota = timezone("America/Bogota")

# General DAG Configuration
default_args = {
    'owner': '@name',
    'depends_on_past': False,
    'email': ['email@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    dag_id='covid_etl_pipeline',
    default_args=default_args,
    description='ETL pipeline for COVID-19 data with extract, transform, and load steps.',
    schedule_interval='0 8 * * *',
    start_date=datetime(2025, 6, 18,tzinfo=bogota),
    catchup=False,
    tags=['covid', 'etl', 'pipeline']
) as dag:

    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data,
        doc_md="### Extract raw COVID data from the disease.sh API"
    )

    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
        doc_md="### Cleans and transforms data to be loaded into the database"
    )

    load_task = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
        doc_md="### Inserts the transformed data into the SQLite database"
    )

    extract_task >> transform_task >> load_task
