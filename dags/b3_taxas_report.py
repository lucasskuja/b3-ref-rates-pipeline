from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.external_task import ExternalTaskSensor
from datetime import datetime, timedelta
import os
from scripts.report_generator import generate_report, save_report
from scripts.email_sender import send_report_email, parse_email_list

# Configurações padrão
default_args = {
    "owner": "data-team",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

# Função para gerar e enviar relatório
def generate_and_send_report(**context):
    """
    Gera o relatório usando LLM e envia via email.
    """
    data_referencia = context["ds"]
    db_connection = os.getenv(
        "DB_CONNECTION_STRING",
        "postgresql://user:pass@localhost/b3_taxas"
    )
    
    # Gerar relatório
    print(f"Gerando relatório para {data_referencia}...")
    report_content = generate_report(data_referencia, db_connection)
    
    # Salvar relatório
    report_path = save_report(report_content, data_referencia)
    print(f"Relatório salvo em: {report_path}")
    
    # Enviar email
    email_recipients_str = os.getenv(
        "EMAIL_RECIPIENTS",
        "credit-team@empresa.com.br"
    )
    email_recipients = parse_email_list(email_recipients_str)
    
    print(f"Enviando relatório para: {', '.join(email_recipients)}")
    send_report_email(
        report_content=report_content,
        data_referencia=data_referencia,
        email_recipients=email_recipients
    )
    
    print(f"Relatório gerado e enviado com sucesso!")
    
    # Salvar path no contexto para referência
    context["task_instance"].xcom_push(key="report_path", value=report_path)

# Definir DAG
with DAG(
    dag_id="b3_taxas_report",
    description="Gera e envia relatório de taxas referenciais B3 via email",
    default_args=default_args,
    schedule_interval="20 20 * * 1-5",  # Executa às 20:20 seg-sex
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["b3", "taxas", "report", "email"],
) as dag:
    
    # Aguardar conclusão de b3_taxas_diario
    wait_for_extraction = ExternalTaskSensor(
        task_id="wait_for_b3_taxas_diario",
        external_dag_id="b3_taxas_diario",
        external_task_id="run_pipeline",
        poke_interval=60,  # Verificar a cada 60 segundos
        timeout=3600,  # Timeout de 1 hora
        mode="poke",  # ou "reschedule" para não ocupar slot do worker
        allowed_states=["success"],
        failed_states=["failed", "upstream_failed"],
    )
    
    # Gerar e enviar relatório
    report_task = PythonOperator(
        task_id="generate_and_send_report",
        python_callable=generate_and_send_report,
        provide_context=True,
    )
    
    # Dependência
    wait_for_extraction >> report_task
