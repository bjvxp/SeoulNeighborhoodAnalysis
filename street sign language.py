import streamlit as st
import pandas as pd
import pydeck as pdk

# Force the dark-mode aesthetic
st.set_page_config(page_title="Urban Typography Ethnography", layout="wide")

@st.cache_data
def load_data():
    # Using the relative path for Streamlit Community Cloud
    df = pd.read_csv("metadata/spatial_typography_master.csv")
    df = df.dropna(subset=['latitude', 'longitude'])
    return df

df_master = load_data()

st.title("🏙️ Urban Typography: Seoul vs. Jeju")
st.markdown("A visual ethnography dashboard measuring curb complexity and typographic density for logistics routing.")

sidebar = st.sidebar
sidebar.header("Spatial Filters")

# 1. Multi-Select Feature
all_neighborhoods = list(df_master['neighborhood'].unique())
selected_neighborhoods = sidebar.multiselect(
    "Select Zones to Compare", 
    all_neighborhoods, 
    default=all_neighborhoods  # Defaults to showing everything
)

if not selected_neighborhoods:
    st.warning("Please select at least one neighborhood from the sidebar.")
    st.stop()

df_filtered = df_master[df_master['neighborhood'].isin(selected_neighborhoods)].copy()

# Assign RGBA colors based on the regex classification
def get_color(lang):
    if lang == 'Hangul': return [50, 168, 82, 200]    # Green
    elif lang == 'English': return [66, 135, 245, 200]  # Blue
    elif lang == 'Mixed': return [235, 143, 52, 200]    # Orange
    return [100, 100, 100, 150]                         # Grey for No_Text

df_filtered['color'] = df_filtered['frame_language'].apply(get_color)

# 2. Add the Color Legend to the Sidebar
sidebar.markdown("### Language Legend")
sidebar.markdown("")