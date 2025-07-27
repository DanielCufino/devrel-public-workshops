from airflow.sdk import dag, task, Param, Asset
from airflow.models.baseoperator import chain
import duckdb
import logging
from pendulum import duration, datetime
import uuid
from pathlib import Path
import os

t_log = logging.getLogger("airflow.task")

# Define variables used in the DAG
_INCLUDE_PATH = Path(os.getenv("AIRFLOW_HOME")) / "include"
_DUCKDB_INSTANCE_NAME = os.getenv("DUCKDB_INSTANCE_NAME", f"{_INCLUDE_PATH}/releaf.db")
_USER_NAME = os.getenv("USER_NAME", "Kenten")
_USER_LOCATION = os.getenv("USER_LOCATION", "Seattle, WA, USA")


@dag(
    start_date=datetime(2025, 7, 1),
    schedule=[Asset(name="database_setup_complete")],
    max_consecutive_failed_dag_runs=5,
    max_active_runs=1,
    default_args={
        "owner": "Astro",
        "retries": 1,
        "retry_delay": duration(seconds=30),
    },
    params={
        "user_name": Param(
            _USER_NAME,
            type="string",
            title="User Name",
            description="Full name of the user to onboard (e.g., 'Jane Smith')",
        ),
        "user_location": Param(
            _USER_LOCATION,
            type="string",
            title="User Location",
            description="User's location for tree recommendations (e.g., 'Austin, TX, USA' or 'London, UK')",
        ),
    },
)
def etl_releaf():

    @task()
    def check_tables_exist(duckdb_instance_name: str = _DUCKDB_INSTANCE_NAME) -> bool:
        cursor = duckdb.connect(duckdb_instance_name)
        tables = cursor.sql("SHOW TABLES").fetchall()
        tables = [table[0] for table in tables]
        needed_tables = [
            "locations",
            "tree_recommendations",
            "tree_species_catalog",
            "users",
        ]
        for table in needed_tables:
            if table not in tables:
                raise Exception(
                    f"Table {table} does not exist in the database. Run the releaf_database_setup DAG to create the necessary tables."
                )
        cursor.close()

    @task
    def extract_user_data(**context) -> dict:
        user_name = context["params"]["user_name"].strip()
        user_location = context["params"]["user_location"].strip()
        ts = context["ts"]

        return {"user_name": user_name, "user_location": user_location, "ts": ts}

    @task
    def transform_user_data(user_data: dict) -> dict:
        from include.custom_functions.releaf_utils import (
            create_user_record,
            create_location_record,
            get_coordinates_for_location,
            get_hardiness_zone_for_location,
        )

        user_name = user_data["user_name"]
        user_location = user_data["user_location"]
        ts = user_data["ts"]

        coordinates = get_coordinates_for_location(user_location)

        enriched_user_data = {
            "user_id": str(uuid.uuid4()),
            "name": user_name,
            "location_string": user_location,
            "latitude": coordinates["lat"],
            "longitude": coordinates["lon"],
            "estimated_hardiness_zone": get_hardiness_zone_for_location(
                coordinates["lat"]
            ),
        }

        user_record = create_user_record(enriched_user_data, ts)
        location_record = create_location_record(enriched_user_data)

        return {"user": user_record, "location": location_record}

    @task
    def generate_tree_recommendations(transformed_data: dict, **context) -> dict:
        from include.custom_functions.releaf_utils import (
            load_tree_species_catalog,
            filter_suitable_species,
            generate_recommendation_records,
        )

        location = transformed_data["location"]
        user_data = transformed_data["user"]
        ts = context["ts"]

        tree_species_df = load_tree_species_catalog()
        suitable_species = filter_suitable_species(tree_species_df, location)
        recommendations = generate_recommendation_records(
            suitable_species, location, user_data, ts
        )

        result = {
            "user": transformed_data["user"],
            "location": transformed_data["location"],
            "recommendations": recommendations,
        }

        return result

    @task
    def load_user_data(
        final_data: dict, duckdb_instance_name: str = _DUCKDB_INSTANCE_NAME
    ):
        from include.custom_functions.releaf_utils import (
            insert_user_to_database,
            insert_location_to_database,
            insert_recommendations_to_database,
        )

        cursor = duckdb.connect(duckdb_instance_name)

        insert_user_to_database(final_data["user"], cursor)
        insert_location_to_database(final_data["location"], cursor)
        insert_recommendations_to_database(final_data["recommendations"], cursor)

        t_log.info("🎉 Successfully loaded all user onboarding data!")

        cursor.close()

        return final_data

    @task(outlets=[Asset(name="etl_complete")])
    def summarize_onboarding(final_data: dict, **context):
        user_name = context["params"]["user_name"]
        user_location = context["params"]["user_location"]

        user = final_data["user"]
        location = final_data["location"]
        recommendations = final_data["recommendations"]

        t_log.info("🌲 USER ONBOARDING COMPLETE! 🌲")
        t_log.info(f"User: {user_name} ({user['email']})")
        t_log.info(f"Location: {user_location}")
        t_log.info(
            f"Generated {len(recommendations)} personalized tree recommendations:"
        )

        for i, rec in enumerate(recommendations, 1):
            t_log.info(f"  {i}. {rec['common_name']} ({rec['species_name']})")
            t_log.info(f"     Confidence: {rec['confidence_score']}")

        t_log.info(f"User ID: {user['user_id']}")
        t_log.info(f"Location ID: {location['location_id']}")
        t_log.info("Ready for tree planting! 🌱")

    _check_tables_exist = check_tables_exist()

    _extract_user_data = extract_user_data()
    _transform_user_data = transform_user_data(_extract_user_data)
    _generate_tree_recommendations = generate_tree_recommendations(_transform_user_data)
    _load_user_data = load_user_data(_generate_tree_recommendations)
    _summarize_onboarding = summarize_onboarding(_load_user_data)

    chain(
        _extract_user_data,
        _transform_user_data,
        _generate_tree_recommendations,
        _load_user_data,
        _summarize_onboarding,
    )

    chain(
        _check_tables_exist,
        _load_user_data,
    )


etl_releaf()
