from scripts.transform import normalize_taxas
import pandas as pd

def test_normalize_taxas(tmp_path):
    file = tmp_path / "taxas.csv"
    file.write_text("tipo,venc,valor\nDI,2024-12,0.12")
    df = normalize_taxas(file, "2024-01-01")
    assert "data_referencia" in df.columns
    assert df.iloc[0]["taxa"] == 0.12