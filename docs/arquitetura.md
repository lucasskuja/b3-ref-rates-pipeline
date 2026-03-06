# Arquitetura da Solução

Fluxo:
B3 → Airflow → Bronze (S3) → Silver → Gold → Consumo analítico

Componentes:
- Airflow: orquestração
- S3: armazenamento bruto
- Postgres/Athena: camada Gold
- Slack: alertas

## 📊 Diagrama do Pipeline

```mermaid
flowchart TD
    A["B3 - Taxas Referenciais"] --> B["Airflow DAGs"]

    subgraph Bronze
        C["Raw - S3"]
    end

    subgraph Silver
        D["Normalizado"]
    end

    subgraph Gold
        E["Histórico Consolidado"]
    end

    B --> C --> D --> E --> F["Consumo Analítico"]
    B --> G["Slack - Alertas"]
```