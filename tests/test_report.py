import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import patch, MagicMock
from scripts.report_generator import generate_report, save_report, fetch_today_rates
from scripts.email_sender import send_report_email, parse_email_list

# Testes para parse_email_list
class TestParseEmailList:
    def test_parse_single_email(self):
        result = parse_email_list("user@example.com")
        assert result == ["user@example.com"]
    
    def test_parse_comma_separated(self):
        result = parse_email_list("user1@example.com, user2@example.com")
        assert result == ["user1@example.com", "user2@example.com"]
    
    def test_parse_semicolon_separated(self):
        result = parse_email_list("user1@example.com; user2@example.com")
        assert result == ["user1@example.com", "user2@example.com"]
    
    def test_parse_with_whitespace(self):
        result = parse_email_list("  user1@example.com  ,  user2@example.com  ")
        assert result == ["user1@example.com", "user2@example.com"]
    
    def test_parse_invalid_emails_filtered(self):
        result = parse_email_list("user1@example.com, invalid, user2@example.com")
        assert result == ["user1@example.com", "user2@example.com"]

# Testes para save_report
class TestSaveReport:
    def test_save_report_creates_file(self, tmp_path):
        import os
        
        content = "Test report content"
        data_ref = "2024-01-01"
        
        report_path = save_report(content, data_ref, str(tmp_path))
        
        assert os.path.exists(report_path)
        assert "relatorio_taxas_2024-01-01" in report_path
        
        with open(report_path, "r") as f:
            saved_content = f.read()
        
        assert saved_content == content
    
    def test_save_report_creates_directory(self, tmp_path):
        import os
        
        content = "Test report"
        output_dir = str(tmp_path / "new_dir")
        
        report_path = save_report(content, "2024-01-01", output_dir)
        
        assert os.path.exists(output_dir)
        assert os.path.exists(report_path)

# Testes para email_sender
class TestSendReportEmail:
    def test_send_email_with_valid_config(self):
        """Teste se validações básicas funcionam (sem enviar email real)."""
        with patch("smtplib.SMTP") as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            result = send_report_email(
                report_content="Test content",
                data_referencia="2024-01-01",
                email_recipients=["test@example.com"],
                smtp_server="smtp.example.com",
                smtp_port=587,
                sender_email="sender@example.com",
                sender_password="password"
            )
            
            assert result is True
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with("sender@example.com", "password")
            mock_server.sendmail.assert_called_once()
    
    def test_send_email_no_recipients_raises_error(self):
        """Teste se erro é levantado sem destinatários."""
        with pytest.raises(ValueError):
            send_report_email(
                report_content="Test",
                data_referencia="2024-01-01",
                email_recipients=[],
                sender_email="sender@example.com",
                sender_password="password"
            )
    
    def test_send_email_no_credentials_raises_error(self):
        """Teste se erro é levantado sem credenciais."""
        with pytest.raises(ValueError):
            send_report_email(
                report_content="Test",
                data_referencia="2024-01-01",
                email_recipients=["test@example.com"],
                sender_email=None,
                sender_password=None
            )

# Testes para generate_report
class TestGenerateReport:
    @patch("scripts.report_generator.fetch_today_rates")
    @patch("scripts.report_generator.llm.invoke")
    def test_generate_report_success(self, mock_llm, mock_fetch):
        """Teste geração bem-sucedida de relatório."""
        # Mock dados
        mock_df = pd.DataFrame({
            "tipo_curva": ["DI", "DI", "SELIC"],
            "vencimento": [30, 90, 180],
            "taxa": [10.5, 11.0, 11.5],
            "data_referencia": ["2024-01-01"] * 3
        })
        mock_fetch.return_value = mock_df
        
        # Mock resposta da LLM
        mock_response = MagicMock()
        mock_response.content = "Análise de mercado positiva..."
        mock_llm.return_value = mock_response
        
        # Executar
        report = generate_report("2024-01-01", "postgresql://localhost/test")
        
        # Validações
        assert "RELATÓRIO DE TAXAS REFERENCIAIS B3" in report
        assert "2024-01-01" in report
        assert "Taxa média:" in report
        assert mock_fetch.called
        assert mock_llm.called
    
    @patch("scripts.report_generator.fetch_today_rates")
    def test_generate_report_empty_data(self, mock_fetch):
        """Teste com dados vazios."""
        mock_fetch.return_value = pd.DataFrame()
        
        report = generate_report("2024-01-01", "postgresql://localhost/test")
        
        assert "Nenhum dado disponível" in report
