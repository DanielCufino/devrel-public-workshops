"""
Generate realistic fake data for the releaf database.
This script creates interconnected data for users, locations, and tree recommendations
with proper foreign key relationships.
"""

import pandas as pd
import uuid
import random
from datetime import datetime, timedelta
from faker import Faker
import os

fake_en = Faker("en_US")
fake_es = Faker("es_ES")
fake_de = Faker("de_DE")
fake_fr = Faker("fr_FR")
fake_au = Faker("en_AU")
fake_in = Faker("en_IN")
fake_br = Faker("pt_BR")
fake_jp = Faker("ja_JP")

fakers = [fake_en, fake_es, fake_de, fake_fr, fake_au, fake_in, fake_br, fake_jp]


def load_tree_species():
    """Load tree species data from CSV."""
    csv_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "tree_species_catalog.csv"
    )
    return pd.read_csv(csv_path)


def get_hardiness_zone_for_location(latitude):
    """Estimate hardiness zone based on latitude (rough approximation)."""
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


def get_soil_types():
    """Return list of possible soil types."""
    return [
        "well-drained",
        "moist well-drained",
        "sandy well-drained",
        "clay well-drained",
        "wet",
        "moist to wet",
        "moist acidic",
        "well-drained acidic",
        "sandy loam",
        "deep well-drained",
        "rocky well-drained",
        "adaptable",
        "moist alkaline",
        "rocky alkaline",
    ]


def get_aspects():
    """Return list of possible slope aspects."""
    return [
        "north",
        "northeast",
        "east",
        "southeast",
        "south",
        "southwest",
        "west",
        "northwest",
        "flat",
    ]


def generate_users(num_users=500):
    """Generate fake user data with global diversity."""
    users = []

    for _ in range(num_users):
        # Use random faker for diversity
        fake = random.choice(fakers)

        # Generate realistic coordinates (avoid oceans/poles)
        latitude = random.uniform(-60, 70)  # Exclude extreme polar regions
        longitude = random.uniform(-180, 180)

        # Bias towards populated areas
        if random.random() < 0.3:  # 30% chance for major population centers
            # Major cities coordinates (rough)
            major_cities = [
                (40.7128, -74.0060),  # New York
                (51.5074, -0.1278),  # London
                (35.6762, 139.6503),  # Tokyo
                (48.8566, 2.3522),  # Paris
                (-33.8688, 151.2093),  # Sydney
                (19.0760, 72.8777),  # Mumbai
                (-23.5505, -46.6333),  # São Paulo
                (39.9042, 116.4074),  # Beijing
                (55.7558, 37.6176),  # Moscow
                (-26.2041, 28.0473),  # Johannesburg
            ]
            base_lat, base_lon = random.choice(major_cities)
            # Add some variance around the city
            latitude = base_lat + random.uniform(-2, 2)
            longitude = base_lon + random.uniform(-2, 2)

        user = {
            "user_id": str(uuid.uuid4()),
            "email": fake.email(),
            "created_at": fake.date_time_between(start_date="-2y", end_date="now"),
            "last_login": (
                fake.date_time_between(start_date="-30d", end_date="now")
                if random.random() > 0.1
                else None
            ),
            "zip_code": fake.postcode() if random.random() > 0.2 else None,
            "latitude": round(latitude, 6),
            "longitude": round(longitude, 6),
            "user_type": random.choices(
                ["individual", "organization", "school", "government", "nonprofit"],
                weights=[70, 15, 5, 5, 5],
            )[0],
            "source": random.choices(
                ["web", "mobile", "partner_campaign", "social_media", "referral"],
                weights=[40, 30, 15, 10, 5],
            )[0],
        }
        users.append(user)

    return pd.DataFrame(users)


def generate_locations(users_df, avg_locations_per_user=1.3):
    """Generate location data for users."""
    locations = []

    for _, user in users_df.iterrows():
        # Most users have 1 location, some have 2-3
        num_locations = random.choices([1, 2, 3], weights=[70, 25, 5])[0]

        for i in range(num_locations):
            # First location is usually close to user's coordinates
            if i == 0:
                lat_offset = random.uniform(-0.1, 0.1)  # Within ~10km
                lon_offset = random.uniform(-0.1, 0.1)
            else:
                lat_offset = random.uniform(-1, 1)  # Within ~100km
                lon_offset = random.uniform(-1, 1)

            location_lat = user["latitude"] + lat_offset
            location_lon = user["longitude"] + lon_offset

            # Ensure coordinates stay in valid range
            location_lat = max(-90, min(90, location_lat))
            location_lon = max(-180, min(180, location_lon))

            fake = random.choice(fakers)

            location = {
                "location_id": str(uuid.uuid4()),
                "user_id": user["user_id"],
                "address": (
                    fake.address().replace("\n", ", ")
                    if random.random() > 0.3
                    else None
                ),
                "latitude": round(location_lat, 6),
                "longitude": round(location_lon, 6),
                "elevation": (
                    random.randint(0, 3000) if random.random() > 0.2 else None
                ),  # meters
                "aspect": random.choice(get_aspects()),
                "slope_deg": (
                    round(random.uniform(0, 45), 1) if random.random() > 0.3 else None
                ),
                "soil_type": random.choice(get_soil_types()),
                "sunlight_hours": round(random.uniform(4, 12), 1),
                "hardiness_zone": get_hardiness_zone_for_location(location_lat),
                "is_verified": random.choices([True, False], weights=[30, 70])[0],
            }
            locations.append(location)

    return pd.DataFrame(locations)


def generate_tree_recommendations(
    users_df, locations_df, tree_species_df, avg_recommendations_per_location=2.5
):
    """Generate tree recommendations that match location conditions."""
    recommendations = []

    for _, location in locations_df.iterrows():
        # Number of recommendations per location
        num_recs = random.choices([1, 2, 3, 4, 5], weights=[20, 30, 25, 15, 10])[0]

        # Get location hardiness zone
        location_zone = location["hardiness_zone"]
        if isinstance(location_zone, str):
            location_zone_num = int(location_zone.rstrip("ab"))
        else:
            location_zone_num = int(location_zone)

        # Filter tree species suitable for this hardiness zone
        suitable_species = tree_species_df[
            (tree_species_df["min_zone"].astype(int) <= location_zone_num)
            & (tree_species_df["max_zone"].astype(int) >= location_zone_num)
        ]

        # If no exact matches, be more lenient with zone matching
        if len(suitable_species) < 5:
            suitable_species = tree_species_df[
                (tree_species_df["min_zone"].astype(int) <= location_zone_num + 1)
                & (tree_species_df["max_zone"].astype(int) >= location_zone_num - 1)
            ]

        # Additional filtering based on soil type preferences
        location_soil = location["soil_type"]
        if location_soil and len(suitable_species) > 10:
            # Prefer species that match soil type, but don't require exact match
            soil_matches = suitable_species[
                suitable_species["ideal_soil"].str.contains(
                    location_soil.split()[0], na=False
                )
            ]
            if len(soil_matches) >= num_recs:
                suitable_species = soil_matches

        # Generate recommendations
        for i in range(min(num_recs, len(suitable_species))):
            if len(suitable_species) == 0:
                continue

            # Select species (without replacement for this location)
            selected_species = suitable_species.sample(1).iloc[0]
            suitable_species = suitable_species.drop(selected_species.name)

            # Calculate confidence score based on how well the tree matches
            confidence = 0.5  # Base confidence

            # Zone matching bonus
            species_min = int(selected_species["min_zone"])
            species_max = int(selected_species["max_zone"])
            if species_min <= location_zone_num <= species_max:
                confidence += 0.3

            # Soil matching bonus
            if (
                location_soil
                and location_soil.split()[0] in selected_species["ideal_soil"]
            ):
                confidence += 0.15

            # Growth rate preference (slight bias toward fast-growing)
            if selected_species["growth_rate"] == "fast":
                confidence += 0.05
            elif selected_species["growth_rate"] == "slow":
                confidence -= 0.05

            confidence = min(0.95, max(0.1, confidence))  # Clamp between 0.1 and 0.95

            recommendation = {
                "recommendation_id": str(uuid.uuid4()),
                "user_id": location["user_id"],
                "location_id": location["location_id"],
                "species_id": selected_species["species_id"],
                "generated_at": datetime.now() - timedelta(days=random.randint(0, 90)),
                "confidence_score": round(confidence, 3),
            }
            recommendations.append(recommendation)

    return pd.DataFrame(recommendations)


def save_data_to_csv(users_df, locations_df, recommendations_df):
    """Save all dataframes to CSV files."""
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(data_dir, exist_ok=True)

    users_df.to_csv(os.path.join(data_dir, "users.csv"), index=False)
    locations_df.to_csv(os.path.join(data_dir, "locations.csv"), index=False)
    recommendations_df.to_csv(
        os.path.join(data_dir, "tree_recommendations.csv"), index=False
    )

    print(f"Generated data saved to {data_dir}/")
    print(f"Users: {len(users_df)} records")
    print(f"Locations: {len(locations_df)} records")
    print(f"Tree Recommendations: {len(recommendations_df)} records")


def main():
    """Main function to generate all data."""
    print("Loading tree species catalog...")
    tree_species_df = load_tree_species()
    print(f"Loaded {len(tree_species_df)} tree species")

    print("Generating users...")
    users_df = generate_users(num_users=500)

    print("Generating locations...")
    locations_df = generate_locations(users_df)

    print("Generating tree recommendations...")
    recommendations_df = generate_tree_recommendations(
        users_df, locations_df, tree_species_df
    )

    print("Saving data to CSV files...")
    save_data_to_csv(users_df, locations_df, recommendations_df)

    print("Data generation complete!")

    # Print some summary statistics
    print("\n=== Summary Statistics ===")
    print(f"Total users: {len(users_df)}")
    print(f"Total locations: {len(locations_df)}")
    print(f"Total recommendations: {len(recommendations_df)}")
    print(f"Avg locations per user: {len(locations_df) / len(users_df):.1f}")
    print(
        f"Avg recommendations per location: {len(recommendations_df) / len(locations_df):.1f}"
    )
    print(f"User types: {users_df['user_type'].value_counts().to_dict()}")
    print(f"Source distribution: {users_df['source'].value_counts().to_dict()}")

    return users_df, locations_df, recommendations_df


if __name__ == "__main__":
    users_df, locations_df, recommendations_df = main()
