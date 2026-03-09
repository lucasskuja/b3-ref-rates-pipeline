import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_report_email(
    report_content: str,
    data_referencia: str,
    email_recipients: list,
    smtp_server: str = None,
    smtp_port: int = None,
    sender_email: str = None,
    sender_password: str = None
) -> bool:
    """
    Envia o relatório de taxas para um grupo de email.
    
    Args:
        report_content: Conteúdo do relatório em texto
        data_referencia: Data da referência (YYYY-MM-DD)
        email_recipients: Lista de emails destinatários
        smtp_server: Servidor SMTP (padrão: env var SMTP_SERVER)
        smtp_port: Porta SMTP (padrão: env var SMTP_PORT)
        sender_email: Email do remetente (padrão: env var SENDER_EMAIL)
        sender_password: Senha do remetente (padrão: env var SENDER_PASSWORD)
    
    Returns:
        True se enviado com sucesso, False caso contrário
    """
    
    # Carregar configurações do ambiente
    smtp_server = smtp_server or os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
    sender_email = sender_email or os.getenv("SENDER_EMAIL")
    sender_password = sender_password or os.getenv("SENDER_PASSWORD")
    
    if not sender_email or not sender_password:
        raise ValueError("SENDER_EMAIL e SENDER_PASSWORD devem ser configurados")
    
    if not email_recipients:
        raise ValueError("Lista de destinatários não pode estar vazia")
    
    try:
        # Criar mensagem
        message = MIMEMultipart("alternative")
        message["Subject"] = f"Relatório de Taxas Referenciais B3 - {data_referencia}"
        message["From"] = sender_email
        message["To"] = ", ".join(email_recipients)
        
        # Corpo em texto
        text_part = MIMEText(report_content, "plain", "utf-8")
        message.attach(text_part)
        
        # Corpo em HTML (versão formatada)
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="background-color: white; padding: 20px; border-radius: 8px; max-width: 800px; margin: 0 auto;">
                    <h1 style="color: #003366; border-bottom: 2px solid #003366; padding-bottom: 10px;">
                        📊 Relatório de Taxas Referenciais B3
                    </h1>
                    <p style="color: #666; font-size: 12px;">
                        <strong>Data:</strong> {data_referencia} | 
                        <strong>Gerado em:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
                    </p>
                    <pre style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #003366; overflow-x: auto; font-size: 12px; line-height: 1.6;">
{report_content}
                    </pre>
                    <hr style="border: none; border-top: 1px solid #ddd; margin-top: 20px; padding-top: 20px;">
                    <p style="color: #999; font-size: 11px; text-align: center;">
                        Relatório automático gerado pelo Pipeline de Taxas Referenciais B3<br>
                        Confidencial - Uso interno apenas
                    </p>
                </div>
            </body>
        </html>
        """
        
        html_part = MIMEText(html_content, "html", "utf-8")
        message.attach(html_part)
        
        # Conectar ao servidor SMTP e enviar
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email_recipients, message.as_string())
        
        print(f"Email enviado com sucesso para {len(email_recipients)} destinatário(s)")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"Erro de autenticação SMTP: {e}")
        raise
    except smtplib.SMTPException as e:
        print(f"Erro ao enviar email SMTP: {e}")
        raise
    except Exception as e:
        print(f"Erro inesperado ao enviar email: {e}")
        raise

def parse_email_list(email_string: str) -> list:
    """
    Converte string de emails (separados por vírgula ou ponto-e-vírgula) em lista.
    
    Args:
        email_string: String como "email1@example.com, email2@example.com"
    
    Returns:
        Lista de emails validados
    """
    separator = "," if "," in email_string else ";"
    emails = [email.strip() for email in email_string.split(separator)]
    return [email for email in emails if email and "@" in email]
