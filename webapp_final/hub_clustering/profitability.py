import pandas as pd
import plotly.express as px
import numpy as np


def load_profitable_data(year: str = "2030"):
    return pd.read_csv(f"data_final/{year}_profitable.csv", index_col=0)


def load_all_data(year: str = "2030"):
    return pd.read_csv(f"data_final/{year}.csv", index_col=0)


def load_and_clean(year="2030"):
    cutoff = {"2030": 30, "2040": 160}
    df = load_all_data(year).sort_values(
        by=["prioritize", "total_h2_sold_per_station"], ascending=False
    )
    df["cumulative_demand"] = compute_pareto(df.total_h2_sold_per_station)
    df.reset_index(inplace=True, drop=True)
    return df.iloc[: cutoff[year], :]


def compute_pareto(h2):
    return h2.cumsum() / h2.sum(), h2.sum()


def load_and_clean(year="2030"):
    df = load_all_data(year).sort_values(
        by=["prioritize", "total_h2_sold_per_station"], ascending=False
    )
    df["cumulative_demand"], total_demand = compute_pareto(df.total_h2_sold_per_station)
    df.reset_index(inplace=True, drop=True)
    return df, total_demand


def add_construction_year(df, construction_rate: int = 5, scenario="monopoly"):
    start_year = {5: 2024, 13: 2030, 3:2030}
    scenario_factor = {"monopoly": 1, "oligopoly": 2, "latecomer": 1}
    total_building_rate = construction_rate * scenario_factor[scenario]
    df["construction_year"] = (
        np.floor(df.index / total_building_rate) + start_year[construction_rate]
    )
    df["construction_year"] = df["construction_year"].astype(int)


def keep_2030_stations(df_2030, df_2040):
    cutoff = df_2030.shape[0]
    return pd.concat([df_2030, df_2040.iloc[:-cutoff, :]])


def pareto_with_2030_stations(df_2040, total_demand=None):
    df = df_2040.copy()
    df.sort_values(
        by=["prioritize", "total_h2_sold_per_station"], ascending=False
    ).reset_index(inplace=True)
    if total_demand:
        df["cumulative_demand"] = df.total_h2_sold_per_station.cumsum() / total_demand
    else:
        df["cumulative_demand"] = (
            df.total_h2_sold_per_station.cumsum() / df.total_h2_sold_per_station.sum()
        )
    return df, df.total_h2_sold_per_station.sum()


def compute_oligopoly_cum_demand(df, propriety, up_to_year, total_demand):
    ours = df[(df.propriety == propriety) & (df.construction_year <= up_to_year)]
    ours = ours.copy()
    ours.drop("cumulative_demand", axis=1, inplace=True)
    ours["cumulative_demand"] = ours.total_h2_sold_per_station.cumsum() / total_demand
    return np.round(ours.cumulative_demand.max() * 100, 1)


def visualise_profitability(df):
    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        zoom=5,
        height=800,
        width=800,
        color="profitability threshold",
        color_continuous_scale="viridis",
        size=df.size_station.map({"small": 6, "medium": 12, "large": 18}),
    )
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


def visualise_profitability_oligopoly(df):
    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        zoom=5,
        height=800,
        width=800,
        size=df.size_station.map({"small": 6, "medium": 12, "large": 18}),
    )
    fig.update_traces(marker_color=df.propriety.map({0: "red", 1: "blue"}))
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


def load_s3_data(year: str = "2030", property="ours"):
    df = pd.read_csv(f"data_final/scenario3_{year}.csv", index_col=0)
    return df.reset_index(drop=True)


def scenario3_compute_cumdemand(df, total):
    df.total_h2_sold_per_station = df.total_h2_sold_per_station.apply(lambda x: 0 if x == "na" else x)
    df.total_h2_sold_per_station = df.total_h2_sold_per_station.astype(float)
    df["cumulative_demand"] = df.total_h2_sold_per_station.cumsum() / total

