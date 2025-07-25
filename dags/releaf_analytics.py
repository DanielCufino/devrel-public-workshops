from airflow.sdk import asset
import duckdb
import logging
from pathlib import Path
import os

t_log = logging.getLogger("airflow.task")

# Define variables used in the DAG
_INCLUDE_PATH = Path(os.getenv("AIRFLOW_HOME")) / "include"
_DUCKDB_INSTANCE_NAME = os.getenv("DUCKDB_INSTANCE_NAME", f"{_INCLUDE_PATH}/releaf.db")


@asset(schedule=None)
# Add your function here
