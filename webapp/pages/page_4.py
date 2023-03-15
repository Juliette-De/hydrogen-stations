import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

import sys

sys.path.append("/Users/antoinerazeghi/Documents/Projects/AirLiquide/airliquide/")

import hub_clustering.params as p
import hub_clustering.utils as f
import hub_clustering.hubstation_sizer as sizer

st.title("Location of hub charging stations")

col1, col2, col3 = st.columns(3)

scenario = "optimistic"
height = 10
replacement_rate = 15
truck_capacity = 100

with col1:
    if st.button("Optimistic scenario"):
        scenario = "optimistic"
with col2:
    if st.button("Moderate scenario"):
        scenario = "moderate"
with col3:
    if st.button("Conservative scenario"):
        scenario = "conservative"

with st.sidebar:
    height = st.slider(
        "Select average height (in meters) for a warehouse", 6, 15, value=height
    )
    replacement_rate = st.slider(
        "Select average replacement rate (in days) for a warehouse",
        7,
        25,
        value=replacement_rate,
    )
    truck_capacity = st.slider(
        "Select average truck capacity (in cubic meters) for a H2 truck",
        70,
        200,
        value=truck_capacity,
    )

dataset = f.load_data()
df = f.filter_dataset(dataset, scenario=scenario)
final_dataset, centroids_df = f.run_kmeans(df)

centroids_df.reset_index(inplace=True)
centroids_df.columns = ["centroid_id", "region", "latitude", "longitude"]
centroids_df.sort_values(by=["region", "centroid_id"])

h2_kg_demand = (
    df["Surface totale"]
    .pipe(sizer.compute_total_volume, height=height)
    .pipe(sizer.compute_daily_stock_volume_gone, replacement_rate=replacement_rate)
    .pipe(sizer.compute_daily_nb_trucks, truck_capacity=truck_capacity)
    .pipe(sizer.compute_daily_nb_h2_trucks)
    .pipe(sizer.compute_daily_h2_demand)
)


daily_trucks = (
    df["Surface totale"]
    .pipe(sizer.compute_total_volume, height=height)
    .pipe(sizer.compute_daily_stock_volume_gone, replacement_rate=replacement_rate)
    .pipe(sizer.compute_daily_nb_trucks, truck_capacity=truck_capacity)
    .pipe(sizer.compute_daily_nb_h2_trucks)
)

st.metric("Daily number of H2 trucks", daily_trucks.sum())

final_dataset["h2_kg_demand"] = h2_kg_demand

final_dataset["surface_totale"] = df["Surface totale"]


df_stations_type = final_dataset.groupby(
    ["Région d'implantation", "centroid"], as_index=False
).agg({"centroid_coord": "first", "h2_kg_demand": "sum", "surface_totale": "sum"})


df_stations_type["stations_type"] = df_stations_type["h2_kg_demand"].apply(
    sizer.stations_type
)

df_stations_type = df_stations_type[
    ["h2_kg_demand", "stations_type", "surface_totale"]
].merge(centroids_df, left_index=True, right_on="centroid_id")


df_stations_type["station_utilization_rate"] = df_stations_type.apply(
    lambda x: sizer.station_utilization_rate(x.h2_kg_demand, x.stations_type), axis=1
)

df_stations_type["plotly_station_utilization_rate"] = df_stations_type.apply(
    lambda x: sizer.plotly_station_utilization_rate(x.h2_kg_demand, x.stations_type),
    axis=1,
)

# st.dataframe(df_stations_type)

fig = sizer.visualize_station_types_on_map(df_stations_type)


stations_count = df_stations_type.stations_type.value_counts()

with col1:
    st.metric("Small stations", stations_count["small"])
with col2:
    st.metric("Medium stations", stations_count["medium"])
with col3:
    st.metric("Large stations", stations_count["large"])


st.plotly_chart(fig)

st.subheader("Repartition")
fig2 = px.histogram(
    df_stations_type.sort_values(by="stations_type", ascending=False),
    x="station_utilization_rate",
    color="stations_type",
    color_discrete_sequence=["blue", "orange", "green"],
)
st.plotly_chart(fig2)

st.subheader("CDF")
fig3 = px.ecdf(
    df_stations_type.sort_values(by="stations_type", ascending=False),
    x="station_utilization_rate",
    color="stations_type",
    color_discrete_sequence=["blue", "orange", "green"],
)
st.plotly_chart(fig3)
