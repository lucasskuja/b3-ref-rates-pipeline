# 📈 Pipeline de Taxas Referenciais da B3

Este repositório contém a implementação de um pipeline de **extração, transformação e carga (ETL)** das **Taxas Referenciais da B3**, utilizando **Apache Airflow** para orquestração e **Postgres/S3** como camadas de armazenamento.

## 🚀 Visão Geral

O pipeline foi projetado para:

- Extrair diariamente as taxas referenciais publicadas pela B3.
- Normalizar e transformar os dados em formato analítico.
- Persistir em camadas **Bronze (Raw)**, **Silver (Normalizado)** e **Gold (Histórico consolidado)**.
- Disponibilizar dados para consumo por times de crédito e análises financeiras.

## 📂 Estrutura do Projeto

```
b3-taxas-pipeline/
│
├── dags/
│   ├── b3_taxas_diario.py        # DAG diário
│   └── b3_taxas_backfill.py      # DAG de backfill
│
├── scripts/
│   ├── extract.py                # Extração dos dados da B3
│   ├── transform.py              # Normalização e transformação
│   └── load.py                   # Carga no banco de dados
│
├── docs/                         # Documentação técnica
│   ├── arquitetura.md
│   ├── modelagem_dados.md
│   └── qualidade_dados.md
│
├── tests/                        # Testes unitários
│   ├── test_extract.py
│   ├── test_transform.py
│   └── test_load.py
│
├── requirements.txt              # Dependências do projeto
├── README.md                     # Este arquivo
└── .gitignore
```

## ⚙️ Tecnologias Utilizadas

- **Apache Airflow** → Orquestração dos DAGs
- **Python (requests, pandas, sqlalchemy)** → Scripts de ETL
- **Postgres/Athena** → Camada Gold
- **AWS S3** → Armazenamento bruto (Bronze)
- **Slack** → Alertas e monitoramento

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

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/b3-taxas-pipeline.git
   cd b3-taxas-pipeline
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure o Airflow:
   - Adicione os DAGs em `dags/`.
   - Configure variáveis de conexão (Postgres, S3).
   - Inicie o scheduler e webserver.

4. Execute o DAG diário:
   - Automático em dias úteis às 20h.

5. Execute o backfill manualmente:
   ```bash
   airflow dags trigger -d b3_taxas_backfill \
     --conf '{"data_referencia":"2024-01-02"}'
   ```