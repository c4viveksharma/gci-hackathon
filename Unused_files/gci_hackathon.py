import pandas as pd
import streamlit as st
import pydeck as pdk
import geopandas as gpd
from shapely.geometry import Polygon

# Streamlit App Setup
st.set_page_config(page_title="Clinic Map Visualization", layout="wide")
st.title("🌍 🏥 Enhanced Clinic Location Visualization")

# File Paths (Update with your file paths)
clinic_file_path = 'C:/GCI_Hackathon/Location Data/cleaned_Clinic_Locations.csv'
# country_shapefile_path = 'C:/GCI_Hackathon/Location Data/countries_shapefile.shp'  # Shapefile for country boundaries

# Load Data
clinic_df = pd.read_csv(clinic_file_path)
# country_gdf = gpd.read_file(country_shapefile_path)

# Filter Clinics with Coordinates
clinic_df = clinic_df.dropna(subset=['clinic_lat', 'clinic_lon'])

# Sidebar Filters
all_countries = clinic_df['clinic_country'].unique().tolist()
all_countries.sort()
selected_country = st.sidebar.selectbox(
    "Select a Country:", 
    options=[None] + all_countries, 
    format_func=lambda x: "Select a Country" if x is None else x
)

# Filter Data by Selected Country
if selected_country:
    filtered_clinic_df = clinic_df[clinic_df['clinic_country'] == selected_country]
    country_geom = None
    st.write(f"Displaying clinics and boundary for **{selected_country}**")
else:
    filtered_clinic_df = clinic_df
    country_geom = None
    st.write("Displaying all clinics")

# Display Data in Table
st.write("Clinic Data Preview:")
st.dataframe(filtered_clinic_df)

# Visualization
if not filtered_clinic_df.empty:
    # Scatterplot Layer for Clinics
    clinic_layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_clinic_df,
        get_position=["clinic_lon", "clinic_lat"],
        get_radius=8000,  # Radius in meters
        get_fill_color=[255, 0, 0, 200],  # Red semi-transparent bubbles
        pickable=True,
    )
    
    layers = [clinic_layer]

    # Highlight Country Boundary if a Country is Selected
    if selected_country and not country_geom.empty:
        # Extract country boundary as a list of polygons
        polygons = [
            [[lng, lat] for lng, lat in geom.exterior.coords]
            for geom in country_geom['geometry']
            if isinstance(geom, Polygon)
        ]
        
        country_layer = pdk.Layer(
            "PolygonLayer",
            data=[{"polygon": polygon} for polygon in polygons],
            get_polygon="polygon",
            get_fill_color="[0, 0, 255, 50]",  # Semi-transparent blue fill
            get_line_color=[0, 0, 255],  # Blue border
            line_width_min_pixels=2,
            pickable=False,
        )
        layers.append(country_layer)

    # Set View State
    if selected_country and not filtered_clinic_df.empty:
        initial_view_state = pdk.ViewState(
            latitude=filtered_clinic_df["clinic_lat"].mean(),
            longitude=filtered_clinic_df["clinic_lon"].mean(),
            zoom=6,
            pitch=50,
        )
    else:
        initial_view_state = pdk.ViewState(
            latitude=0,
            longitude=0,
            zoom=2,
            pitch=0,
        )

    # Mapbox Style
    map_style = "mapbox://styles/mapbox/outdoors-v11"

    # Render Map
    st.pydeck_chart(
        pdk.Deck(
            map_style=map_style,
            initial_view_state=initial_view_state,
            layers=layers,
        )
    )
else:
    st.warning("No clinic data available for the selected country.")
