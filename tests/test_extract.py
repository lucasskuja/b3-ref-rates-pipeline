from scripts.extract import download_taxas
import os

def test_download_taxas(tmp_path):
    # Mock simples (não chama API real)
    fake_file = tmp_path / "taxas_2024-01-01.csv"
    fake_file.write_text("tipo,venc,valor\nDI,2024-12,0.12")
    assert fake_file.exists()