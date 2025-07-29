import os
from pathlib import Path

from airflow.sdk import Param, dag, task

# Define variables used in the DAG
_INCLUDE_PATH = Path(os.getenv("AIRFLOW_HOME")) / "include"
_USER_NAME = os.getenv("USER_NAME", "Kenten")
_USER_LOCATION = os.getenv("USER_LOCATION", "Seattle, WA, USA")


@dag(
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
def genai_trees():

    @task
    def extract_user_data(**context) -> dict:
        import uuid

        user_name = context["params"]["user_name"].strip()
        user_location = context["params"]["user_location"].strip()

        from include.custom_functions.trees_utils import (
            get_coordinates_for_location,
            get_hardiness_zone_for_location,
        )

        coordinates = get_coordinates_for_location(user_location)

        user_data = {
            "user_id": str(uuid.uuid4()),
            "name": user_name,
            "location_string": user_location,
            "latitude": coordinates["lat"],
            "longitude": coordinates["lon"],
            "estimated_hardiness_zone": get_hardiness_zone_for_location(
                coordinates["lat"]
            ),
        }

        return user_data

    @task
    def transform_user_data(user_data: dict, **context) -> dict:
        from include.custom_functions.trees_utils import (
            create_user_record,
            create_location_record,
        )

        ts = context["ts"]

        user_record = create_user_record(user_data, ts)
        location_record = create_location_record(user_data)

        transformed_data = {"user": user_record, "location": location_record}

        return transformed_data

    @task
    def generate_tree_recommendations(transformed_data: dict, **context) -> dict:
        from include.custom_functions.trees_utils import (
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

    @task.llm(
        model="gpt-4o-mini",
        result_type=str,
        system_prompt=(
            "Describe what the user's garden will look like in 10 years if they plant the recommended trees. "
            "Add at least 3 tree related puns. "
        ),
    )
    def generate_garden_description(full_user_data: dict):
        import json

        user_data = full_user_data["user"]
        location_data = full_user_data["location"]
        recommendations = full_user_data["recommendations"]

        user_data_string = (
            f"User: {json.dumps(user_data)}\n"
            f"Location: {json.dumps(location_data)}\n"
            f"Recommendations: {json.dumps(recommendations)}"
        )

        return user_data_string

    @task
    def print_llm_output(llm_output: str, **context):
        import textwrap
        import logging
        import os

        t_log = logging.getLogger("airflow.task")

        t_log.info("🤖 LLM GENERATED trees VISION:")
        t_log.info("=" * 80)
        user_name = context["params"]["user_name"]
        ds = context["ds"]

        os.makedirs(_INCLUDE_PATH / "garden_descriptions", exist_ok=True)
        file_name = f"{_INCLUDE_PATH}/garden_descriptions/{ds}_{user_name}_garden_description.txt"

        with open(file_name, "w") as f:
            f.write("")

        paragraphs = llm_output.split("\n\n")
        for paragraph in paragraphs:
            if paragraph.strip():
                wrapped_paragraph = textwrap.fill(paragraph.strip(), width=75)
                t_log.info(wrapped_paragraph)
                t_log.info("")

                with open(file_name, "a") as f:
                    f.write(wrapped_paragraph + "\n\n")

        t_log.info("=" * 80)

    _extract_user_data = extract_user_data()
    _transform_user_data = transform_user_data(_extract_user_data)
    _generate_tree_recommendations = generate_tree_recommendations(_transform_user_data)
    _llm_task = generate_garden_description(
        full_user_data=_generate_tree_recommendations
    )
    print_llm_output(_llm_task)


genai_trees()
