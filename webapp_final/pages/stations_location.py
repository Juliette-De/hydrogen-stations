import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

import sys

sys.path.append("/Users/antoinerazeghi/Documents/Projects/AirLiquide/airliquide/")


import hub_clustering.params as p
import hub_clustering.utils as f
import hub_clustering.hubstation_sizer as sizer


import hub_clustering.streamlit_function as l

st.header("Stations location to meet 100% of demand")


# Setting default values
scenario = "count_moderate"
height = 6
replacement_rate = 15
truck_capacity = 100

# Converting scenario strings to index
scenario_indexes = {"count_optimistic": 0, "count_moderate": 1, "count_conservative": 2}

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Optimistic Scenario"):
        scenario = "count_optimistic"
with col2:
    if st.button("Moderate Scenario"):
        scenario = "count_moderate"
with col3:
    if st.button("Conservative Scenario"):
        scenario = "count_conservative"

col1, col2 = st.columns(2)
year = "2030"  # Setting default
with col1:
    if st.button("2030"):
        year = "2030"
with col2:
    if st.button("2040"):
        year = "2040"

with st.sidebar:
    height = st.slider(
        "Select average height (in meters) for a warehouse", 5, 15, value=height
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


# Loading Road Stations data
road_data = l.load_and_prepare_location()

frequency, affluence = p.ROAD_HUB_THRESHOLDS[year][scenario_indexes[scenario]]
_, road_stations = l.intermediateStations(road_data, frequency, affluence)
road_stations = road_stations[road_stations.is_stationable == 1]

number_of_trucks = p.NUMBER_OF_TRUCKS[year]
hydrogene_kg_served_by_hubs = p.HYDROGENE_SERVED_BY_HUBS[year]
road_profitability = l.get_profitability_info(
    road_stations, number_of_trucks, hydrogene_kg_served_by_hubs
)

to_map_roads = pd.merge(road_stations, road_profitability, on="route", how="left")
to_map_roads.rename({"latD": "latitude", "lonD": "longitude"}, axis=1, inplace=True)


# Loading Hub Stations data

hub_data = f.load_data()
df = f.filter_dataset(hub_data, scenario=scenario[6:], year=year)
final_dataset, centroids_df = f.run_kmeans(df, scenario=scenario[6:], year=year)

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


# Merging both datasets
df_stations_type.rename({"stations_type": "size_station"}, axis=1, inplace=True)
hubs_to_plot = df_stations_type[["latitude", "longitude", "size_station"]]
hubs_to_plot["type"] = "hub"

roads_to_plot = to_map_roads[["latitude", "longitude", "size_station"]]
roads_to_plot["type"] = "road"

df_to_plot = pd.concat([hubs_to_plot, roads_to_plot])


# Mapping

st.subheader("Stations according to type (hubs vs roads)")
col1, col2 = st.columns(2)
col1.metric("Hub stations", df_to_plot[df_to_plot.type == "hub"].shape[0])
col2.metric("Road stations", df_to_plot[df_to_plot.type == "road"].shape[0])
st.plotly_chart(f.visualize_on_map_contrast(df_to_plot))


# Mapping

st.subheader("Stations according to size (small, medium, large)")
col1, col2, col3 = st.columns(3)
col1.metric("Small stations", df_to_plot[df_to_plot.size_station == "small"].shape[0])
col2.metric("Medium stations", df_to_plot[df_to_plot.size_station == "medium"].shape[0])
col3.metric("Large stations", df_to_plot[df_to_plot.size_station == "large"].shape[0])
st.plotly_chart(f.visualize_on_map_contrast(df_to_plot, contrast="size"))

