import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import sys

sys.path.append("/Users/antoinerazeghi/Documents/Projects/AirLiquide/airliquide/")


import hub_clustering.params as p
import hub_clustering.utils as f


def percentage_change(old, new):
    return str(np.round((new - old) / old * 100)) + " %"

st.title("Evolution of charing station number from 2030 to 2040")

dataset = f.load_data()


col1, col2, col3 = st.columns(3)

# default
hub_size_threshold = p.HUB_SIZE_THRESHOLDS["optimistic"]
distance_threshold_default = p.DISTANCE_THRESHOLD_KM
nb_areas_per_centroid_threahold_default = p.THRESHOLD_NB_AREAS_BY_CENTROID

scenario = "optimistic"
scenario_2040 = {"2040": 0}
distance_threshold_default = 0

with col1:
    if st.button("Optimistic scenario"):
        scenario = "optimistic"
        scenario_2040 = {"2040": 0}
        distance_threshold_default = 0
with col2:
    if st.button("Moderate scenario"):
        scenario = "moderate"
        scenario_2040 = {"2040": 25_000}
        distance_threshold_default = p.DISTANCE_THRESHOLD_KM
with col3:
    if st.button("Conservative scenario"):
        scenario = "conservative"
        scenario_2040 = {"2040": 75_000}
        distance_threshold_default = p.DISTANCE_THRESHOLD_KM

dataset = f.load_data()
df_2030 = f.filter_dataset(dataset, scenario)
final_dataset, centroids_df = f.run_kmeans(
    df_2030,
)

hub_size_threshold = {}
df_2030 = f.count_centroid_by_region(centroids_df)

df_2040 = f.filter_dataset(dataset, "2040", scenario_2040)
final_dataset, centroids_df = f.run_kmeans(
    df_2040,
    threshold_km=distance_threshold_default,
)
df_2040 = f.count_centroid_by_region(centroids_df)
df_evolution = df_2030.merge(df_2040, on=["Libellé des régions", "Code région"])
df_evolution.drop("Code région", axis=1, inplace=True)
df_evolution.columns = ["Régions", "in_2030", "in_2040"]

df_evolution.sort_values(by="in_2030", ascending=False, inplace=True)
regions = df_evolution["Régions"]

col1, col2 = st.columns(2)
col1.metric("2030", df_evolution.in_2030.sum())
col2.metric(
    "2040",
    df_evolution.in_2040.sum(),
    percentage_change(df_evolution.in_2030.sum(), df_evolution.in_2040.sum()),
)



fig = go.Figure()
fig.add_trace(
    go.Bar(
        x=regions,
        y=df_evolution["in_2030"],
        name="2030",
        marker_color=px.colors.qualitative.Plotly[0],
    )
)
fig.add_trace(
    go.Bar(
        x=regions,
        y=df_evolution["in_2040"],
        name="2040",
        marker_color=px.colors.qualitative.Plotly[1],
    )
)
fig.update_layout(barmode="group", xaxis_tickangle=-45)
st.plotly_chart(fig)

