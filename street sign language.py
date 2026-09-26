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

# --- 3. MAP LAYERS ---
layer = pdk.Layer(
    "ColumnLayer",
    data=df_filtered,  # INTEGRATION POINT 2: The layer now reads from the filtered data, not the master data
    get_position=["longitude", "latitude"],
    get_elevation="sign_count",
    elevation_scale=15,
    radius=30,
    get_fill_color="color",
    pickable=True,
    auto_highlight=True,
)

# INTEGRATION POINT 3: PyDeck automatically calculates the bounding box and zoom level based on the remaining points
view_state = pdk.data_utils.compute_view(df_filtered[["longitude", "latitude"]])
view_state.pitch = 45 

# INTEGRATION POINT 4: The view_state and layer are injected into the final map render
r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style="dark",
    tooltip={
        "text": "Zone: {neighborhood}\nLanguage: {frame_language}\nSigns: {sign_count}\nText: {combined_text}"
    }
)

st.pydeck_chart(r)

# --- 4. DYNAMIC METRICS ---
col1, col2, col3 = st.columns(3)
# INTEGRATION POINT 5: The bottom metrics also update dynamically based on the filtered data
col1.metric("Total Spatial Points", len(df_filtered))
col2.metric("Peak Curb Complexity", df_filtered['sign_count'].max())
col3.metric("Zero-Text Routes", len(df_filtered[df_filtered['sign_count'] == 0]))
