from airflow.hooks.base import BaseHook
from minio import Minio
import json
from io import BytesIO
from airflow.exceptions import AirflowNotFoundException
import pandas as pd
from sqlalchemy import create_engine
from io import StringIO

BUCKET_NAME = 'stock-market'

def _get_stock_prices(url, symbol):
    import requests

    url = f"{url}{symbol}?metrics=high?&interval=1d&range=1y"
    api = BaseHook.get_connection('stock_api')
    response = requests.get(url, headers=api.extra_dejson['headers'])

    return json.dumps(response.json()['chart']['result'][0])

def _get_minio_client():
    minio = BaseHook.get_connection('minio')
    client = Minio(
        endpoint = minio.extra_dejson['endpoint_url'].split('//')[1],
        access_key = minio.login,
        secret_key = minio.password,
        secure = False
    )
    return client

def _store_prices(stock):
    client = _get_minio_client()
    if not client.bucket_exists(BUCKET_NAME):
        client.make_bucket(BUCKET_NAME)
    stock = json.loads(stock)
    symbol = stock['meta']['symbol']
    data = json.dumps(stock, ensure_ascii = False).encode('utf8')
    objw = client.put_object(
        bucket_name = BUCKET_NAME,
        object_name = f'{symbol}/prices.json',
        data = BytesIO(data),
        length = len(data)
    )
    return f'{objw.bucket_name}/{symbol}'

def _get_formatted_csv(path):
    client = _get_minio_client()
    prefix_name = f"{path.split('/')[1]}/formatted_prices/"
    objects = client.list_objects(BUCKET_NAME, prefix = prefix_name, recursive=True)
    for obj in objects:
        if obj.object_name.endswith('.csv'):
            return obj.object_name
    return AirflowNotFoundException('Não encontrou o arquivo CSV')


def _load_to_dw(csv_object_name):
    """
    Carrega o arquivo CSV do MinIO para PostgreSQL
    csv_object_name: nome do objeto retornado por _get_formatted_csv
    """
    # Conecta ao MinIO e baixa o arquivo
    client = _get_minio_client()
    print(f"Baixando {csv_object_name} do MinIO...")
    response = client.get_object(BUCKET_NAME, csv_object_name)
    csv_content = response.read().decode('utf8')

    # Conecta ao PostgreSQL DW usando a conexão dedicada
    pg_conn = BaseHook.get_connection('postgres_dw')
    connection_string = f"postgresql://{pg_conn.login}:{pg_conn.password}@{pg_conn.host}:{pg_conn.port}/{pg_conn.schema}"
    engine = create_engine(connection_string)

    # Converte CSV para DataFrame e carrega no banco
    df = pd.read_csv(StringIO(csv_content))

    # Cria automaticamente a tabela stock_prices no schema public e insere os dados
    df.to_sql(
        'stock_prices',
        con=engine,
        if_exists='append',
        index=False,
        method='multi'
    )

    print(f"✅ {len(df)} registros carregados no PostgreSQL DW (public)!")
    return f"Loaded {len(df)} records"
