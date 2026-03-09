## Guia de Deployment: b3_taxas_report com Docker Compose

### Pré-requisitos

- Docker >= 20.10
- Docker Compose >= 1.29
- OpenAI API Key (obter em https://platform.openai.com/api-keys)
- Email corporativo ou conta Gmail configurada

## 1. Configurar Variáveis de Ambiente

### Criar arquivo `.env`

```bash
cp ./examples/env.example .env
```

Editar `.env` com suas credenciais:

```env
# ===== OPENAI / LLM =====
OPENAI_API_KEY=sk-...sua-chave-aqui...

# ===== EMAIL =====
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=seu-email@gmail.com
SENDER_PASSWORD=abcd efgh ijkl mnop  # Senha de app do Gmail

# Lista de emails destinatários (separados por vírgula)
EMAIL_RECIPIENTS=credit-anal@empresa.com.br,manager@empresa.com.br

# ===== DATABASE =====
DB_CONNECTION_STRING=postgresql://airflow:airflow@postgres:5432/b3_taxas
```

### ⚠️ Configurar credenciais Gmail (recomendado)

1. Acesse: https://myaccount.google.com/apppasswords
2. Gere uma "Senha de app" para Gmail
3. Copie para `SENDER_PASSWORD`

**Exemplo:**
```
Gmail password: meu_password_123
App password: abcd efgh ijkl mnop  ← Use isto
```

## 2. Atualizar docker-compose.yml

Adicione as variáveis de ambiente ao serviço Airflow:

```yaml
services:
  airflow-webserver:
    environment:
      # ... variáveis existentes ...
      
      # Novas para LLM Reports
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      SMTP_SERVER: ${SMTP_SERVER}
      SMTP_PORT: ${SMTP_PORT}
      SENDER_EMAIL: ${SENDER_EMAIL}
      SENDER_PASSWORD: ${SENDER_PASSWORD}
      EMAIL_RECIPIENTS: ${EMAIL_RECIPIENTS}
      DB_CONNECTION_STRING: ${DB_CONNECTION_STRING}
  
  airflow-scheduler:
    environment:
      # ... mesmas variáveis ...
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      SMTP_SERVER: ${SMTP_SERVER}
      SMTP_PORT: ${SMTP_PORT}
      SENDER_EMAIL: ${SENDER_EMAIL}
      SENDER_PASSWORD: ${SENDER_PASSWORD}
      EMAIL_RECIPIENTS: ${EMAIL_RECIPIENTS}
      DB_CONNECTION_STRING: ${DB_CONNECTION_STRING}
```

## 3. Verificar Dockerfile

O Dockerfile deve incluir as dependências Python. Verifique:

```dockerfile
FROM apache/airflow:2.9.0-python3.9

# Instalar dependências de sistema (se necessário)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean

# Copiar requirements
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

# Copiar DAGs e scripts
COPY dags /opt/airflow/dags
COPY scripts /home/airflow/scripts
```

## 4. Build e Inicialização

### Build da imagem
```bash
docker compose build
```

### Inicializar Airflow
```bash
docker compose up airflow-init
```

### Subir os serviços
```bash
docker compose up -d
```

### Verificar status
```bash
docker compose ps
```

Esperado:
```
NAME                  STATUS
airflow-postgres      Up
airflow-redis         Up
airflow-webserver     Up
airflow-scheduler     Up
```

## 5. Acessar Airflow Web UI

1. Abra: http://localhost:8080
2. Login: `airflow` / `airflow`
3. Procure pela DAG `b3_taxas_report`
4. Clique no toggle para ativar

## 6. Validar Configuração

### Teste 1: Verificar variáveis
```bash
# Entrar no container do scheduler
docker compose exec airflow-scheduler bash

# Dentro do container
echo $OPENAI_API_KEY
echo $SMTP_SERVER
echo $SENDER_EMAIL
```

### Teste 2: Testar conexão com banco
```bash
# Dentro do container
python -c "
from sqlalchemy import create_engine
engine = create_engine(os.environ['DB_CONNECTION_STRING'])
print('✅ Conexão OK' if engine.execute('SELECT 1').scalar() else '❌ Erro')
"
```

### Teste 3: Testar API OpenAI
```bash
# Dentro do container
python -c "
import openai
openai.api_key = os.environ['OPENAI_API_KEY']
print('✅ OpenAI OK' if openai.Model.list() else '❌ Erro')
"
```

### Teste 4: Testar SMTP
```bash
# Dentro do container
python -c "
import smtplib
server = smtplib.SMTP('${SMTP_SERVER}', ${SMTP_PORT})
server.starttls()
server.login('${SENDER_EMAIL}', '${SENDER_PASSWORD}')
print('✅ SMTP OK')
server.quit()
"
```

## 7. Testes de Execução

### Teste: Gerar relatório localmente

```bash
docker compose exec airflow-webserver python -c "
from datetime import datetime
from scripts.report_generator import generate_report, save_report
import os

# Usar data atual
data_ref = datetime.now().strftime('%Y-%m-%d')

# Gerar
report = generate_report(data_ref, os.environ['DB_CONNECTION_STRING'])
print(report)

# Salvar
path = save_report(report, data_ref)
print(f'✅ Salvo em: {path}')
"
```

### Teste: Enviar email de teste

```bash
docker compose exec airflow-webserver python -c "
from scripts.email_sender import send_report_email
import os

send_report_email(
    report_content='Este é um email de teste!',
    data_referencia='2024-03-08',
    email_recipients=['seu-email@test.com'],
)
print('✅ Email enviado')
"
```

### Teste: Executar DAG manualmente

No Airflow Web UI:
1. DAGs → b3_taxas_report
2. Clique em "Trigger DAG"
3. Defina uma data
4. Monitore a execução

Or via CLI:
```bash
docker compose exec airflow-webserver \
  airflow dags test b3_taxas_report 2024-03-08
```

## 8. Monitoramento e Logs

### Ver logs em tempo real
```bash
# Logs do scheduler
docker compose logs -f airflow-scheduler

# Logs da web
docker compose logs -f airflow-webserver

# Logs de uma task específica
docker compose exec airflow-scheduler \
  airflow tasks log b3_taxas_report generate_and_send_report 2024-03-08
```

### Acessar logs via Web UI
1. DAGs → b3_taxas_report → Tree View
2. Clique em uma task
3. Abrir "Log"
