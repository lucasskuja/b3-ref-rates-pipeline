from sqlalchemy import create_engine

def upsert_taxas(df, connection_string: str):
    engine = create_engine(connection_string)
    with engine.begin() as conn:
        df.to_sql(
            "curva_referencial_historica",
            conn,
            if_exists="append",
            index=False
        )