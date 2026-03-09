# 📈 Pipeline de Taxas Referenciais da B3

Este repositório contém a implementação de um pipeline de **extração, transformação e carga (ETL)** das **Taxas Referenciais da B3**, utilizando **Apache Airflow** para orquestração e **Postgres/S3** como camadas de armazenamento.

## ✅ Requisitos do Projeto

Antes de rodar o pipeline, certifique-se de ter:

- **Docker** >= 20.10  
- **docker-compose** >= 1.29  
- **Python** >= 3.9 (para testes locais sem Docker)  
- **Postgres** configurado (se não usar o container interno)  
- **AWS CLI** configurado (para acesso ao S3, se aplicável)  
- **Chave Fernet** para criptografia interna do Airflow  

## 🚀 Visão Geral

O pipeline foi projetado para:

- Extrair diariamente as taxas referenciais publicadas pela B3.
- Normalizar e transformar os dados em formato analítico.
- Persistir em camadas **Bronze (Raw)**, **Silver (Normalizado)** e **Gold (Histórico consolidado)**.
- Disponibilizar dados para consumo por times de crédito e análises financeiras.

## 📂 Estrutura do Projeto

```
b3-ref-rates-pipeline/
│
├── dags/                       # DAGs do Airflow
├── scripts/                    # Scripts de ETL
├── docs/                       # Documentação técnica
├── tests/                      # Testes unitários
├── requirements.txt            # Dependências
├── entrypoint.sh               # Script para gerar Fernet key
├── Dockerfile                  # Imagem customizada do Airflow
├── docker-compose.yml          # Orquestração dos serviços
├── Makefile                    # Comandos simplificados
├── README.md                   # Este arquivo
└── .gitignore
```

## ⚙️ Tecnologias Utilizadas

- **Apache Airflow** → Orquestração dos DAGs
- **Python (requests, pandas, sqlalchemy)** → Scripts de ETL
- **Postgres/Athena** → Camada Gold
- **AWS S3** → Armazenamento bruto (Bronze)
- **Slack** → Alertas e monitoramento
- **Docker + docker-compose** → Containerização
- **LangChain + OpenAI** → Geração de relatórios com IA e análise de dados
- **SMTP** → Envio de emails

## 📑 Modelagem de Dados

- **Bronze** → `curva_referencial_raw`  
  Armazena os arquivos originais da B3.

- **Silver** → `curva_referencial_diaria`  
  Normalização: 1 linha por vencimento, tipo de curva e data.

- **Gold** → `curva_referencial_historica`  
  Tabela consolidada para consumo analítico.  
  Chave primária: `(data_referencia, tipo_curva, vencimento)`.

## 📅 DAGs

- **`b3_taxas_diario`**  
  Executa diariamente em dias úteis às 20h.  
  Responsável por extrair, transformar e carregar as taxas referenciais.

- **`b3_taxas_report`**
  Executa às 20:20 (logo após `b3_taxas_diario` completar).  
  Gera relatórios executivos com análise de LLM e envia via email para grupos de crédito.
  - Aguarda conclusão de `b3_taxas_diario` via `ExternalTaskSensor`
  - Analisa dados usando OpenAI GPT
  - Envia relatório formatado (HTML + texto) via SMTP

- **`b3_taxas_backfill`**  
  Permite reprocessar períodos históricos (até 10 anos).

## 🛠️ Instalação e Uso

Para começar a trabalhar com este projeto, o primeiro passo é clonar o repositório:

```bash
git clone https://github.com/lucasskuja/b3-ref-rates-pipeline
cd b3-ref-rates-pipeline
```
<details>
<summary>📍 Modo local</summary>

### 1. Criando uma virtualenv
```bash
python3.9 -m venv venv
source venv/Scripts/activate
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar Airflow
O Airflow precisa ser inicializado e configurado antes de rodar os DAGs:

#### 🔧 Inicializar banco de metadados
```bash
airflow db init
```

#### 👤 Criar usuário administrador
```bash
airflow users create \
  --username airflow \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password airflow
```
#### ▶️ Iniciar serviços
Em dois terminais diferentes:
```bash
airflow scheduler
```

```bash
airflow webserver -p 8080
```
</details>

<details>
<summary>🐳 Dockerização</summary>

### 1. Build das imagens

```bash
docker compose build
```

### 2. Inicializar o Airflow (cria banco e usuário)

```bash
docker compose up airflow-init
```

### 3. Subir os serviços

```bash
docker compose up -d
```

</details>

<details>
<summary> 📂 Makefile – Comandos de Uso</summary>

### 1. Construir as imagens Docker

```bash
make build
```
### 2. Subir os serviços

```bash
make init
```

### 3. Subir os serviços do pipeline

```bash
make up
```
</details>

### 👉 Acesse o painel em:  
Airflow Web UI: `http://localhost:8080`  
Usuário: `airflow`  
Senha: `airflow`

### 🔗 Configurar conexões
No Airflow Web UI:
- Vá em **Admin → Connections** e crie:
  - **Postgres**  
    - Conn Id: `postgres_default`  
    - Conn Type: `Postgres`  
    - Host: `localhost`  
    - Schema: nome do banco  
    - Login: usuário  
    - Password: senha  
    - Port: `5432`
  - **S3/AWS**  
    - Conn Id: `aws_default`  
    - Conn Type: `Amazon Web Services`  
    - Access Key ID e Secret Access Key configurados.

### ⚙️ Configurar variáveis
Em **Admin → Variables**, adicione:
- `S3_BUCKET` → nome do bucket para camada Bronze.  
- `SLACK_WEBHOOK` → URL do webhook para alertas.  
- `DB_SCHEMA` → schema do Postgres para camada Gold.  

### 🤖 Configurar DAG de Relatórios com LLM (b3_taxas_report)

Para utilizar a nova DAG de geração de relatórios com análise de LLM, siga os passos:

#### 1️⃣ Instalar dependências adicionais

As dependências necessárias já estão em `requirements.txt`:
- `langchain` → Framework para integração com LLMs
- `openai` → API OpenAI para análise de taxas
- `python-dotenv` → Gerenciar variáveis de ambiente

#### 2️⃣ Configurar variáveis de ambiente

Copie o arquivo de exemplo e configure:

```bash
cp .env.example .env
```

Edite `.env` com suas credenciais:

```env
# OpenAI API Key (obter em https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-your-api-key-here

# Configuração SMTP para envio de email
SMTP_SERVER=smtp.gmail.com        # Usar Gmail ou seu servidor SMTP
SMTP_PORT=587
SENDER_EMAIL=seu-email@gmail.com
SENDER_PASSWORD=sua-senha-de-app  # Para Gmail, use "senha de app"

# Lista de destinatários (separados por vírgula)
EMAIL_RECIPIENTS=credit-team@empresa.com.br,manager@empresa.com.br

# Banco de dados
DB_CONNECTION_STRING=postgresql://user:password@localhost:5432/b3_taxas
```

**Dica para Gmail**: Se usar Gmail, gere uma [senha de aplicativo](https://myaccount.google.com/apppasswords) em vez de sua senha normal.

#### 3️⃣ Configurar no Airflow (Docker)

Se usar Docker, adicione as variáveis no `docker-compose.yml`:

```yaml
environment:
  OPENAI_API_KEY: sk-your-api-key
  SMTP_SERVER: smtp.gmail.com
  SMTP_PORT: 587
  SENDER_EMAIL: seu-email@gmail.com
  SENDER_PASSWORD: sua-senha
  EMAIL_RECIPIENTS: credit-team@empresa.com.br
  DB_CONNECTION_STRING: postgresql://user:pass@postgres:5432/b3_taxas
```

#### 4️⃣ Ativar a DAG

No Airflow Web UI:
1. Vá para a lista de DAGs
2. Procure por `b3_taxas_report`
3. Clique no toggle para ativar
4. A DAG será executada automaticamente às 20:20 em dias úteis

#### 5️⃣ Como funciona

1. **ExternalTaskSensor**: Aguarda que `b3_taxas_diario` complete com sucesso
2. **Geração de Relatório**: Fetch de dados do Postgres → Análise via LLM (GPT) → Geração de narrativa executiva
3. **Envio de Email**: Relatório é formatado em HTML e texto, enviado para todos os destinatários

#### 6️⃣ Exemplo de relatório gerado

O relatório inclui:
- 📊 **Análise Executiva** (gerada por IA)
- 📈 **Estatísticas** (taxa média, mínima, máxima, desvio padrão)
- 📅 **Data da referência** e horário de geração
- 🔒 **Confidencial** - Uso interno apenas

### ✅ Validar DAGs
- Verifique se os DAGs aparecem na interface.  
- Ative o DAG `b3_taxas_diario`.  
- Teste manualmente o DAG `b3_taxas_backfill` com uma data de referência.

## ⚙️ Comandos úteis 

Este projeto inclui um **Makefile** para simplificar a execução dos comandos mais comuns.  
<details>
<summary>Abaixo estão os principais comandos e como utilizá-los na prática:</summary>

- Subir containers do projeto

```bash
make up # Sobe todos os containers com build
```

- Inicializar Airflow (cria banco e usuário)

```bash
make init # Inicializa banco de metadados e cria usuário admin
```

- Derrubar containers

```bash
make down # Derruba todos os containers
```

- Derrubar containers e volumes (reset total)

```bash
make clean # Derruba containers e remove volumes (reset completo)
```

- Reiniciar containers

```bash
make restart # Derruba e sobe novamente os containers com build
```

- Rebuild da imagem Docker

```bash
make build # Rebuild da imagem Docker sem subir containers
```

- Mostrar status dos serviços

```bash
make ps # Mostra status atual dos containers
```

- Logs em tempo real

```bash
make logs # Exibe logs em tempo real de todos os serviços
```

- Logs apenas do scheduler

```bash
make logs-scheduler # Exibe logs em tempo real do scheduler
```

- Logs apenas do webserver

```bash
make logs-webserver # Exibe logs em tempo real do webserver
```

- Listar DAGs

```bash
make list-dags # Lista todas as DAGs registradas no Airflow
```

- Executar DAG diária manualmente

```bash
make run-dag-diario # Dispara manualmente a DAG b3_taxas_diario
```

- Executar DAG de backfill

```bash
make run-dag-backfill # Dispara manualmente a DAG b3_taxas_backfill com data de referência
```

- Acessar shell do container Airflow

```bash
make shell # Abre um shell bash dentro do container do webserver
```

</details>