import os
import sys
import json
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import PythonOperator


# code_path = "/root/demo/lab03/etl_scripts"
# sys.path.insert(0, code_path)

from etl_scripts.transform import transform_data
from etl_scripts.ExtractDataFromAPItoGCS import main

# AIRFLOW_HOME = os.environ.get('AIRFLOW_HOME', '/opt/airflow')
# CREDS_TARGET_DIR = AIRFLOW_HOME + '/warm-physics-405522-a07e9b7bfc0d.json'

# with open(CREDS_TARGET_DIR, 'r') as f:
#     credentials_content = f.read()


default_args = {
    "owner": "amith.nandivada",
    "depends_on_past": False,
    "start_date": datetime(2023, 11, 1),
    "retries": 1,
    "retry_delay": timedelta(seconds=5)
}


with DAG(
    dag_id="outcomes_dag",
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
) as dag:
        start = BashOperator(task_id = "START",
                             bash_command = "echo start")

        # copy_creds = BashOperator(task_id = "COPY_CREDS", bash_command = "echo start")

        extract_api_data_to_gcs =  PythonOperator(task_id = "EXTRACT_API_DATA_TO_GCS",
                                                  python_callable = main,)

        transform_data_step = PythonOperator(task_id="TRANSFORM_DATA",
                                             python_callable=transform_data,)

        end = BashOperator(task_id = "END", bash_command = "echo end")

        start >> extract_api_data_to_gcs >> transform_data_step >> end