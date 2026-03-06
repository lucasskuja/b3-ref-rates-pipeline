# Makefile para gerenciar o pipeline B3 Taxas Referenciais

# Subir containers do projeto
up:
	@echo "🔼 Subindo containers..."
	docker compose up -d --build

# Inicializar Airflow (cria banco e usuário)
init:
	@echo "🛠️ Inicializando banco do Airflow..."
	docker compose up airflow-init

# Derrubar containers
down:
	@echo "⏹️ Derrubando containers..."
	docker compose down

# Derrubar containers e volumes (reset total)
clean:
	@echo "🧹 Limpando containers e volumes..."
	docker compose down -v

# Reiniciar containers
restart:
	@echo "🔄 Reiniciando containers..."
	docker compose down
	docker compose up -d --build

# Rebuild da imagem Docker
build:
	@echo "🏗️ Rebuild da imagem..."
	docker compose build

# Mostrar status dos serviços
ps:
	@echo "📋 Status dos containers:"
	docker compose ps

# Logs em tempo real
logs:
	@echo "📜 Exibindo logs..."
	docker compose logs -f

# Logs apenas do scheduler
logs-scheduler:
	docker compose logs -f airflow-scheduler

# Logs apenas do webserver
logs-webserver:
	docker compose logs -f airflow-webserver

# Listar DAGs
list-dags:
	@echo "📊 Listando DAGs..."
	docker compose exec airflow-webserver airflow dags list

# Executar DAG diário manualmente
run-dag-diario:
	@echo "▶️ Executando DAG diário..."
	docker compose exec airflow-webserver airflow dags trigger b3_taxas_diario

# Executar DAG de backfill manualmente
run-dag-backfill:
	@echo "▶️ Executando DAG de backfill..."
	docker compose exec airflow-webserver airflow dags trigger b3_taxas_backfill --conf '{"data_referencia":"2024-01-02"}'

# Acessar shell do container Airflow
shell:
	@echo "💻 Entrando no container..."
	docker compose exec airflow-webserver bash