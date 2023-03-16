import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sys


import hub_clustering.utils as f
import hub_clustering.profitability as prof
import numpy as np


import hub_clustering.streamlit_function as l

st.header("Profitability")


with st.sidebar:
    up_to_year = st.slider("Select a year (monopoly)", 2025, 2040, 2026) - 1
    up_to_year_o = st.slider("Select a year (oligopoly)", 2025, 2040, 2026) - 1
    up_to_year_l = st.slider("Select a year (latecomer)", 2025, 2040, 2026) - 1

st.subheader("Scenario 1: Monopoly")


df_2030, total_demand_2030 = prof.load_and_clean()
df_2040, _ = prof.load_and_clean("2040")
prof.add_construction_year(df_2030, scenario="monopoly")
prof.add_construction_year(df_2040, construction_rate=13, scenario="monopoly")
merged_2040 = prof.keep_2030_stations(df_2030.iloc[:30], df_2040)
final_2040, total_demand_2040 = prof.pareto_with_2030_stations(merged_2040)
final_2040 = final_2040.iloc[:160]
final_2040["profitability threshold"] = final_2040["profitability threshold"].apply(
    lambda x: min(3, x)
)

col1, col2 = st.columns(2)
if up_to_year < 2030:
    print(df_2030.head())#
    col1.metric(
        "total number of stations",
        df_2030[df_2030.construction_year <= up_to_year].shape[0],
        f.percentage_change(
            df_2030[df_2030.construction_year <= up_to_year - 1].shape[0],
            df_2030[df_2030.construction_year <= up_to_year].shape[0],
        ),
    )
    col2.metric(
        "% of demand met by AirLiquide",
        str(
            np.round(
                df_2030[df_2030.construction_year <= up_to_year][
                    "cumulative_demand"
                ].max(),
                2,
            )
            * 100
        )[:4]
        + "%",
    )
    st.plotly_chart(
        prof.visualise_profitability(df_2030[df_2030.construction_year <= up_to_year])
    )
else:
    col1.metric(
        "Total number of stations",
        final_2040[final_2040.construction_year <= up_to_year].shape[0],
        f.percentage_change(
            final_2040[final_2040.construction_year <= up_to_year - 1].shape[0],
            final_2040[final_2040.construction_year <= up_to_year].shape[0],
        ),
    )
    col2.metric(
        "% of demand met by AirLiquide",
        str(
            np.round(
                final_2040[final_2040.construction_year <= up_to_year][
                    "cumulative_demand"
                ].max()
                * 100,
                2,
            )
        )[:4]
        + "%",
    )
    st.plotly_chart(
        prof.visualise_profitability(
            final_2040[final_2040.construction_year <= up_to_year]
        )
    )

    
    

### Scenario 2


st.subheader("Scenario 2: Oligopoly")


total_demand_2040 = 876257.7037511724

df_2030 = pd.read_csv("oligopoly_2030.csv")
df_2030['propriety'] = np.where(df_2030['propriety'] == 1, 'Air Liquide', 'Red Team')

final_2040 = pd.read_csv("oligopoly_2040.csv")
final_2040['propriety'] = np.where(final_2040['propriety'] == 1, 'Air Liquide', 'Red Team')


def compute_oligopoly_cum_demand(df, propriety, up_to_year, total_demand):
    ours = df[(df.propriety == propriety) & (df.construction_year <= up_to_year)]
    ours = ours.copy()
    ours.drop("cumulative_demand", axis=1, inplace=True)
    ours["cumulative_demand"] = ours.total_h2_sold_per_station.cumsum() / total_demand
    return np.round(ours.cumulative_demand.max() * 100, 1)

def visualise_profitability_oligopoly(df):
    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        zoom=5,
        height=800,
        width=800,
        size=df.size_station.map({"small": 1, "medium": 5, "large": 10}),
        size_max=12,
        color='propriety',
        color_discrete_map={"Air Liquide": "blue", "Red Team": "red"}
        
    )
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


col1, col2 = st.columns(2)
if up_to_year_o < 2030:
    col1.metric(
        "Total number of stations",
        df_2030[df_2030.construction_year <= up_to_year_o].shape[0],
        f.percentage_change(
            df_2030[df_2030.construction_year <= up_to_year_o - 1].shape[0],
            df_2030[df_2030.construction_year <= up_to_year_o].shape[0],
        ),
    )
    col2.metric(
        "% of demand met in total",
        str(compute_oligopoly_cum_demand(
                df_2030, 'Air Liquide', up_to_year_o, total_demand_2030
            )
            + compute_oligopoly_cum_demand(
                df_2030, 'Red Team', up_to_year_o, total_demand_2030
            )
        )[:4]
        + "%",
        str(compute_oligopoly_cum_demand(
                df_2030, 'Air Liquide', up_to_year_o, total_demand_2030
            )
            + compute_oligopoly_cum_demand(
                df_2030, 'Red Team', up_to_year_o, total_demand_2030
            )
            - (compute_oligopoly_cum_demand(
                    df_2030, 'Air Liquide', up_to_year_o - 1, total_demand_2030
                )
                + compute_oligopoly_cum_demand(
                    df_2030, 'Red Team', up_to_year_o - 1, total_demand_2030
                )
            )
        )[:4],
    )
    col1.metric(
        "% of demand met by AirLiquide",
        str(compute_oligopoly_cum_demand(
                df_2030, 'Air Liquide', up_to_year_o, total_demand_2030
            )
        )[:4]
        + "%",
        str(compute_oligopoly_cum_demand(
                df_2030, 'Air Liquide', up_to_year_o, total_demand_2030
            )
            - compute_oligopoly_cum_demand(
                df_2030, 'Air Liquide', up_to_year_o - 1, total_demand_2030
            )
        )[:4],
    )
    col2.metric(
        "% of demand met by Red Team",
        str(compute_oligopoly_cum_demand(
                df_2030, 'Red Team', up_to_year_o, total_demand_2030
            )
        )[:4]
        + "%",
        str(compute_oligopoly_cum_demand(
                df_2030, 'Red Team', up_to_year_o, total_demand_2030
            )
            - compute_oligopoly_cum_demand(
                df_2030, 'Red Team', up_to_year_o - 1, total_demand_2030
            )
        )[:4],
    )

    st.plotly_chart(visualise_profitability_oligopoly(
            df_2030[df_2030.construction_year <= up_to_year_o]
        )
    )
else:
    col1.metric(
        "Total number of stations",
        final_2040[final_2040.construction_year <= up_to_year_o].shape[0],
        f.percentage_change(
            final_2040[final_2040.construction_year <= up_to_year_o - 1].shape[0],
            final_2040[final_2040.construction_year <= up_to_year_o].shape[0],
        ),
    )
    col2.metric(
        "% of demand met in total",
        str(compute_oligopoly_cum_demand(
                final_2040, 'Air Liquide', up_to_year_o, total_demand_2040
            )
            + compute_oligopoly_cum_demand(
                final_2040, 'Red Team', up_to_year_o, total_demand_2040
            )
        )[:4]
        + "%",
        str(
            compute_oligopoly_cum_demand(
                final_2040, 'Air Liquide', up_to_year_o, total_demand_2040
            )
            + compute_oligopoly_cum_demand(
                final_2040, 'Red Team', up_to_year_o, total_demand_2040
            )
            - (
                compute_oligopoly_cum_demand(
                    final_2040, 'Air Liquide', up_to_year_o - 1, total_demand_2040
                )
                + compute_oligopoly_cum_demand(
                    final_2040, 'Red Team', up_to_year_o - 1, total_demand_2040
                )
            )
        )[:4],
    )
    col1.metric(
        "% of demand met by AirLiquide",
        str(
            compute_oligopoly_cum_demand(
                final_2040, 'Air Liquide', up_to_year_o, total_demand_2040
            )
        )[:4]
        + "%",
        str(
            compute_oligopoly_cum_demand(
                final_2040, 'Air Liquide', up_to_year_o, total_demand_2040
            )
            - compute_oligopoly_cum_demand(
                final_2040, 'Air Liquide', up_to_year_o - 1, total_demand_2040
            )
        )[:4],
    )
    col2.metric(
        "% of demand met by Red Team",
        str(
            compute_oligopoly_cum_demand(
                final_2040, 'Red Team', up_to_year_o, total_demand_2040
            )
        )[:4]
        + "%",
        str(
            compute_oligopoly_cum_demand(
                final_2040, 'Red Team', up_to_year_o, total_demand_2040
            )
            - compute_oligopoly_cum_demand(
                final_2040, 'Red Team', up_to_year_o - 1, total_demand_2040
            )
        )[:4],
    )
    st.plotly_chart(visualise_profitability_oligopoly(final_2040[final_2040.construction_year <= up_to_year_o]))
    
    
    
### Scenario 3


st.subheader("Scenario 3: AirLiquide enters the market after Red Team")


s3_2030 = pd.read_csv("webapp_final/s3_2030.csv", index_col=0)
new_s3_2040 = pd.read_csv("webapp_final/s3_2040.csv", index_col=0)


def visualise_later(df, year=2030):
    if year == 2030:
        size = df.size_station.map({"small": 18, "medium": 12, "large": 18, "na": 1})
    else:
        size = df.size_station.map({"small": 6, "medium": 12, "large": 18, "na": 1})

    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        zoom=5,
        height=800,
        width=800,
        size=size,
    )
    fig.update_traces(
        marker_color=df.size_station.map(
            {"small": "blue", "medium": "green", "large": "orange", "na": "red"}
        )
    )
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig



if up_to_year_l < 2030:
    col1, col2 = st.columns(2)
    col1.metric(
        "AirLiquide's stations",
        s3_2030[
            (s3_2030.construction_year < up_to_year_l) & (s3_2030.property == "ours")
        ].shape[0],
    )
    col2.metric(
        "AirLiquide's market share",
        str(
            np.round(
                s3_2030[
                    (s3_2030.construction_year < up_to_year_l)
                    & (s3_2030.property == "ours")
                ]["cumulative_demand"].max(),
                2,
            )
            * 100
        )[:4]
        + "%",
    )
    st.image("webapp_final/2030.png")
    
else:
    col1, col2 = st.columns(2)
    col1.metric(
        "AirLiquide's stations",
        new_s3_2040[
            (new_s3_2040.construction_year < up_to_year_l)
            & (new_s3_2040.property == "ours")
        ].shape[0],
    )
    col2.metric(
        "AirLiquide's market share",
        str(
            np.round(
                new_s3_2040[
                    (new_s3_2040.construction_year < up_to_year_l)
                    & (new_s3_2040.property == "ours")
                ]["cumulative_demand"].max(),
                2,
            )
            * 100
        )[:4]
        + "%",
    )
    st.image("webapp_final/2040.png")
