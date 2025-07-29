import logging
import os
from pathlib import Path

import duckdb
from airflow.sdk import Asset, asset

t_log = logging.getLogger("airflow.task")

# Define variables used in the DAG
_INCLUDE_PATH = Path(os.getenv("AIRFLOW_HOME")) / "include"
_DUCKDB_INSTANCE_NAME = os.getenv("DUCKDB_INSTANCE_NAME", f"{_INCLUDE_PATH}/trees.db")


@asset(schedule=None)
# Add your function here
