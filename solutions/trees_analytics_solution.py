import logging
import os
from pathlib import Path

import duckdb
from airflow.sdk import Asset, asset

t_log = logging.getLogger("airflow.task")

# Define variables used in the DAG
_INCLUDE_PATH = Path(os.getenv("AIRFLOW_HOME")) / "include"
_DUCKDB_INSTANCE_NAME = os.getenv("DUCKDB_INSTANCE_NAME", f"{_INCLUDE_PATH}/trees.db")


@asset(schedule=[Asset(name="trees_data")])
def trees_analytics():

    sql_file_path = f"{_INCLUDE_PATH}/sql/trees_analytics.sql"

    with open(sql_file_path, "r") as file:
        analytics_query = file.read()

    cursor = duckdb.connect(_DUCKDB_INSTANCE_NAME)
    results = cursor.execute(analytics_query).fetchall()
    cursor.close()

    for result in results:
        print(result)