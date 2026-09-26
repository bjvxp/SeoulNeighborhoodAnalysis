import streamlit as st
import pandas as pd
import pydeck as pdk

# Force the dark-mode aesthetic
st.set_page_config(page_title="Urban Typography & Environmental Ethnography", layout="wide")

@st.cache_data
def load_data():
    # Load the newly minted multi-modal master dataset
    df = pd.read_csv("metadata/master_multimodal_dataset.csv")
    df = df.dropna(subset=['latitude', 'longitude'])
    return df

df_master = load_data()

st.title("🏙️ Multi-Modal Urban Ethnography: Seoul vs. Jeju")
st.markdown("Analyzing urban typography, curb complexity, and environmental ratios for logistics and spatial planning.")

sidebar = st.sidebar
sidebar.header("Spatial & Metric Controls")

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

df_filtered = df_master[df_master['neighborhood'].isin(selected_neighborhoods)].copy()

# --- 2. METRIC TOGGLE ---
metric_view = sidebar.selectbox(
    "Select Map Visualization Metric",
    [
        "Typology: Sign Count (Curb Complexity)", 
        "Environment: Green-Space Ratio", 
        "Environment: Blue-Space Ratio (Water/Ocean)", 
        "Environment: Grey-Space Ratio (Infrastructure)"
    ]
)

# Configure column mapping based on selection
if "Sign Count" in metric_view:
    elevation_col = "sign_count"
    elevation_scale = 15
    color_series = df_filtered['frame_language'].apply(lambda lang: 
        [50, 168, 82, 200] if lang == 'Hangul' else 
        ([66, 135, 245, 200] if lang == 'English' else 
        ([235, 143, 52, 200] if lang == 'Mixed' else [100, 100, 100, 150]))
    )
    legend_title = "Language Legend"
    legend_html = (
        "