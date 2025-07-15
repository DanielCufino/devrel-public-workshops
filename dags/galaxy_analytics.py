from airflow.sdk import asset, Asset

from airflow.sdk import Asset, chain, Param, dag, task # This DAG uses the TaskFlow API. See: https://www.astronomer.io/docs/learn/airflow-decorators
from airflow.models.baseoperator import chain
from airflow.models.param import Param
from pendulum import datetime, duration
from tabulate import tabulate
import pandas as pd
import duckdb
import logging
import os
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
# Modularize code by importing functions from the include folder.
from include.custom_functions.galaxy_functions import get_galaxy_data


t_log = logging.getLogger("airflow.task")


_DUCKDB_INSTANCE_NAME = os.getenv("DUCKDB_INSTANCE_NAME", "include/astronomy.db")
_DUCKDB_TABLE_NAME = os.getenv("DUCKDB_TABLE_NAME", "galaxy_data")
_DUCKDB_TABLE_URI = f"duckdb://{_DUCKDB_INSTANCE_NAME}/{_DUCKDB_TABLE_NAME}"



@asset(schedule=(Asset("galaxy_data")))
def analyze_galaxies(
    duckdb_instance_name: str = _DUCKDB_INSTANCE_NAME,
    table_name: str = _DUCKDB_TABLE_NAME,
) -> None:
    """
    Analyze the galaxy data by creating an analytics
    table (in the logs!) with the count of galaxies
    by type.

    In production, you would write this data to a 
    persistent table somewhere and perhaps use it
    in an analytics dashboard.
    """

    cursor = duckdb.connect(duckdb_instance_name)

    query = f"""
        SELECT type_of_galaxy, COUNT(*) AS count
        FROM {_DUCKDB_TABLE_NAME}
        GROUP BY type_of_galaxy
        ORDER BY count DESC
    """

    galaxy_analysis_df = cursor.sql(query).df()
    t_log.info(tabulate(galaxy_analysis_df, headers="keys", tablefmt="pretty"))
    cursor.close()

    return galaxy_analysis_df

