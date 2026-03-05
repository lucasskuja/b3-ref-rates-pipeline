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
    dag_id="b3_taxas_backfill",
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False
) as dag:

    run_backfill = PythonOperator(
        task_id="run_backfill",
        python_callable=pipeline,
        op_kwargs={"data_referencia": "{{ dag_run.conf['data_referencia'] }}"}
    )