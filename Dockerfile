FROM apache/airflow:2.9.0

# Instala dependências extras
USER airflow
RUN pip install --no-cache-dir \
    requests==2.31.0 \
    boto3==1.34.34

# Script de entrypoint para gerar Fernet key se não existir
USER root
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER airflow

# Copia DAGs e scripts para dentro do container
COPY dags/ /opt/airflow/dags/
COPY scripts/ /opt/airflow/scripts/
COPY requirements.txt /requirements.txt

ENTRYPOINT ["/entrypoint.sh"]
