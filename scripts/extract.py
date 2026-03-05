import requests
from pathlib import Path

BASE_URL = "https://www.b3.com.br/.../taxas"

def download_taxas(data_referencia: str, output_path: str) -> str:
    params = {"data": data_referencia}
    response = requests.get(BASE_URL, params=params, timeout=60)
    response.raise_for_status()

    file_path = Path(output_path) / f"taxas_{data_referencia}.csv"
    file_path.write_bytes(response.content)

    return str(file_path)