import pandas as pd
import folium
from folium.plugins import HeatMap, MarkerCluster
import numpy as np

def load_clinic_data():
    """Load and clean clinic location data"""
    df = pd.read_csv('Location Data/cleaned_Clinic_Locations_Google.csv')
    return df

def create_base_map(center_lat=0, center_lon=0, zoom=2):
    """Create a base map centered at specified coordinates"""
    return folium.Map(location=[center_lat, center_lon], zoom_start=zoom)

def visualize_clinic_distribution(df):
    """Create an interactive map showing clinic distribution with different layers"""
    # Calculate the center point for the map
    center_lat = df['clinic_lat'].mean()
    center_lon = df['clinic_lon'].mean()
    
    # Create base map
    m = create_base_map(center_lat, center_lon, zoom=3)
    
    # Create different layer groups
    all_clinics = folium.FeatureGroup(name='All Clinics')
    ponseti_clinics = folium.FeatureGroup(name='Ponseti Treatment Available')
    heatmap_layer = folium.FeatureGroup(name='Clinic Density Heatmap')
    
    # Add markers for all clinics
    marker_cluster = MarkerCluster()
    for idx, row in df.iterrows():
        # Create popup content
        popup_content = f"""
            <b>Clinic Details:</b><br>
            Country: {row['clinic_country']}<br>
            City: {row['clinic_city']}<br>
            Clinicians: {row['clinicians_available']}<br>
            Ponseti Treatment: {'Yes' if row['ponseti_treatment_available'] else 'No'}
        """
        
        # Add marker with popup
        folium.Marker(
            location=[row['clinic_lat'], row['clinic_lon']],
            popup=folium.Popup(popup_content, max_width=300),
            icon=folium.Icon(color='red' if row['ponseti_treatment_available'] else 'blue')
        ).add_to(marker_cluster)
    
    marker_cluster.add_to(all_clinics)
    
    # Add heatmap layer
    heat_data = df[['clinic_lat', 'clinic_lon']].values.tolist()
    HeatMap(heat_data).add_to(heatmap_layer)
    
    # Add all layers to map
    all_clinics.add_to(m)
    heatmap_layer.add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

def analyze_clinic_statistics(df):
    """Generate statistical analysis of clinic distribution"""
    stats = {
        'total_clinics': len(df),
        'countries_covered': df['clinic_country'].nunique(),
        'ponseti_available': df['ponseti_treatment_available'].sum(),
        'clinician_distribution': df['clinicians_available'].value_counts().to_dict()
    }
    return stats

def main():
    # Load data
    df = load_clinic_data()
    
    # Create visualization
    m = visualize_clinic_distribution(df)
    
    # Save the map
    m.save('clinic_distribution_map.html')
    
    # Generate statistics
    stats = analyze_clinic_statistics(df)
    
    # Print statistics
    print("\nClinic Distribution Statistics:")
    print(f"Total number of clinics: {stats['total_clinics']}")
    print(f"Number of countries covered: {stats['countries_covered']}")
    print(f"Number of clinics with Ponseti treatment: {stats['ponseti_available']}")
    print("\nClinician distribution:")
    for category, count in stats['clinician_distribution'].items():
        print(f"{category}: {count} clinics")

if __name__ == "__main__":
    main()
