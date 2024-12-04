import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap, MarkerCluster
import plotly.express as px
from streamlit_folium import folium_static
import numpy as np
from scipy.spatial.distance import cdist
from math import radians, cos, sin, asin, sqrt
import os

# Set page config
st.set_page_config(
    page_title="Global Clubfoot Initiative Dashboard",
    page_icon="👣",
    layout="wide"
)

# Display logo
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("GCI_logo.png", use_column_width=True, width=300)

# Add subheader
st.subheader("Clinic Profiling and Analysis by Country")

# Add custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stTitle {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        padding-bottom: 1rem;
        border-bottom: 2px solid #3498db;
        margin-bottom: 2rem;
    }
    .stSubheader {
        color: #2980b9;
        font-size: 1.8rem;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
    }
    .metric-label {
        color: #7f8c8d;
        font-size: 0.9rem;
    }
    .map-instructions {
        background-color: #e8f4f8;
        border-left: 4px solid #3498db;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 0 5px 5px 0;
    }
    .sidebar .stSelectbox label, .sidebar .stMultiSelect label {
        color: #2c3e50;
        font-weight: 600;
    }
    /* Country selector indicator */
    .country-indicator {
        position: fixed;
        left: 20px;
        top: 50%;
        background-color: #3498db;
        color: white;
        padding: 10px 15px;
        border-radius: 8px;
        z-index: 1000;
        display: flex;
        align-items: center;
        gap: 10px;
        animation: bounce 2s infinite;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateX(0); }
        50% { transform: translateX(10px); }
    }
    
    .arrow-left {
        width: 0;
        height: 0;
        border-top: 8px solid transparent;
        border-bottom: 8px solid transparent;
        border-right: 12px solid white;
    }
    </style>
    """, unsafe_allow_html=True)

# Add country selector indicator
st.markdown("""
    <div class="country-indicator">
        <div class="arrow-left"></div>
        <span>Select Your Country</span>
    </div>
""", unsafe_allow_html=True)

# Add custom CSS with animations
st.markdown("""
    <style>
    /* Animated title */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { transform: translateX(-50px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .title-container {
        animation: fadeIn 1.5s ease-out;
        text-align: center;
        padding: 1rem;
        margin-bottom: 2rem;
    }
    
    .ngo-info {
        animation: slideIn 1.5s ease-out;
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #2980b9;
    }
    
    .metric-card {
        animation: fadeIn 1s ease-out;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .map-instructions {
        animation: slideIn 1s ease-out;
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 5px solid #27ae60;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess all required data"""
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load global clinic data
    clinics_df = pd.read_csv(os.path.join(current_dir, 'Location Data', 'cleaned_Clinic_Locations_Google.csv'))
    
    # Load patient location data
    patients_df = pd.read_csv(os.path.join(current_dir, 'Location Data', 'Dummy - Patient Location.csv'))
    
    # Load treatment data
    treatment_df = pd.read_csv(os.path.join(current_dir, 'Treatment Data', 'Processed_Treatment_Cases_All_Years.csv'))
    
    # Convert coordinates to float for clinics
    for col in ['clinic_lat', 'clinic_lon']:
        clinics_df[col] = pd.to_numeric(clinics_df[col], errors='coerce')
    
    # Convert coordinates to float for patients
    patients_df['patient_location_lat'] = pd.to_numeric(patients_df['patient_location_lat'], errors='coerce')
    patients_df['patient_location_long'] = pd.to_numeric(patients_df['patient_location_long'], errors='coerce')
    
    # Drop rows with missing coordinates
    clinics_df = clinics_df.dropna(subset=['clinic_lat', 'clinic_lon'])
    patients_df = patients_df.dropna(subset=['patient_location_lat', 'patient_location_long', 'patient_country'])
    
    # Fill NaN values with appropriate defaults
    clinics_df['clinic_city'] = clinics_df['clinic_city'].fillna('City not available')
    clinics_df['formatted_address'] = clinics_df['formatted_address'].fillna('Address not available')
    clinics_df['ponseti_treatment_available'] = clinics_df['ponseti_treatment_available'].fillna('Unknown')
    
    # Group patients by location to get counts for heatmap weights
    patients_df['location_key'] = patients_df['patient_location_lat'].astype(str) + '_' + patients_df['patient_location_long'].astype(str)
    location_counts = patients_df.groupby('location_key').size().reset_index(name='patient_count')
    patients_df = patients_df.merge(location_counts, on='location_key', how='left')
    
    return clinics_df, patients_df, treatment_df

def get_available_countries(clinics_df):
    """Get list of available countries from clinic data"""
    return sorted(clinics_df['clinic_country'].unique())

def calculate_metrics(clinics_df, patients_df=None, selected_countries=None):
    """Calculate basic metrics for selected countries"""
    if selected_countries and 'All Countries' not in selected_countries:
        # Convert single string to list if necessary
        if isinstance(selected_countries, str):
            selected_countries = [selected_countries]
        clinics_df = clinics_df[clinics_df['clinic_country'].isin(selected_countries)]
        if patients_df is not None:
            patients_df = patients_df[patients_df['patient_country'].isin(selected_countries)]
    
    total_clinics = len(clinics_df)
    ponseti_clinics = len(clinics_df[clinics_df['ponseti_treatment_available'] == True])
    total_patients = len(patients_df) if patients_df is not None else 0
    
    # Calculate weighted Ponseti coverage rate
    if total_clinics > 0:
        # Base rate from number of Ponseti clinics
        base_rate = (ponseti_clinics / total_clinics) * 100
        
        # Geographic distribution factor
        # For "All Countries", use a simplified calculation to improve performance
        if selected_countries == ['All Countries']:
            # Calculate distribution based on country-level presence instead of individual clinics
            countries_with_ponseti = len(clinics_df[clinics_df['ponseti_treatment_available'] == True]['clinic_country'].unique())
            total_countries = len(clinics_df['clinic_country'].unique())
            distribution_factor = countries_with_ponseti / total_countries
        else:
            # For specific countries, use the detailed geographic calculation
            if ponseti_clinics > 1:
                clinic_coords = clinics_df[clinics_df['ponseti_treatment_available'] == True][['clinic_lat', 'clinic_lon']]
                
                # Optimize by sampling points if there are too many clinics
                if len(clinic_coords) > 50:
                    clinic_coords = clinic_coords.sample(n=50, random_state=42)
                
                total_area = 0
                coord_array = clinic_coords.values
                for i in range(len(coord_array)):
                    # Only calculate distances to 10 nearest points for each clinic
                    for j in range(i+1, min(i+11, len(coord_array))):
                        dist = haversine(
                            coord_array[i][1],  # lon
                            coord_array[i][0],  # lat
                            coord_array[j][1],  # lon
                            coord_array[j][0]   # lat
                        )
                        total_area += dist
                distribution_factor = min(1, total_area / (100 * min(50, ponseti_clinics)))
            else:
                distribution_factor = 1 if ponseti_clinics == 1 else 0
        
        # Calculate final weighted rate
        ponseti_rate = base_rate * distribution_factor
    else:
        ponseti_rate = 0
    
    return {
        'total_clinics': total_clinics,
        'active_ponseti_clinics': ponseti_clinics,
        'ponseti_rate': round(ponseti_rate, 1),
        'total_patients': total_patients
    }

def create_coverage_map(clinics_df, patients_df=None, max_distance_km=50, show_density=False, selected_country='All Countries'):
    """Create an interactive map showing clinic locations with coverage and optional patient density"""
    if len(clinics_df) == 0:
        return None
    
    # Filter clinics by country
    if selected_country != 'All Countries':
        clinics_df = clinics_df[clinics_df['clinic_country'] == selected_country]
    
    # Calculate map center based on filtered clinics
    center_lat = clinics_df['clinic_lat'].mean()
    center_lon = clinics_df['clinic_lon'].mean()
    
    # Create base map with appropriate zoom level
    m = folium.Map(location=[center_lat, center_lon], 
                  zoom_start=6 if selected_country != 'All Countries' else 4)
    
    # Create feature groups for different layers
    all_clinics = folium.FeatureGroup(name="All Clinics")
    ponseti_clinics = folium.FeatureGroup(name="Ponseti Clinics Only")
    coverage_group = folium.FeatureGroup(name="Coverage Areas")
    density_group = folium.FeatureGroup(name="Patient Density")
    
    # Add clinic markers and coverage areas
    for idx, row in clinics_df.iterrows():
        # Create detailed popup text
        popup_text = f"""
            <div style='font-family: Arial; font-size: 12px;'>
                <h4 style='margin: 0; color: #2c3e50;'>{row['clinic_city']}, {row['clinic_country']}</h4>
                <hr style='margin: 5px 0;'>
                <b>Location:</b><br>
                {row['formatted_address']}<br><br>
                <b>Status:</b> Active<br>
                <b>Ponseti Treatment:</b> {'Available' if row['ponseti_treatment_available'] else 'Not Available'}<br>
                <b>Clinicians Available:</b> {row['clinicians_available']}<br>
            </div>
        """
        
        # Create marker with appropriate color based on Ponseti availability
        is_ponseti = row['ponseti_treatment_available']
        marker = folium.Marker(
            location=[row['clinic_lat'], row['clinic_lon']],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(
                color='green' if is_ponseti else 'red',
                icon='info-sign',
                prefix='fa'
            )
        )
        
        # Add to all clinics group
        marker.add_to(all_clinics)
        
        # Add to Ponseti clinics group if applicable
        if is_ponseti:
            marker_ponseti = folium.Marker(
                location=[row['clinic_lat'], row['clinic_lon']],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(
                    color='green',
                    icon='info-sign',
                    prefix='fa'
                )
            )
            marker_ponseti.add_to(ponseti_clinics)
        
        # Add coverage circle
        folium.Circle(
            location=[row['clinic_lat'], row['clinic_lon']],
            radius=max_distance_km * 1000,  # Convert km to meters
            color='green' if row['ponseti_treatment_available'] else 'red',
            fill=True,
            opacity=0.1,
            fillOpacity=0.1
        ).add_to(coverage_group)
    
    # Add patient density heatmap if requested and data is available
    if show_density and patients_df is not None and not patients_df.empty:
        try:
            # Create heatmap data with weights
            heat_data = [[row['patient_location_lat'], 
                         row['patient_location_long'], 
                         row['patient_count']] for _, row in patients_df.iterrows()]
            
            # Add heatmap layer with weights
            HeatMap(
                heat_data,
                radius=15,
                blur=10,
                max_zoom=1,
                min_opacity=0.3,
                gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}
            ).add_to(density_group)
            
            # Add markers with patient counts
            for _, row in patients_df.drop_duplicates(['patient_location_lat', 'patient_location_long']).iterrows():
                folium.CircleMarker(
                    location=[row['patient_location_lat'], row['patient_location_long']],
                    radius=5,
                    color='blue',
                    fill=True,
                    popup=f"Patients at this location: {int(row['patient_count'])}",
                    fill_color='blue',
                    fill_opacity=0.7
                ).add_to(density_group)
            
        except Exception as e:
            st.warning(f"Could not create heatmap: {str(e)}")
    
    # Add all feature groups to map
    all_clinics.add_to(m)
    ponseti_clinics.add_to(m)
    coverage_group.add_to(m)
    density_group.add_to(m)
    
    # Add layer control to top right corner
    folium.LayerControl(position='topright').add_to(m)
    
    return m

def haversine(lon1, lat1, lon2, lat2, unit='km'):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    if unit == 'km':
        r = 6371
    elif unit == 'm':
        r = 6371000
    return c * r

@st.cache_data
def get_treatment_analysis(treatment_df, selected_country):
    """Cache treatment analysis calculations"""
    if selected_country != 'All Countries':
        treatment_filtered = treatment_df[treatment_df['Country Name'] == selected_country]
    else:
        treatment_filtered = treatment_df
    
    # Calculate success rate based on completion rate
    treatment_filtered['success_rate'] = (
        treatment_filtered['number of children completed 2 years FAB'] / 
        treatment_filtered['Total new children treated']
    ).fillna(0) * 100
    
    # Calculate all the metrics at once
    success_rate = treatment_filtered.groupby('YEAR_RECORDED')['success_rate'].mean()
    age_data = treatment_filtered[['0-1 years', '1-2 years', '2-3 years', '3-4 years', 
                                 '4-5 years', '5-10 years', '10-15 years', '15+ years']].sum()
    
    effectiveness_data = pd.DataFrame({
        'Stage': ['Started Treatment', 'Completed 2 Years', 'Completed 4 Years'],
        'Count': [
            treatment_filtered['Total new children treated'].sum(),
            treatment_filtered['number of children completed 2 years FAB'].sum(),
            treatment_filtered['NUMBER_OF_CHILDREN_COMPLETED_4_YEARS_FAB'].sum()
        ]
    })
    
    coverage_rate = (treatment_filtered['Total new children treated'] / 
                    treatment_filtered['Expected number of clubfoot cases'] * 100)
    coverage_by_year = coverage_rate.groupby(treatment_filtered['YEAR_RECORDED']).mean()
    
    return success_rate, age_data, effectiveness_data, coverage_by_year

def main():
    """Main function for the Streamlit dashboard"""
    # Load data
    clinics_df, patients_df, treatment_df = load_data()
    
    # Display title and NGO information
    st.markdown("""
        <div class="title-container">
            <h1>🌍 Global Clubfoot Initiative Dashboard</h1>
        </div>
        
        <div class="ngo-info">
            <h3>About Global Clubfoot Initiative (GCI)</h3>
            <p>GCI is a non-profit organization dedicated to ending disability caused by clubfoot. Every year, 175,000 children are born with clubfoot, 
            a condition that causes one or both feet to turn inward and upward.</p>
            <p>Through the Ponseti treatment method, we help children walk, play, and live normal lives. The treatment is non-surgical, 
            cost-effective, and has a 95% success rate when properly administered.</p>
            <p><a href="https://globalclubfoot.com" target="_blank">Visit GCI Website →</a></p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar filters
    with st.sidebar:
        st.markdown("""
            <div style='animation: slideIn 1s ease-out;'>
                <h2>📊 Dashboard Controls</h2>
            </div>
        """, unsafe_allow_html=True)
        
        # Country selection
        available_countries = get_available_countries(clinics_df)
        selected_country = st.selectbox(
            "Select Country",
            ['All Countries'] + available_countries
        )
        
        # Coverage radius
        coverage_radius = st.slider(
            "Coverage Radius (km)",
            min_value=10,
            max_value=200,
            value=50,
            step=10,
            help="Radius around clinics to show potential coverage area"
        )
    
    # Filter data based on selections
    clinics_filtered = clinics_df.copy()
    if selected_country != 'All Countries':
        clinics_filtered = clinics_filtered[clinics_filtered['clinic_country'] == selected_country]
    
    # Calculate metrics
    metrics = calculate_metrics(clinics_filtered, patients_df, selected_country)
    
    # Display KPIs with animations
    kpi_cols = st.columns(4)
    
    with kpi_cols[0]:
        st.markdown("""
            <div class='metric-card' style='background-color: white; padding: 1rem; border-radius: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                <h4 style='margin: 0; color: #2c3e50;'>Total Clinics</h4>
                <p style='font-size: 24px; font-weight: bold; margin: 0.5rem 0; color: #2980b9;'>{}</p>
            </div>
        """.format(metrics['total_clinics']), unsafe_allow_html=True)
    
    with kpi_cols[1]:
        st.markdown("""
            <div class='metric-card' style='background-color: white; padding: 1rem; border-radius: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                <h4 style='margin: 0; color: #2c3e50;'>Ponseti Treatment Clinics</h4>
                <p style='font-size: 24px; font-weight: bold; margin: 0.5rem 0; color: #27ae60;'>{}</p>
            </div>
        """.format(metrics['active_ponseti_clinics']), unsafe_allow_html=True)
    
    with kpi_cols[2]:
        st.markdown("""
            <div class='metric-card' style='background-color: white; padding: 1rem; border-radius: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                <h4 style='margin: 0; color: #2c3e50;'>Ponseti Coverage Rate</h4>
                <p style='font-size: 24px; font-weight: bold; margin: 0.5rem 0; color: #8e44ad;'>{:.1f}%</p>
                <p style='margin: 0; font-size: 12px; color: #7f8c8d;'>
                    Measures the effectiveness of Ponseti treatment coverage based on:
                    <br>• Percentage of clinics offering treatment
                    <br>• Geographic distribution of clinics
                </p>
            </div>
        """.format(metrics['ponseti_rate']), unsafe_allow_html=True)
    
    with kpi_cols[3]:
        st.markdown("""
            <div class='metric-card' style='background-color: white; padding: 1rem; border-radius: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                <h4 style='margin: 0; color: #2c3e50;'>Total Patients</h4>
                <p style='font-size: 24px; font-weight: bold; margin: 0.5rem 0; color: #e67e22;'>{}</p>
            </div>
        """.format(metrics['total_patients']), unsafe_allow_html=True)
    
    # Create tabs for different analyses
    tab1, tab2 = st.tabs([
        "🗺️ Clinic Distribution",
        "📊 Coverage Analysis"
    ])
    
    with tab1:
        # Map instructions
        st.markdown("""
        <div class='map-instructions'>
            <h4 style='margin-top: 0;'>🗺️ Interactive Map Guide</h4>
            <ul>
                <li><b>Clinic Markers:</b> Green = Ponseti Treatment Available, Red = Not Available</li>
                <li><b>Coverage Areas:</b> Circles show potential service areas</li>
                <li><b>Patient Density:</b> Heat map shows concentration of patients (visible when country is selected)</li>
                <li><b>Layer Control:</b> Toggle different views using controls in top right in the map section below</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Create and display map
        if selected_country != 'All Countries':
            # Filter patients for the selected country
            patients_filtered = patients_df[patients_df['patient_country'] == selected_country].copy()
        else:
            patients_filtered = None

        m = create_coverage_map(
            clinics_filtered,
            patients_filtered,
            coverage_radius,
            selected_country != 'All Countries',  # Only show density for specific country
            selected_country
        )
        if m:
            folium_static(m, width=1200, height=600)
        else:
            st.warning("No clinics found for the selected filters.")
    
    with tab2:
        st.header("Coverage Analysis")
        
        # Existing coverage analysis code
        st.subheader("Clinic Distribution")
        
        # Distribution of clinics by country
        clinic_dist = clinics_filtered['clinic_country'].value_counts()
        fig = px.bar(
            x=clinic_dist.index,
            y=clinic_dist.values,
            title="Number of Clinics by Country",
            labels={'x': 'Country', 'y': 'Number of Clinics'},
            color_discrete_sequence=['#2980b9']  # Blue color
        )
        st.plotly_chart(fig)
        
        # Ponseti treatment availability
        st.subheader("Ponseti Treatment Availability")
        ponseti_dist = clinics_filtered['ponseti_treatment_available'].value_counts()
        fig = px.pie(
            values=ponseti_dist.values,
            names=['Available' if x == True else 'Not Available' for x in ponseti_dist.index],
            title="Ponseti Treatment Availability",
            color_discrete_sequence=['#27ae60', '#e74c3c']  # Green and Red colors
        )
        st.plotly_chart(fig)
        
        # New Treatment Analysis Section
        st.subheader("Treatment Analysis")
        
        # Get treatment analysis data
        success_rate, age_data, effectiveness_data, coverage_by_year = get_treatment_analysis(treatment_df, selected_country)
        
        # Treatment success rate over time (using completion rate as success metric)
        fig = px.line(
            x=success_rate.index,
            y=success_rate.values,
            title="Treatment Completion Rate Over Time (2 Years FAB)",
            labels={'x': 'Year', 'y': 'Completion Rate (%)', 'value': 'Rate'},
            color_discrete_sequence=['#8e44ad']  # Purple color
        )
        fig.update_traces(mode='lines+markers')
        st.plotly_chart(fig)
        
        # Age distribution of patients
        fig = px.bar(
            x=age_data.index,
            y=age_data.values,
            title="Age Distribution of Patients",
            labels={'x': 'Age Group', 'y': 'Number of Patients'},
            color_discrete_sequence=['#e67e22']  # Orange color
        )
        st.plotly_chart(fig)
        
        # Treatment effectiveness
        fig = px.bar(
            effectiveness_data,
            x='Stage',
            y='Count',
            title="Treatment Progress Stages",
            labels={'Count': 'Number of Children'},
            color_discrete_sequence=['#16a085']  # Turquoise color
        )
        st.plotly_chart(fig)
        
        # Coverage analysis
        fig = px.bar(
            x=coverage_by_year.index,
            y=coverage_by_year.values,
            title="Treatment Coverage Rate by Year",
            labels={'x': 'Year', 'y': 'Coverage Rate (%)', 'value': 'Rate'},
            color_discrete_sequence=['#c0392b']  # Dark Red color
        )
        st.plotly_chart(fig)

if __name__ == "__main__":
    main()
