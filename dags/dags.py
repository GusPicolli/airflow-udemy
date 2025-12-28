from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def hello():
    print("HELLO WORLD - AIRFLOW FUNCIONANDO")

with DAG(
    dag_id="debug_minimal",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
) as dag:

    hello_task = PythonOperator(
        task_id="hello",
        python_callable=hello
    )
