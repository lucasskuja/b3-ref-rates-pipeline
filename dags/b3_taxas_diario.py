from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from scripts.extract import download_taxas
from scripts.transform import normalize_taxas
from scripts.load import upsert_taxas

def pipeline(data_referencia, **context):
    raw_path = download_taxas(data_referencia, "/tmp")
    df = normalize_taxas(raw_path, data_referencia)
    upsert_taxas(df, "postgresql://user:pass@host/db")

with DAG(
    dag_id="b3_taxas_diario",
    schedule_interval="0 20 * * 1-5",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["b3", "taxas"]
) as dag:

    run_pipeline = PythonOperator(
        task_id="run_pipeline",
        python_callable=pipeline,
        op_kwargs={"data_referencia": "{{ ds }}"}
    )