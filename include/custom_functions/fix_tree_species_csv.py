"""
Fix tree species CSV by adding UUIDs and resolving duplicate species names.
"""

import pandas as pd
import uuid
import os

def fix_tree_species_csv():
    """Add UUIDs and fix duplicate species names in the tree species catalog."""
    
    # Load current CSV
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'tree_species_catalog.csv')
    df = pd.read_csv(csv_path)
    
    print(f"Original CSV has {len(df)} records")
    
    # Check for duplicates
    duplicates = df[df.duplicated(subset=['species_name'], keep=False)]
    if len(duplicates) > 0:
        print(f"Found {len(duplicates)} duplicate species names:")
        for _, row in duplicates.iterrows():
            print(f"  - {row['species_name']} ({row['common_name']})")
    
    # Fix the duplicate Prunus avium - rename the Wild Cherry version
    # Keep Sweet Cherry (cultivated version) and rename Wild Cherry to avoid conflict
    mask = (df['species_name'] == 'Prunus avium') & (df['common_name'] == 'Wild Cherry')
    df.loc[mask, 'species_name'] = 'Prunus avium subsp. avium'
    df.loc[mask, 'common_name'] = 'European Wild Cherry'
    
    # Check for any other duplicates
    remaining_duplicates = df[df.duplicated(subset=['species_name'], keep=False)]
    if len(remaining_duplicates) > 0:
        print(f"Still have {len(remaining_duplicates)} duplicates after fixes:")
        for _, row in remaining_duplicates.iterrows():
            print(f"  - {row['species_name']} ({row['common_name']})")
        # Remove any remaining duplicates (keep first occurrence)
        df = df.drop_duplicates(subset=['species_name'], keep='first')
    
    # Add UUID column as first column
    df.insert(0, 'species_id', [str(uuid.uuid4()) for _ in range(len(df))])
    
    # Reorder columns to have species_id first
    columns = ['species_id'] + [col for col in df.columns if col != 'species_id']
    df = df[columns]
    
    # Save fixed CSV
    df.to_csv(csv_path, index=False)
    
    print(f"Fixed CSV saved with {len(df)} records and UUIDs")
    print("New columns:", list(df.columns))
    
    # Show first few rows
    print("\nFirst 3 rows:")
    print(df.head(3).to_string())
    
    return df

if __name__ == "__main__":
    fix_tree_species_csv() 