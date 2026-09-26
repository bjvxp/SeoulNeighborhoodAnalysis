import streamlit as st
import pandas as pd
import pydeck as pdk

# Force the dark-mode aesthetic
st.set_page_config(page_title="Urban Typography Ethnography", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("E:/street_imagery_project/metadata/spatial_typography_master.csv")
    df = df.dropna(subset=['latitude', 'longitude'])
    return df

df_master = load_data()

st.title("🏙️ Urban Typography: Seoul vs. Jeju")
st.markdown("A visual ethnography dashboard measuring curb complexity and typographic density for logistics routing.")

sidebar = st.sidebar
sidebar.header("Spatial Filters")
selected_neighborhood = sidebar.selectbox("Select Zone", ["All"] + list(df_master['neighborhood'].unique()))

if selected_neighborhood != "All":
    df_filtered = df_master[df_master['neighborhood'] == selected_neighborhood]
else:
    df_filtered = df_master

# Assign RGBA colors based on the regex classification
def get_color(lang):
    if lang == 'Hangul': return [50, 168, 82, 200]    # Green
    elif lang == 'English': return [66, 135, 245, 200]  # Blue
    elif lang == 'Mixed': return [235, 143, 52, 200]    # Orange
    return [100, 100, 100, 150]                         # Grey for No_Text

df_filtered['color'] = df_filtered['frame_language'].apply(get_color)

# 3D Elevation Layer
layer = pdk.Layer(
    "ColumnLayer",
    data=df_filtered,
    get_position=["longitude", "latitude"],
    get_elevation="sign_count",
    elevation_scale=15,
    radius=30,
    get_fill_color="color",
    pickable=True,
    auto_highlight=True,
)

view_state = pdk.ViewState(
    latitude=df_filtered['latitude'].mean(),
    longitude=df_filtered['longitude'].mean(),
    zoom=11.5,
    pitch=45,
)

# Render the PyDeck map with the dark basemap
r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style="dark",
    tooltip={
        "text": "Zone: {neighborhood}\nLanguage: {frame_language}\nSigns: {sign_count}\nText: {combined_text}"
    }
)

st.pydeck_chart(r)

# Summary Operations Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Spatial Points", len(df_filtered))
col2.metric("Peak Curb Complexity", df_filtered['sign_count'].max())
col3.metric("Zero-Text Routes", len(df_filtered[df_filtered['sign_count'] == 0]))