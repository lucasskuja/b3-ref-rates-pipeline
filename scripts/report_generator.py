import os
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Configurar LLM
llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-3.5-turbo",
    temperature=0.5
)

def fetch_today_rates(connection_string: str, data_referencia: str) -> pd.DataFrame:
    """Busca as taxas de hoje do banco de dados (camada Gold)."""
    engine = create_engine(connection_string)
    
    query = f"""
    SELECT 
        tipo_curva,
        vencimento,
        taxa,
        data_referencia
    FROM curva_referencial_historica
    WHERE data_referencia = '{data_referencia}'
    ORDER BY tipo_curva, vencimento
    """
    
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    
    return df

def generate_report(data_referencia: str, connection_string: str) -> str:
    """
    Gera relatório narrativo usando LLM com base nos dados de taxas.
    """
    # Buscar dados
    df = fetch_today_rates(connection_string, data_referencia)
    
    if df.empty:
        return f"Nenhum dado disponível para {data_referencia}"
    
    # Extrair estatísticas básicas
    stats = {
        "data": data_referencia,
        "total_registros": len(df),
        "tipos_curva": df["tipo_curva"].unique().tolist(),
        "taxa_media": df["taxa"].mean(),
        "taxa_minima": df["taxa"].min(),
        "taxa_maxima": df["taxa"].max(),
        "taxa_desvio_padrao": df["taxa"].std()
    }
    
    # Criar prompt para o LLM
    prompt_template = PromptTemplate(
        input_variables=["stats", "df_summary"],
        template="""
        Você é um analista financeiro expert. Com base nos seguintes dados de Taxas Referenciais da B3 para {data_referencia}:
        
        - Total de registros: {total_registros}
        - Tipos de curva: {tipos_curva}
        - Taxa média: {taxa_media:.4f}%
        - Taxa mínima: {taxa_minima:.4f}%
        - Taxa máxima: {taxa_maxima:.4f}%
        - Desvio padrão: {taxa_desvio_padrao:.4f}%
        
        Gere um relatório executivo conciso (máximo 3 parágrafos) que:
        1. Resuma o comportamento das taxas do dia
        2. Identifique padrões ou anomalias significativas
        3. Forneça insights sobre o impacto para operações de crédito
        
        Mantenha um tom profissional e apropriado para stakeholders de crédito.
        """
    )
    
    # Formatar prompt com dados
    formatted_prompt = prompt_template.format(
        data=stats["data"],
        total_registros=stats["total_registros"],
        tipos_curva=", ".join(stats["tipos_curva"]),
        taxa_media=stats["taxa_media"],
        taxa_minima=stats["taxa_minima"],
        taxa_maxima=stats["taxa_maxima"],
        taxa_desvio_padrao=stats["taxa_desvio_padrao"]
    )
    
    # Gerar relatório via LLM
    response = llm.invoke(formatted_prompt)
    report_text = response.content
    
    # Montar relatório completo
    full_report = f"""
╔════════════════════════════════════════════════════════════════╗
║           RELATÓRIO DE TAXAS REFERENCIAIS B3                   ║
║                       {data_referencia}                        ║
╚════════════════════════════════════════════════════════════════╝

DATA: {data_referencia}
GERADO EM: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ANÁLISE EXECUTIVA:

{report_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ESTATÍSTICAS:

• Total de registros: {stats['total_registros']}
• Tipos de curva: {', '.join(stats['tipos_curva'])}
• Taxa média: {stats['taxa_media']:.4f}%
• Taxa mínima: {stats['taxa_minima']:.4f}%
• Taxa máxima: {stats['taxa_maxima']:.4f}%
• Desvio padrão: {stats['taxa_desvio_padrao']:.4f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Relatório automático gerado pelo Pipeline de Taxas Referenciais B3
Confidencial - Uso interno apenas

"""
    
    return full_report

def save_report(report_content: str, data_referencia: str, output_dir: str = "/tmp/reports") -> str:
    """Salva o relatório em arquivo."""
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"relatorio_taxas_{data_referencia}.txt"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    return filepath
