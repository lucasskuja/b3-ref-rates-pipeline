## Visão Geral

A DAG `b3_taxas_report` utiliza um Large Language Model (LLM), especificamente OpenAI GPT-3.5-turbo, para gerar relatórios executivos automáticos e inteligentes sobre as taxas referenciais da B3. Os relatórios são enviados via email para times de crédito diariamente.

## Arquitetura

``` mermaid
flowchart TD

A["1️⃣ ExternalTaskSensor<br/>Aguarda conclusão de <b>b3_taxas_diario</b>"]

B["2️⃣ Fetch de Dados<br/>SELECT * FROM curva_referencial_historica"]

C["3️⃣ Processamento"]

C1["📊 Cálculo de estatísticas<br/>min / max / avg / std"]
C2["🧩 Preparação de prompt estruturado"]

D["4️⃣ Análise via LLM<br/>🧠 OpenAI GPT<br/>Análise + narrativa automática"]

E["5️⃣ Formatação de Relatório"]

E1["🧾 Cabeçalho estruturado"]
E2["🤖 Análise executiva<br/>gerada por IA"]
E3["📈 Estatísticas detalhadas"]

F["6️⃣ Envio de Email"]

F1["📄 Formato HTML + Texto"]
F2["📧 SMTP<br/>Gmail / Servidor corporativo"]

A --> B
B --> C

C --> C1
C --> C2

C1 --> D
C2 --> D

D --> E

E --> E1
E --> E2
E --> E3

E1 --> F
E2 --> F
E3 --> F

F --> F1
F --> F2
```

## Fluxo de Execução

### 1. ExternalTaskSensor (20:20)

A DAG aguarda até 1 hora que `b3_taxas_diario` complete com sucesso. Se falhar, o DAG inteiro falha.

### 2. Fetch de Dados

Executa SQL para trazer todas as taxas do dia:
```sql
SELECT tipo_curva, vencimento, taxa, data_referencia
FROM curva_referencial_historica
WHERE data_referencia = '{data_referencia}'
```

### 3. Análise via LLM

O script `report_generator.py` utiliza:
- **LangChain**: Framework para integrar LLMs
- **OpenAI GPT-3.5-turbo**: Modelo de linguagem
- **PromptTemplate**: Template estruturado para o prompt

**Prompt enviado para o LLM:**
```
Você é um analista financeiro expert. Com base nos seguintes dados...

- Total de registros: X
- Tipos de curva: [DI, SELIC, CDI]
- Taxa média: X.XX%
- Taxa mínima: X.XX%
- Taxa máxima: X.XX%
- Desvio padrão: X.XX%

Gere um relatório executivo conciso (máximo 3 parágrafos) que:
1. Resuma o comportamento das taxas do dia
2. Identifique padrões ou anomalias significativas
3. Forneça insights sobre o impacto para operações de crédito

Mantenha um tom profissional...
```

### 4. Formatação e Envio

O relatório final é formatado com:

**Versão Texto:**
```
╔════════════════════════════════════════════════════════════════╗
║           RELATÓRIO DE TAXAS REFERENCIAIS B3                   ║
║                       2024-03-08                               ║
╚════════════════════════════════════════════════════════════════╝

DATA: 2024-03-08
GERADO EM: 08/03/2024 20:23:15

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ANÁLISE EXECUTIVA:

[Análise gerada pela IA...]
```

**Versão HTML:**
- Cabeçalho com logo/identidade visual
- Análise em destaque
- Tabela formatada com estatísticas
- Rodapé com aviso de confidencialidade

## Configuração

### Variáveis de Ambiente Necessárias

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `OPENAI_API_KEY` | Chave de API OpenAI | `sk-...` |
| `SMTP_SERVER` | Servidor SMTP | `smtp.gmail.com` |
| `SMTP_PORT` | Porta SMTP | `587` |
| `SENDER_EMAIL` | Email remetente | `relatorios@empresa.com` |
| `SENDER_PASSWORD` | Senha/token SMTP | `abcd1234efgh` |
| `EMAIL_RECIPIENTS` | Destinatários | `team@emp.com.br,manager@emp.com.br` |
| `DB_CONNECTION_STRING` | String de conexão Postgres | `postgresql://user:pass@host:5432/db` |

### Configuração Gmail

Para usar Gmail (recomendado para laboratórios/POC):

1. Ativar 2FA em sua conta
2. Gerar [Senha de Aplicativo](https://myaccount.google.com/apppasswords)
3. Usar essa senha em `SENDER_PASSWORD`

Exemplo:
```
SENDER_EMAIL=reports@gmail.com
SENDER_PASSWORD=abcd efgh ijkl mnop  # Senha gerada pelo Gmail
```

### Configuração SMTP Corporativo

Para servidor corporativo (ex: Outlook, Exchange):

```
SMTP_SERVER=smtp.outlook.office365.com
SMTP_PORT=587
SENDER_EMAIL=seu.email@empresa.com
SENDER_PASSWORD=sua-senha
```

## Componentes Principais

### `scripts/report_generator.py`

**Funções principais:**

| Função | Responsabilidade |
|--------|-------------------|
| `fetch_today_rates()` | Busca dados do Postgres para um dia |
| `generate_report()` | Coordena análise com LLM e monta relatório |
| `save_report()` | Salva relatório em arquivo local |

**Fluxo:**
```python
# 1. Buscar dados
df = fetch_today_rates(connection_string, data_referencia)

# 2. Calcular estatísticas
stats = {
    "taxa_media": df["taxa"].mean(),
    "taxa_minima": df["taxa"].min(),
    ...
}

# 3. Enviar para LLM
response = llm.invoke(formatted_prompt)

# 4. Montar relatório
full_report = f"""
╔════════════════════════════════════════════════════════════════╗
...
"""

# 5. Salvar
save_report(full_report, data_referencia)
```

### `scripts/email_sender.py`

**Funções principais:**

| Função | Responsabilidade |
|--------|-------------------|
| `send_report_email()` | Envia relatório via SMTP |
| `parse_email_list()` | Converte string de emails em lista |

**Exemplo de uso:**
```python
send_report_email(
    report_content=report,
    data_referencia="2024-03-08",
    email_recipients=["team@empresa.com.br", "manager@empresa.com.br"]
)
```

### `dags/b3_taxas_report.py`

**DAG com dois passos:**

1. **ExternalTaskSensor**: Aguarda `b3_taxas_diario`
2. **PythonOperator**: Executa `generate_and_send_report()`

## Exemplo de Saída

### Relatório Gerado

```
╔════════════════════════════════════════════════════════════════╗
║           RELATÓRIO DE TAXAS REFERENCIAIS B3                  ║
║                       2024-03-08                               ║
╚════════════════════════════════════════════════════════════════╝

DATA: 2024-03-08
GERADO EM: 08/03/2024 20:23:15

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ANÁLISE EXECUTIVA:

O mercado de taxas referenciais apresentou movimento de reconversão
nesta sexta-feira, com a curva de DI mantendo estabilidade acima de
10,80% para prazos mais longos. A Selic foi mantida em 13,75%, 
refletindo a expectativa de inflação controlada. Para operações de
crédito, recomenda-se atenção especial aos vencimentos de 30-60 dias,
onde observou-se maior volatilidade. As operações com taxas 
referenciadas ao CDI devem monitorar closely a curva de DI para 
oportunidades de refinanciamento.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ESTATÍSTICAS:

• Total de registros: 45
• Tipos de curva: DI, SELIC, CDI
• Taxa média: 11.23%
• Taxa mínima: 9.87%
• Taxa máxima: 13.75%
• Desvio padrão: 1.45%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Relatório automático gerado pelo Pipeline de Taxas Referenciais B3
Confidencial - Uso interno apenas
```

## Testes

### Executar testes

```bash
pytest tests/test_report.py -v
```

### Testes disponíveis

- ✅ `test_parse_email_list` - Validação de parsing de emails
- ✅ `test_save_report_creates_file` - Salvamento de arquivo
- ✅ `test_send_email_with_valid_config` - Envio de email (mock)
- ✅ `test_generate_report_success` - Geração de relatório

### Executar teste específico

```bash
pytest tests/test_report.py::TestParseEmailList::test_parse_comma_separated -v
```

## Troubleshooting

### Problema: "ModuleNotFoundError: No module named 'langchain'"

**Solução:**
```bash
pip install -r requirements.txt
# ou especificamente:
pip install langchain langchain-openai openai
```

### Problema: "Invalid API key" do OpenAI

**Verificar:**
- Chave é válida em https://platform.openai.com
- Variável `OPENAI_API_KEY` está configurada
- Não há espaços extras na chave

### Problema: "SMTP Authentication Error"

**Verificar:**
- Credenciais SMTP corretas
- Para Gmail: usar senha de app, não a senha da conta
- SMTP_SERVER e SMTP_PORT corretos
- Firewall não está bloqueando SMTP

### Problema: DAG não executa às 20:20

**Verificar:**
- DAG está ativada no Airflow UI
- Scheduler está rodando
- `ExternalTaskSensor` está com timeout adequado
- `b3_taxas_diario` está executando com sucesso

## Custos

### OpenAI API
- **Modelo**: gpt-3.5-turbo
- **Custo aproximado**: ~$0.0005 por relatório
- **Para 250 dias úteis/ano**: ~$0.13/ano

### SMTP
- **Gmail**: Gratuito
- **Servidor corporativo**: Dependente da empresa

## Segurança

⚠️ **Boas práticas:**

1. **Nunca commit credenciais**: Use `.env` ou variáveis de ambiente
2. **Chaves de API**: Use `OPENAI_API_KEY` segura
3. **Senhas SMTP**: Pre ferir senhas de aplicativo
4. **Dados**: Relatórios contêm dados financeiros → Confidencial
5. **Email**: Validar destinatários antes de ativar automaticamente

### Checklist de Segurança

- [ ] Variáveis de ambiente configuradas (não in code)
- [ ] `.env` adicionado ao `.gitignore`
- [ ] OpenAI API key restrita a modelos necessários
- [ ] Destinatários de email verificados
- [ ] Relatários salvos em local seguro
- [ ] Logs não expõem credenciais
