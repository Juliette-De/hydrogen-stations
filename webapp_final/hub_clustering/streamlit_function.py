import pandas as pd
import folium
import numpy as np
import streamlit as st
from math import inf
import sys

import hub_clustering.params as p


@st.cache_data
def load_and_prepare():
    df = pd.read_csv("df_clean.csv")
    region_dep = pd.read_csv("departements-region.csv", sep=";")

    df["truck_traffic"] = df["TMJA"] * df["ratioPL"] / 100
    df["depPrD"] = df["depPrD"].astype(str)
    df = df.merge(
        region_dep[["num_dep", "region_name"]],
        right_on="num_dep",
        left_on="depPrD",
        how="left",
    )

    df_by_region_and_road = (
        df.groupby(["route", "region_name"])["truck_traffic"].mean().reset_index()
    )
    df = df.merge(df_by_region_and_road, how="left", on=["region_name", "route"])
    df.rename(
        columns={
            "truck_traffic_y": "truck_traffic_region",
            "truck_traffic_x": "truck_traffic_segment",
        },
        inplace=True,
    )

    df["avg_traffic_bin"] = pd.cut(
        df["truck_traffic_segment"], 5, labels=[1, 5, 10, 15, 20]
    )

    df["longueur"] = df["longueur"].str.replace(",", ".").astype(float)
    df_len = df.groupby("route")["longueur"].sum().reset_index()
    df = df.merge(df_len, how="left", on="route")
    df.rename(
        columns={"longueur_x": "longueur", "longueur_y": "longueur_route"}, inplace=True
    )
    return df

@st.cache_data
def load_and_prepare_location():
    df = pd.read_csv("hub_clustering/df_clean.csv")
    region_dep = pd.read_csv("hub_clustering/departements-region.csv", sep=";")

    df["truck_traffic"] = df["TMJA"] * df["ratioPL"] / 100
    df["depPrD"] = df["depPrD"].astype(str)
    df = df.merge(
        region_dep[["num_dep", "region_name"]],
        right_on="num_dep",
        left_on="depPrD",
        how="left",
    )

    df_by_region_and_road = df.groupby(["route"])["truck_traffic"].mean().reset_index()
    df = df.merge(df_by_region_and_road, how="left", on=["route"])
    df.rename(
        columns={
            "truck_traffic_y": "truck_traffic_road",
            "truck_traffic_x": "truck_traffic_segment",
        },
        inplace=True,
    )

    df["avg_traffic_bin"] = pd.cut(
        df["truck_traffic_segment"], 5, labels=[1, 5, 10, 15, 20]
    )

    df["longueur"] = df["longueur"].str.replace(",", ".").astype(float)
    df_len = df.groupby("route")["longueur"].sum().reset_index()
    df = df.merge(df_len, how="left", on="route")
    df.rename(
        columns={"longueur_x": "longueur", "longueur_y": "longueur_route"}, inplace=True
    )
    return df


def color():
    # generate a random list of n hexadecimal colors
    n = 1000
    colors = [
        "#" + "".join([np.random.choice(list("0123456789ABCDEF")) for j in range(6)])
        for i in range(n)
    ]
    return colors


def intermediateStations_region(df, year="2030"):
    options = p.ROAD_HUB_THRESHOLDS[year]
    l = []
    for option in options:
        frequency = option[0]
        affluence = option[1]
        seuil_frequentation_quantile = np.quantile(
            df["truck_traffic_segment"], affluence
        )
        df_grandes_routes = df[
            (df["longueur_route"] >= frequency * 1000)
            & (df["truck_traffic_segment"] >= seuil_frequentation_quantile)
        ].reset_index()
        df_grandes_routes["longueur_cumul"] = df_grandes_routes.groupby(["route"])[
            "longueur"
        ].cumsum()

        df_idx = pd.DataFrame()
        df_grandes_routes["index"] = df_grandes_routes.index
        for k in range(
            round(max(df_grandes_routes.longueur_cumul) / (int(frequency) * 1000))
        ):
            milestone = k * frequency * 1000
            temp = pd.DataFrame(
                df_grandes_routes[df_grandes_routes["longueur_cumul"] <= milestone]
                .groupby("route")["index"]
                .max()
            ).reset_index(drop=True)
            df_idx = pd.concat([df_idx, temp], axis=0).drop_duplicates()

        df_idx = df_idx.reset_index(drop=True)

        df_idx["is_stationable"] = 1

        df_grandes_routes = df_grandes_routes.merge(df_idx, how="left", on="index")

        df_grandes_routes = (
            df_grandes_routes.groupby("region_name")["is_stationable"]
            .sum()
            .reset_index()
        )

        l.append(df_grandes_routes)
    return l


def intermediateStations(df, frequency, affluence):
    seuil_frequentation_quantile = np.quantile(df["truck_traffic_segment"], affluence)
    df_grandes_routes = df[
        (df["longueur_route"] >= frequency * 1000)
        & (df["truck_traffic_segment"] >= seuil_frequentation_quantile)
    ].reset_index()
    df_grandes_routes["longueur_cumul"] = df_grandes_routes.groupby(["route"])[
        "longueur"
    ].cumsum()

    df_idx = pd.DataFrame()
    df_grandes_routes["index"] = df_grandes_routes.index

    for k in range(
        round(max(df_grandes_routes.longueur_cumul) / (int(frequency) * 1000))
    ):
        milestone = k * frequency * 1000
        temp = pd.DataFrame(
            df_grandes_routes[df_grandes_routes["longueur_cumul"] <= milestone]
            .groupby("route")["index"]
            .max()
        ).reset_index(drop=True)
        df_idx = pd.concat([df_idx, temp], axis=0).drop_duplicates()

    df_idx = df_idx.reset_index(drop=True)

    df_idx["is_stationable"] = 1

    df_grandes_routes = df_grandes_routes.merge(df_idx, how="left", on="index")

    colors = color()

    map_center = [46.2276, 2.2137]
    m = folium.Map(zoom_start=5.4, location=map_center)
    j = 0
    for route in list(df.route.unique()):
        for i, row in df[df["route"] == route].iterrows():
            folium.PolyLine(
                locations=[[row["latD"], row["lonD"]], [row["latF"], row["lonF"]]],
                color=colors[j],
                tooltip=row["route"],
                weight=row["avg_traffic_bin"],
            ).add_to(m)
        j += 1

    for i, row in df_grandes_routes[
        df_grandes_routes["is_stationable"] == 1
    ].iterrows():
        folium.Marker(
            location=[row["latF"], row["lonF"]], color="red", radius=4
        ).add_to(m)

    return m, df_grandes_routes


def globalTraffic(df):
    colors = color()

    # create a folium map centered on the US
    map_center = [46.2276, 2.2137]
    m = folium.Map(zoom_start=5.4, location=map_center)

    # add markers for starting and ending positions

    j = 0
    for route in list(df.route.unique()):
        for i, row in df[df["route"] == route].iterrows():
            folium.PolyLine(
                locations=[[row["latD"], row["lonD"]], [row["latF"], row["lonF"]]],
                color=colors[j],
                tooltip=row["route"],
                weight=row["avg_traffic_bin"],
            ).add_to(m)

        j += 1

    return m


def aggregate_road_stations(df: pd.DataFrame, year: str = "2030") -> pd.DataFrame:
    to_df = intermediateStations_region(df, year)
    to_df[0].columns, to_df[1].columns, to_df[2].columns = (
        ["region_name", "count_optimistic"],
        ["region_name", "count_moderate"],
        ["region_name", "count_conservative"],
    )
    final = pd.DataFrame(to_df[0])

    for scenario in range(1, len(to_df)):
        final = final.merge(to_df[scenario])

    return final.sort_values(by="region_name").set_index("region_name")


def return_total_h2(
    consommation_moyenne, nb_camions_par_jour, distance_moyenne_parcourue_par_jour
):
    # Ex: 10kg/100km * 10 000 * 800km =>
    return (
        consommation_moyenne
        * nb_camions_par_jour
        * distance_moyenne_parcourue_par_jour
        / 100
    )


# create function to calculate profitability threshold based on size
def calc_profit_threshold(row):
    threshold = {"small": 1_000, "medium": 2_000, "large": 4_000}
    return row["total_h2_sold_per_station"] / threshold[row["size_station"]]


def categorize_profitability(row):
    threshold = {"small": 0.9, "medium": 0.8, "large": 0.7}
    return (
        "saturated"
        if row["profitability threshold"] > 1
        else "non profitable"
        if row["profitability threshold"] < threshold[row["size_station"]]
        else "profitable"
    )


def get_profitability_info(df, number_of_trucks, hydrogene_kg_served_by_hubs):
    temp = (
        df.groupby("route")
        .agg({"truck_traffic_road": "mean", "is_stationable": "sum"})
        .reset_index()
    )
    temp["percentage_truck_traffic_road"] = (
        temp["truck_traffic_road"] / temp["truck_traffic_road"].sum()
    )
    temp["total_h2_sold"] = temp["percentage_truck_traffic_road"] * (
        return_total_h2(10, number_of_trucks, 120) - hydrogene_kg_served_by_hubs
    )
    temp["total_h2_sold_per_station"] = temp["total_h2_sold"] / temp["is_stationable"]

    bins = [0, 1000, 2000, inf]
    labels = ["small", "medium", "large"]
    temp["size_station"] = pd.cut(
        temp["total_h2_sold_per_station"], bins=bins, labels=labels
    )

    temp["profitability threshold"] = temp.apply(calc_profit_threshold, axis=1)
    temp["profitable"] = temp.apply(categorize_profitability, axis=1)
    return temp
