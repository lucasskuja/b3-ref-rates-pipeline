import pandas as pd
from scripts.load import upsert_taxas

def test_upsert_taxas(monkeypatch):
    df = pd.DataFrame([{"data_referencia":"2024-01-01","tipo_curva":"DI","vencimento":"2024-12","taxa":0.12}])
    def fake_to_sql(*args, **kwargs): return None
    monkeypatch.setattr(df, "to_sql", fake_to_sql)
    upsert_taxas(df, "sqlite:///:memory:")