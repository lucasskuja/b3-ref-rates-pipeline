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