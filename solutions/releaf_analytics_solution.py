from airflow.sdk import asset
import duckdb
import logging
from pathlib import Path

t_log = logging.getLogger("airflow.task")

# Define path variables for relative paths
INCLUDE_PATH = (Path(__file__).parent.parent / "include").resolve().as_posix()
SQL_PATH = (Path(__file__).parent.parent / "include" / "sql").resolve().as_posix()
_DUCKDB_INSTANCE_NAME = f"{INCLUDE_PATH}/releaf.db"


@asset(schedule=None)
def releaf_analytics():

    sql_file_path = f"{SQL_PATH}/releaf_analytics.sql"

    with open(sql_file_path, "r") as file:
        analytics_query = file.read()

    cursor = duckdb.connect(_DUCKDB_INSTANCE_NAME)
    results = cursor.execute(analytics_query).fetchall()
    cursor.close()

    for result in results:
        print(result)
