import streamlit as st
import pandas as pd
import pydeck as pdk

# Force the dark-mode aesthetic
st.set_page_config(page_title="Multi-Modal Urban Ethnography", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("metadata/master_multimodal_dataset.csv")
    df = df.dropna(subset=['latitude', 'longitude'])
    return df

df_master = load_data()

st.title("🏙️ Multi-Modal Urban Ethnography: Seoul vs. Jeju")
st.markdown("Comparing hyper-dense commercial typography against natural coastal and vegetative landscapes for spatial planning.")

# --- GLOBAL SIDEBAR CONTROLS ---
sidebar = st.sidebar
sidebar.header("Global Spatial Filters")

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

# --- STREAMLIT TABS ARCHITECTURE ---
tab1, tab2 = st.tabs([
    "🏙️ Urban Typography & Curb Complexity", 
    "🌿 Environmental Segmentation (Green / Blue / Grey)"
])

# ==========================================
# TAB 1: TYPOGRAPHY & LANGUAGE DENSITY
# ==========================================
with tab1:
    st.subheader("Linguistic Signage & Curb Complexity")
    st.markdown("Examines the ratio of Hangul, English, and Mixed signage across urban grids (Seoul vs. Jeju City).")

    # Colors for languages
    def get_lang_color(lang):
        if lang == 'Hangul': return [50, 168, 82, 200]
        elif lang == 'English': return [66, 135, 245, 200]
        elif lang == 'Mixed': return [235, 143, 52, 200]
        return [100, 100, 100, 150]

    df_filtered['lang_color'] = df_filtered['frame_language'].apply(get_lang_color)

    layer_tab1 = pdk.Layer(
        "ColumnLayer",
        data=df_filtered,
        get_position=["longitude", "latitude"],
        get_elevation="sign_count",
        elevation_scale=15,
        radius=30,
        get_fill_color="lang_color",
        pickable=True,
        auto_highlight=True,
    )

    view_state_tab1 = pdk.data_utils.compute_view(df_filtered[["longitude", "latitude"]])
    view_state_tab1.pitch = 45 

    r_tab1 = pdk.Deck(
        layers=[layer_tab1],
        initial_view_state=view_state_tab1,
        map_style="dark",
        tooltip={"text": "Zone: {neighborhood}\nLanguage: {frame_language}\nSigns: {sign_count}\nText: {combined_text}"}
    )
    st.pydeck_chart(r_tab1)

    # Tab 1 Legend & Metrics
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("**Language Legend**")
        st.markdown("")

# Local selector for the environmental view
env_metric = st.selectbox(
    "Select Environmental Layer",
    ["Green-Space (Vegetation & Parks)", "Blue-Space (Ocean & Coastlines)", "Grey-Space (Asphalt & Buildings)"]
)

if "Green-Space" in env_metric:
    env_col = "green_space_ratio"
    env_color = lambda r: [34, 139, 34, int(100 + 155 * r)]
    env_desc = "Extrusion scales with tree and park foliage density."
elif "Blue-Space" in env_metric:
    env_col = "blue_space_ratio"
    env_color = lambda r: [0, 119, 182, int(100 + 155 * r)]
    env_desc = "Extrusion scales with ocean and coastal water density (Jeju/Jungmun)."
else:
    env_col = "grey_space_ratio"
    env_color = lambda r: [128, 128, 128, int(100 + 155 * r)]
    env_desc = "Extrusion scales with concrete, asphalt, and building density (Seoul Core)."

df_filtered['env_color'] = df_filtered[env_col].apply(env_color)

layer_tab2 = pdk.Layer(
    "ColumnLayer",
    data=df_filtered,
    get_position=["longitude", "latitude"],
    get_elevation=env_col,
    elevation_scale=400, # Scaled up since ratios are fractions
    radius=30,
    get_fill_color="env_color",
    pickable=True,
    auto_highlight=True,
)

view_state_tab2 = pdk.data_utils.compute_view(df_filtered[["longitude", "latitude"]])
view_state_tab2.pitch = 45 

r_tab2 = pdk.Deck(
    layers=[layer_tab2],
    initial_view_state=view_state_tab2,
    map_style="dark",
    tooltip={
        "text": "Zone: {neighborhood}\nGreen Ratio: {green_space_ratio}\nBlue Ratio: {blue_space_ratio}\nGrey Ratio: {grey_space_ratio}"
    }
)
st.pydeck_chart(r_tab2)
st.caption(env_desc)

# Tab 2 Summary Ratios
e1, e2, e3 = st.columns(3)
e1.metric("Avg Green-Space", f"{df_filtered['green_space_ratio'].mean():.2%}")
e2.metric("Avg Blue-Space", f"{df_filtered['blue_space_ratio'].mean():.2%}")
e3.metric("Avg Grey-Space", f"{df_filtered['grey_space_ratio'].mean():.2%}")