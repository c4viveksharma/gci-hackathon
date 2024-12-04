import pandas as pd
import googlemaps
import time
import json
from pathlib import Path

# Google Maps API Key
API_KEY = "AIzaSyAMOAJ8OkNO-wCGFmjYMNNbdRruqLjV9ig"

# Initialize Google Maps client
gmaps = googlemaps.Client(key=API_KEY)

# Constants
RATE_LIMIT_DELAY = 0.1  # 100ms between requests
MAX_RETRIES = 3

def load_progress(progress_file):
    """Load previously geocoded results"""
    if Path(progress_file).exists():
        with open(progress_file, 'r') as f:
            return json.load(f)
    return {}

def save_progress(geocoded_data, progress_file):
    """Save geocoding progress"""
    with open(progress_file, 'w') as f:
        json.dump(geocoded_data, f)

def extract_lat_long(lat_long_str):
    """Extract latitude and longitude from the Lat/Long column"""
    if pd.isna(lat_long_str):
        return None, None
    try:
        # Handle POINT format
        if 'POINT' in lat_long_str:
            # Extract numbers from format like "POINT (77.57541979660013 12.965939330486481)"
            coords = lat_long_str.replace('POINT (', '').replace(')', '').split()
            return float(coords[1]), float(coords[0])  # lat, long
        # Handle comma-separated format
        elif ',' in lat_long_str:
            # Extract from format like "28.67433948261137, 77.13399019632512"
            lat, lon = map(float, lat_long_str.split(','))
            return lat, lon
    except:
        return None, None
    return None, None

def geocode_address(address_components):
    """
    Geocode an address with retries and error handling
    """
    # Construct address query
    query = ", ".join(str(comp) for comp in address_components if pd.notna(comp) and str(comp).strip())
    
    for attempt in range(MAX_RETRIES):
        try:
            # Add delay for rate limiting
            time.sleep(RATE_LIMIT_DELAY)
            
            # Perform geocoding request
            geocode_result = gmaps.geocode(query)
            
            if geocode_result:
                result = geocode_result[0]
                location = result['geometry']['location']
                return {
                    'lat': location['lat'],
                    'lng': location['lng'],
                    'formatted_address': result['formatted_address'],
                    'query': query
                }
            else:
                print(f"No results found for: {query}")
                return None
                
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                print(f"Error geocoding {query} after {MAX_RETRIES} attempts: {str(e)}")
                return None
            time.sleep(RATE_LIMIT_DELAY * (attempt + 1))  # Exponential backoff
    
    return None

def geocode_india_clinics():
    """Geocode Indian clinic addresses with progress tracking"""
    # Read India clinic data
    file_path = 'C:/GCI_Hackathon/Location Data/India Clinic Locations.csv'
    df = pd.read_csv(file_path)
    
    # Clean column names by removing trailing spaces
    df.columns = df.columns.str.strip()
    
    # Load previous progress
    progress_file = 'india_geocoding_progress.json'
    geocoded_results = load_progress(progress_file)
    
    # Add/update columns for results
    df['clinic_lat'] = None
    df['clinic_lon'] = None
    df['formatted_address'] = None
    
    # Track progress
    total = len(df)
    success_count = 0
    failure_count = 0
    
    print(f"Starting geocoding for {total} Indian clinics...")
    
    # Process each clinic
    for index, row in df.iterrows():
        # First check if coordinates are already provided in the Lat/Long column
        lat, lon = extract_lat_long(row['Lat/Long'])
        if lat is not None and lon is not None:
            df.at[index, 'clinic_lat'] = lat
            df.at[index, 'clinic_lon'] = lon
            df.at[index, 'formatted_address'] = row['Clinic Address']
            success_count += 1
            continue
        
        # Create unique key for this clinic
        clinic_key = f"{row['Clinic Name']}_{row['State']}"
        
        # Skip if already geocoded in previous run
        if clinic_key in geocoded_results:
            result = geocoded_results[clinic_key]
            df.at[index, 'clinic_lat'] = result['lat']
            df.at[index, 'clinic_lon'] = result['lng']
            df.at[index, 'formatted_address'] = result['formatted_address']
            success_count += 1
            continue
        
        # Prepare address components
        address_components = [
            row['Clinic Address'],
            row['District'],
            row['State'],
            'India'  # Explicitly add country
        ]
        
        # Geocode the address
        result = geocode_address(address_components)
        
        if result:
            df.at[index, 'clinic_lat'] = result['lat']
            df.at[index, 'clinic_lon'] = result['lng']
            df.at[index, 'formatted_address'] = result['formatted_address']
            geocoded_results[clinic_key] = result
            success_count += 1
        else:
            failure_count += 1
            print(f"Failed to geocode: {row['Clinic Name']} in {row['State']}")
        
        # Save progress periodically
        if (index + 1) % 10 == 0:
            save_progress(geocoded_results, progress_file)
            print(f"Progress: {index + 1}/{total} clinics processed")
    
    # Save final results
    save_progress(geocoded_results, progress_file)
    output_file = 'C:/GCI_Hackathon/Location Data/cleaned_India_Clinic_Locations.csv'
    df.to_csv(output_file, index=False)
    
    print(f"\nGeocoding complete:")
    print(f"Successfully geocoded: {success_count}")
    print(f"Failed to geocode: {failure_count}")
    print(f"Results saved to {output_file}")
    
    return df

def main():
    print("Starting geocoding process for Indian clinics...")
    geocode_india_clinics()

if __name__ == "__main__":
    main()
