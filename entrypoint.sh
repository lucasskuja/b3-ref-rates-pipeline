#!/bin/bash
set -e

# Gera Fernet key automaticamente se não estiver definida
if [ -z "$AIRFLOW__CORE__FERNET_KEY" ]; then
  export AIRFLOW__CORE__FERNET_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
  echo "Fernet key gerada automaticamente: $AIRFLOW__CORE__FERNET_KEY"
fi

# Executa o entrypoint original do Airflow
exec /entrypoint "$@"
