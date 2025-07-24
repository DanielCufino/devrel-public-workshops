"""
Utility functions for the releaf recommendation system.
Contains geocoding, hardiness zone estimation, and confidence calculation functions.
"""

import json
import time
import random
import pandas as pd
from pathlib import Path
import logging

t_log = logging.getLogger("airflow.task")


DATA_PATH = (Path(__file__).parent.parent / "data").resolve().as_posix()


def get_coordinates_for_location(location_string: str) -> dict:
    """
    Get latitude and longitude for a location using cached geocoding.
    Uses local caching to avoid repeated API calls.
    """
    from geopy.geocoders import Nominatim

    locations_file = Path(f"{DATA_PATH}/locations.json")

    if not locations_file.exists():
        locations_file.write_text("{}")

    locations_data = json.loads(locations_file.read_text())

    if location_string in locations_data.keys():
        lat, lon = locations_data[location_string]
        return {"lat": lat, "lon": lon}

    time.sleep(2)

    geolocator = Nominatim(user_agent="releafApp/1.0 (Demo Project)")
    location_object = geolocator.geocode(location_string)

    if location_object is None:
        raise Exception(f"Geocoding failed for '{location_string}'")
    coordinates = (float(location_object.latitude), float(location_object.longitude))

    locations_data[location_string] = coordinates
    locations_file.write_text(json.dumps(locations_data, indent=2))

    t_log.info(
        f"Geocoded '{location_string}' -> {coordinates[0]:.4f}, {coordinates[1]:.4f}"
    )

    return {"lat": coordinates[0], "lon": coordinates[1]}


def get_hardiness_zone_for_location(latitude: float) -> int:
    """Estimate hardiness zone based on latitude."""
    abs_lat = abs(latitude)
    if abs_lat <= 23:  # Tropics
        return random.choice([10, 11, 12])
    elif abs_lat <= 35:  # Subtropics
        return random.choice([8, 9, 10])
    elif abs_lat <= 45:  # Temperate
        return random.choice([6, 7, 8])
    elif abs_lat <= 55:  # Cool temperate
        return random.choice([4, 5, 6])
    elif abs_lat <= 65:  # Subarctic
        return random.choice([2, 3, 4])
    else:  # Arctic
        return random.choice([1, 2])


def calculate_recommendation_confidence(species: pd.Series, location: dict) -> float:
    """Calculate confidence score for a tree recommendation."""
    confidence = 0.5  # Base confidence

    # Zone matching bonus
    user_zone = int(location["hardiness_zone"])
    if species["min_zone"] <= user_zone <= species["max_zone"]:
        confidence += 0.3

    # Soil matching bonus
    if (
        location["soil_type"]
        and location["soil_type"].split()[0] in species["ideal_soil"]
    ):
        confidence += 0.15

    # Growth rate preference (slight bias toward fast-growing)
    if species["growth_rate"] == "fast":
        confidence += 0.05
    elif species["growth_rate"] == "slow":
        confidence -= 0.05

    return min(0.95, max(0.1, confidence))


def create_user_record(user_data: dict, timestamp: str) -> dict:
    """
    Create a user record dictionary for database insertion.
    
    Args:
        user_data: Dictionary containing user information (user_id, name, latitude, longitude)
        timestamp: ISO timestamp for record creation
        
    Returns:
        Dictionary formatted for users table insertion
    """
    from faker import Faker
    
    fake = Faker()
    email = f"{user_data['name'].lower().replace(' ', '.')}@example.com"
    
    return {
        "user_id": user_data["user_id"],
        "email": email,
        "created_at": timestamp,
        "last_login": None,
        "zip_code": fake.postcode(),
        "latitude": user_data["latitude"],
        "longitude": user_data["longitude"],
        "user_type": "individual",
        "source": "manual_onboarding",
    }


def create_location_record(user_data: dict) -> dict:
    """
    Create a location record dictionary for database insertion.
    
    Args:
        user_data: Dictionary containing user information (user_id, location_string, 
                  latitude, longitude, estimated_hardiness_zone)
        
    Returns:
        Dictionary formatted for locations table insertion
    """
    import uuid
    import random
    
    return {
        "location_id": str(uuid.uuid4()),
        "user_id": user_data["user_id"],
        "address": user_data["location_string"],
        "latitude": user_data["latitude"],
        "longitude": user_data["longitude"],
        "elevation": random.randint(0, 1000),
        "aspect": random.choice([
            "north", "south", "east", "west", 
            "northeast", "southeast", "southwest", "northwest", "flat"
        ]),
        "slope_deg": round(random.uniform(0, 15), 1),
        "soil_type": random.choice([
            "well-drained", "moist well-drained", "sandy well-drained"
        ]),
        "sunlight_hours": round(random.uniform(6, 10), 1),
        "hardiness_zone": user_data["estimated_hardiness_zone"],
        "is_verified": False,
    }


def load_tree_species_catalog() -> pd.DataFrame:
    """
    Load the tree species catalog from CSV file.
    
    Returns:
        DataFrame containing tree species information
    """
    catalog_path = f"{DATA_PATH}/tree_species_catalog.csv"
    return pd.read_csv(catalog_path)


def filter_suitable_species(tree_species_df: pd.DataFrame, location: dict) -> pd.DataFrame:
    """
    Filter tree species based on location compatibility.
    
    Args:
        tree_species_df: DataFrame with all tree species
        location: Location data dictionary with hardiness_zone and soil_type
        
    Returns:
        Filtered DataFrame of suitable species
    """
    # Filter by hardiness zone compatibility
    user_zone = int(location["hardiness_zone"])
    suitable_species = tree_species_df[
        (tree_species_df["min_zone"] <= user_zone)
        & (tree_species_df["max_zone"] >= user_zone)
    ]
    
    # Further filter by soil type if we have enough species
    location_soil = location["soil_type"]
    if len(suitable_species) > 10:
        soil_matches = suitable_species[
            suitable_species["ideal_soil"].str.contains(
                location_soil.split()[0], na=False
            )
        ]
        if len(soil_matches) >= 3:
            suitable_species = soil_matches
    
    return suitable_species


def generate_recommendation_records(suitable_species: pd.DataFrame, location: dict, 
                                   user_data: dict, timestamp: str) -> list:
    """
    Generate tree recommendation records from suitable species.
    
    Args:
        suitable_species: DataFrame of filtered suitable species
        location: Location data dictionary
        user_data: User data dictionary  
        timestamp: ISO timestamp for the recommendations
        
    Returns:
        List of recommendation dictionaries ready for database insertion
    """
    import uuid
    import random
    
    num_recommendations = random.randint(3, 5)
    recommendations = []
    
    # Make a copy to avoid modifying the original DataFrame
    species_pool = suitable_species.copy()
    
    for i in range(min(num_recommendations, len(species_pool))):
        if len(species_pool) == 0:
            break
            
        # Select a random species
        selected_species = species_pool.sample(1).iloc[0]
        species_pool = species_pool.drop(selected_species.name)
        
        # Calculate confidence score
        confidence = calculate_recommendation_confidence(selected_species, location)
        
        # Create recommendation record
        recommendation = {
            "recommendation_id": str(uuid.uuid4()),
            "user_id": location["user_id"],
            "location_id": location["location_id"],
            "species_id": selected_species["species_id"],
            "generated_at": timestamp,
            "confidence_score": round(confidence, 3),
            "species_name": selected_species["species_name"],
            "common_name": selected_species["common_name"],
        }
        recommendations.append(recommendation)
    
    t_log.info(f"🌲 Generated {len(recommendations)} tree recommendations")
    if recommendations:
        top_rec = recommendations[0]
        t_log.info(f"🏆 Top recommendation: {top_rec['common_name']} (confidence: {top_rec['confidence_score']})")
    
    return recommendations


def insert_user_to_database(user_data: dict, cursor) -> None:
    """
    Insert user data into the users table.
    
    Args:
        user_data: User record dictionary
        cursor: DuckDB database cursor
    """
    cursor.execute(
        """
        INSERT OR IGNORE INTO users (user_id, email, created_at, last_login, zip_code, 
                         latitude, longitude, user_type, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_data["user_id"],
            user_data["email"],
            user_data["created_at"],
            user_data["last_login"],
            user_data["zip_code"],
            user_data["latitude"],
            user_data["longitude"],
            user_data["user_type"],
            user_data["source"],
        ),
    )
    t_log.info(f"✓ Inserted user: {user_data['email']}")


def insert_location_to_database(location_data: dict, cursor) -> None:
    """
    Insert location data into the locations table.
    
    Args:
        location_data: Location record dictionary
        cursor: DuckDB database cursor
    """
    cursor.execute(
        """
        INSERT OR IGNORE INTO locations (location_id, user_id, address, latitude, longitude,
                             elevation, aspect, slope_deg, soil_type, sunlight_hours,
                             hardiness_zone, is_verified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            location_data["location_id"],
            location_data["user_id"],
            location_data["address"],
            location_data["latitude"],
            location_data["longitude"],
            location_data["elevation"],
            location_data["aspect"],
            location_data["slope_deg"],
            location_data["soil_type"],
            location_data["sunlight_hours"],
            location_data["hardiness_zone"],
            location_data["is_verified"],
        ),
    )
    t_log.info(f"✓ Inserted location: {location_data['address']}")


def insert_recommendations_to_database(recommendations_data: list, cursor) -> None:
    """
    Insert tree recommendations into the tree_recommendations table.
    
    Args:
        recommendations_data: List of recommendation record dictionaries
        cursor: DuckDB database cursor
    """
    for rec in recommendations_data:
        cursor.execute(
            """
            INSERT OR IGNORE INTO tree_recommendations (recommendation_id, user_id, location_id,
                                            species_id, generated_at, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                rec["recommendation_id"],
                rec["user_id"],
                rec["location_id"],
                rec["species_id"],
                rec["generated_at"],
                rec["confidence_score"],
            ),
        )
    
    t_log.info(f"✓ Inserted {len(recommendations_data)} tree recommendations")
    if recommendations_data:
        t_log.info(f"📋 Top recommendation: {recommendations_data[0]['common_name']} (confidence: {recommendations_data[0]['confidence_score']})")


