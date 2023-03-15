import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

import sys

sys.path.append("/Users/antoinerazeghi/Documents/Projects/AirLiquide/airliquide/")


import hub_clustering.params as p
import hub_clustering.utils as f

# st.header("Locating charging stations according to hubs")

dataset = f.load_data()

st.title("Scenario-creation pannel")


col1, col2, col3 = st.columns(3)

# default
hub_size_threshold = p.HUB_SIZE_THRESHOLDS["optimistic"]
distance_threshold_default = p.DISTANCE_THRESHOLD_KM
nb_areas_per_centroid_threshold_default = p.THRESHOLD_NB_AREAS_BY_CENTROID

with col1:
    if st.button("Optimistic scenario"):
        hub_size_threshold = p.HUB_SIZE_THRESHOLDS["optimistic"]
        distance_threshold_default = p.DISTANCE_THRESHOLD_KM
        nb_areas_per_centroid_threshold_default = p.THRESHOLD_NB_AREAS_BY_CENTROID
with col2:
    if st.button("Moderate scenario"):
        hub_size_threshold = p.HUB_SIZE_THRESHOLDS["moderate"]
        distance_threshold_default = p.DISTANCE_THRESHOLD_KM
        nb_areas_per_centroid_threshold_default = p.THRESHOLD_NB_AREAS_BY_CENTROID
with col3:
    if st.button("Conservative scenario"):
        hub_size_threshold = p.HUB_SIZE_THRESHOLDS["conservative"]
        distance_threshold_default = p.DISTANCE_THRESHOLD_KM
        nb_areas_per_centroid_threshold_default = p.THRESHOLD_NB_AREAS_BY_CENTROID


with st.sidebar:
    hub_size_threshold = st.slider(
        "Select a hub size threshold", 0, 200_000, value=hub_size_threshold
    )
    distance_threshold = st.slider(
        "Select a distance threshold", 0, 40, value=distance_threshold_default
    )
    nb_areas_per_centroid_threahold = st.slider(
        "Number of hubs per stations",
        0,
        10,
        value=nb_areas_per_centroid_threshold_default,
    )

custum_hub_size = {"custom": hub_size_threshold}


dataset = f.load_data()
df = f.filter_dataset(dataset, "custom", custum_hub_size)
final_dataset, centroids_df = f.run_kmeans(
    df,
    threshold_km=distance_threshold_default,
    threshold_nb_areas_by_centroid=nb_areas_per_centroid_threshold_default,
)
df = f.count_centroid_by_region(centroids_df)

df.sort_values(by="count", ascending=False, inplace=True)
fig = go.Figure()
fig.add_trace(
    go.Bar(
        x=df["Libellé des régions"],
        y=df["count"],
        name="Custom",
        marker_color=px.colors.qualitative.Plotly[0],
    )
)
st.plotly_chart(fig)

st.write(f'Total number of stations: {df["count"].sum()}')

st.subheader("Map")

fig2 = f.visualize_on_map(final_dataset, centroids_df)
st.plotly_chart(fig2)
