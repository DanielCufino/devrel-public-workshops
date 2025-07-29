import logging
import os
from pathlib import Path

import duckdb
import pandas as pd
from airflow.models.baseoperator import chain
from airflow.sdk import Asset, dag, task
from pendulum import datetime, duration

t_log = logging.getLogger("airflow.task")

# Define variables used in the DAG
_INCLUDE_PATH = Path(os.getenv("AIRFLOW_HOME")) / "include"
_DATA_PATH = f"{_INCLUDE_PATH}/data"
_DUCKDB_INSTANCE_NAME = os.getenv("DUCKDB_INSTANCE_NAME", f"{_INCLUDE_PATH}/trees.db")


@dag(
    start_date=datetime(2025, 7, 1),
    schedule=None,
    max_active_runs=1,
    max_active_tasks=1,
    max_consecutive_failed_dag_runs=5,
    default_args={
        "owner": "Astro",
        "retries": 1,
        "retry_delay": duration(seconds=30),
    },
    tags=["Run this DAG first!"]
)
def trees_database_setup():

    @task
    def create_users_table(duckdb_instance_name: str = _DUCKDB_INSTANCE_NAME) -> None:
        t_log.info("Creating users table in DuckDB.")

        os.makedirs(os.path.dirname(duckdb_instance_name), exist_ok=True)

        cursor = duckdb.connect(duckdb_instance_name)

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id UUID PRIMARY KEY,
                email TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                zip_code TEXT,
                latitude DOUBLE,
                longitude DOUBLE,
                user_type TEXT, -- 'individual', 'organization', etc.
                source TEXT -- 'web', 'mobile', 'partner_campaign', etc.
            )
        """
        )

        cursor.close()
        t_log.info("Users table created successfully.")

    @task
    def create_locations_table(
        duckdb_instance_name: str = _DUCKDB_INSTANCE_NAME,
    ) -> None:
        t_log.info("Creating locations table in DuckDB.")

        cursor = duckdb.connect(duckdb_instance_name)

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS locations (
                location_id UUID PRIMARY KEY,
                user_id UUID REFERENCES users(user_id),
                address TEXT,
                latitude DOUBLE NOT NULL,
                longitude DOUBLE NOT NULL,
                elevation DOUBLE, -- meters
                aspect TEXT, -- 'north', 'south', etc.
                slope_deg DOUBLE, -- terrain slope
                soil_type TEXT,
                sunlight_hours DOUBLE, -- estimated avg daily sunlight
                hardiness_zone TEXT, -- e.g. '6b'
                is_verified BOOLEAN DEFAULT FALSE
            )
        """
        )

        cursor.close()
        t_log.info("Locations table created successfully.")

    @task
    def create_tree_species_catalog_table(
        duckdb_instance_name: str = _DUCKDB_INSTANCE_NAME,
    ) -> None:
        t_log.info("Creating tree_species_catalog table in DuckDB.")

        cursor = duckdb.connect(duckdb_instance_name)

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tree_species_catalog (
                species_id UUID PRIMARY KEY,
                species_name TEXT NOT NULL,
                common_name TEXT,
                min_zone TEXT,
                max_zone TEXT,
                ideal_soil TEXT,
                drought_tolerant BOOLEAN,
                max_height_m DOUBLE,
                growth_rate TEXT, -- 'fast', 'medium', 'slow'
                canopy_spread_m DOUBLE
            )
        """
        )

        cursor.close()
        t_log.info("Tree species catalog table created successfully.")

    @task
    def create_tree_recommendations_table(
        duckdb_instance_name: str = _DUCKDB_INSTANCE_NAME,
    ) -> None:
        t_log.info("Creating tree_recommendations table in DuckDB.")

        cursor = duckdb.connect(duckdb_instance_name)

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tree_recommendations (
                recommendation_id UUID PRIMARY KEY,
                user_id UUID REFERENCES users(user_id),
                location_id UUID REFERENCES locations(location_id),
                species_id UUID REFERENCES tree_species_catalog(species_id),
                generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                confidence_score DOUBLE, -- 0-1
            )
        """
        )

        cursor.close()
        t_log.info("Tree recommendations table created successfully.")

    @task
    def load_tree_species_catalog(
        duckdb_instance_name: str = _DUCKDB_INSTANCE_NAME,
    ) -> None:

        t_log.info("Loading tree species catalog data...")

        csv_path = f"{_DATA_PATH}/tree_species_catalog.csv"
        tree_species_df = pd.read_csv(csv_path)

        cursor = duckdb.connect(duckdb_instance_name)
        cursor.register("tree_species_df", tree_species_df)
        cursor.execute(
            "INSERT OR IGNORE INTO tree_species_catalog SELECT * FROM tree_species_df"
        )

        count = cursor.execute("SELECT COUNT(*) FROM tree_species_catalog").fetchone()[
            0
        ]
        cursor.close()

        t_log.info(
            f"Tree species catalog now has {count} total records (duplicates skipped if any)."
        )

    @task
    def load_users_data(duckdb_instance_name: str = _DUCKDB_INSTANCE_NAME) -> None:
        t_log.info("Loading users data...")

        csv_path = f"{_DATA_PATH}/users.csv"
        users_df = pd.read_csv(csv_path)

        users_df["created_at"] = pd.to_datetime(users_df["created_at"])
        users_df["last_login"] = pd.to_datetime(users_df["last_login"], errors="coerce")

        cursor = duckdb.connect(duckdb_instance_name)
        cursor.register("users_df", users_df)
        cursor.execute("INSERT OR IGNORE INTO users SELECT * FROM users_df")

        count = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        cursor.close()

        t_log.info(
            f"Users table now has {count} total records (duplicates skipped if any)."
        )

    @task
    def load_locations_data(duckdb_instance_name: str = _DUCKDB_INSTANCE_NAME) -> None:
        t_log.info("Loading locations data...")

        csv_path = f"{_DATA_PATH}/locations.csv"
        locations_df = pd.read_csv(csv_path)

        cursor = duckdb.connect(duckdb_instance_name)
        cursor.register("locations_df", locations_df)
        cursor.execute("INSERT OR IGNORE INTO locations SELECT * FROM locations_df")

        count = cursor.execute("SELECT COUNT(*) FROM locations").fetchone()[0]
        cursor.close()

        t_log.info(
            f"Locations table now has {count} total records (duplicates skipped if any)."
        )

    @task
    def load_recommendations_data(
        duckdb_instance_name: str = _DUCKDB_INSTANCE_NAME,
    ) -> None:
        t_log.info("Loading tree recommendations data...")

        csv_path = f"{_DATA_PATH}/tree_recommendations.csv"
        recommendations_df = pd.read_csv(csv_path)

        recommendations_df["generated_at"] = pd.to_datetime(
            recommendations_df["generated_at"]
        )

        cursor = duckdb.connect(duckdb_instance_name)
        cursor.register("recommendations_df", recommendations_df)
        cursor.execute(
            "INSERT OR IGNORE INTO tree_recommendations SELECT * FROM recommendations_df"
        )

        count = cursor.execute("SELECT COUNT(*) FROM tree_recommendations").fetchone()[
            0
        ]
        cursor.close()

        t_log.info(
            f"Tree recommendations table now has {count} total records (duplicates skipped if any)."
        )

    @task(outlets=[Asset(name="database_setup_complete")])
    def verify_data_loaded(duckdb_instance_name: str = _DUCKDB_INSTANCE_NAME) -> None:
        t_log.info("Verifying all data was loaded successfully...")

        cursor = duckdb.connect(duckdb_instance_name)

        tables = ["users", "locations", "tree_species_catalog", "tree_recommendations"]

        for table in tables:
            count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            t_log.info(f"✓ Table '{table}': {count} records")

        t_log.info("\n=== Sample Data Relationships ===")

        user_types = cursor.execute(
            """
            SELECT user_type, COUNT(*) as count 
            FROM users 
            GROUP BY user_type 
            ORDER BY count DESC
        """
        ).fetchall()
        t_log.info(f"User types: {dict(user_types)}")

        avg_locations = cursor.execute(
            """
            SELECT AVG(location_count) as avg_locations
            FROM (
                SELECT user_id, COUNT(*) as location_count 
                FROM locations 
                GROUP BY user_id
            )
        """
        ).fetchone()[0]
        t_log.info(f"Average locations per user: {avg_locations:.1f}")

        avg_recommendations = cursor.execute(
            """
            SELECT AVG(rec_count) as avg_recs
            FROM (
                SELECT location_id, COUNT(*) as rec_count 
                FROM tree_recommendations 
                GROUP BY location_id
            )
        """
        ).fetchone()[0]
        t_log.info(f"Average recommendations per location: {avg_recommendations:.1f}")

        top_species = cursor.execute(
            """
            SELECT tsc.species_name, tsc.common_name, COUNT(*) as recommendation_count
            FROM tree_recommendations tr 
            JOIN tree_species_catalog tsc ON tr.species_id = tsc.species_id
            GROUP BY tsc.species_name, tsc.common_name 
            ORDER BY recommendation_count DESC 
            LIMIT 5
        """
        ).fetchall()
        t_log.info(
            f"Top 5 recommended species: {[(f'{row[0]} ({row[1]})', row[2]) for row in top_species]}"
        )

        cursor.close()
        t_log.info("🌳 Database setup and data loading complete! 🌲")

    users_table_task = create_users_table()
    tree_catalog_table_task = create_tree_species_catalog_table()
    locations_table_task = create_locations_table()
    recommendations_table_task = create_tree_recommendations_table()

    load_tree_catalog_task = load_tree_species_catalog()
    load_users_task = load_users_data()
    load_locations_task = load_locations_data()
    load_recommendations_task = load_recommendations_data()

    verify_task = verify_data_loaded()

    chain(
        [users_table_task, tree_catalog_table_task],
        [locations_table_task, recommendations_table_task],
        [load_tree_catalog_task, load_users_task],
        load_locations_task,
        load_recommendations_task,
        verify_task,
    )


trees_database_setup()