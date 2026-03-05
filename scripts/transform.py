import pandas as pd

def normalize_taxas(file_path: str, data_referencia: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df["data_referencia"] = data_referencia
    # Normalização básica (ajuste conforme schema real)
    df = df.rename(columns={"tipo": "tipo_curva", "venc": "vencimento", "valor": "taxa"})
    return df