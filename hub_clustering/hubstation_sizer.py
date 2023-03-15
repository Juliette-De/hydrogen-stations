import numpy as np
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go


def compute_total_volume(surface: float, height: float = 8) -> float:
    """
    Computes the total volume of a hub based on its surface and a height parameters
    """
    return surface * height


def compute_daily_stock_volume_gone(
    tot_volume: float, replacement_rate: float = 15
) -> float:
    """
    Computes for a given hub, the daily volume of its stock that is transported away by trucks
    """
    return tot_volume * (1/replacement_rate)


def compute_daily_nb_trucks(daily_volume: float, truck_capacity: float = 100) -> int:
    """
    Computes the daily number of trucks needed to transport a given volume of stock out of a hub
    """
    return np.ceil(daily_volume / truck_capacity)


def compute_daily_nb_h2_trucks(
    daily_nb_trucks: int, nb_h2_trucks: int = 10_000, nb_trucks: int = 300_000
) -> int:
    """
    Computes the number of daily H2 trucks needed to transport a given volume of stock out of a hub
    """
    return np.round(daily_nb_trucks * (nb_h2_trucks / nb_trucks), 0)


def compute_daily_h2_demand(
    daily_nb_h2_trucks: int,
    tank_volume: int = 32,
    percentage_of_trucks_refilling: float = 0.8,
    avg_tank_refilling_percentage: float = 0.7,
) -> float:
    """
    Computes the number of H2 kg needed in a warehouse per day
    """
    return (
        daily_nb_h2_trucks
        * tank_volume
        * percentage_of_trucks_refilling
        * avg_tank_refilling_percentage
    )


def stations_type(h2_kg_demand: float) -> str:
    """
    Stations type (small, medium or large) required to satisfy the daily demand
    """
    return (
        "small"
        if h2_kg_demand < 1_000
        else "medium"
        if h2_kg_demand < 2_000
        else "large"
    )


def station_utilization_rate(h2_kg_demand: float, stations_type: str) -> float:
    capacity_max = {"small": 1000, "medium": 2000, "large": 4000}
    return np.round((h2_kg_demand / capacity_max[stations_type] * 100), 2)


def plotly_station_utilization_rate(h2_kg_demand: float, stations_type: str) -> float:
    return (
        "Util. rate = "
        + str(station_utilization_rate(h2_kg_demand, stations_type))
        + "%"
    )





def visualize_station_types_on_map(df_stations_type):

    fig = px.scatter_mapbox(
        df_stations_type,
        lat=df_stations_type["latitude"].astype(float),
        lon=df_stations_type["longitude"].astype(float),
        zoom=5,
        height=800,
        width=650,
        hover_name="plotly_station_utilization_rate",
    )

    fig.update_traces(
        marker_color=df_stations_type.stations_type.map(
            {"small": "blue", "medium": "green", "large": "orange"}
        ),
        marker_size=df_stations_type.stations_type.map(
            {"small": 6, "medium": 12, "large": 18}
        ),
    )

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig
