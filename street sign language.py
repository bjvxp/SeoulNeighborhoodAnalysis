import streamlit as st
import pandas as pd
import pydeck as pdk

# Force the dark-mode aesthetic
st.set_page_config(page_title="Urban Typography Ethnography", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("metadata/spatial_typography_master.csv")
    df = df.dropna(subset=['latitude', 'longitude'])
    return df

df_master = load_data()

st.title("🏙️ Urban Typography: Seoul vs. Jeju")
st.markdown("A visual ethnography dashboard measuring curb complexity and typographic density for logistics routing.")

sidebar = st.sidebar
sidebar.header("Spatial Filters")

# --- 1. SIDEBAR CONTROLS ---
all_neighborhoods = list(df_master['neighborhood'].unique())
selected_neighborhoods = sidebar.multiselect(
    "Select Zones to Compare", 
    all_neighborhoods, 
    default=all_neighborhoods
)

if not selected_neighborhoods:
    st.warning("Please select at least one neighborhood from the sidebar.")
    st.stop()

# INTEGRATION POINT 1: We create a new dataframe containing only the selected neighborhoods
df_filtered = df_master[df_master['neighborhood'].isin(selected_neighborhoods)].copy()

# --- 2. COLOR LEGEND ---
def get_color(lang):
    if lang == 'Hangul': return [50, 168, 82, 200]
    elif lang == 'English': return [66, 135, 245, 200]
    elif lang == 'Mixed': return [235, 143, 52, 200]
    return [100, 100, 100, 150]

df_filtered['color'] = df_filtered['frame_language'].apply(get_color)

sidebar.markdown("### Language Legend")
legend_html = ("")