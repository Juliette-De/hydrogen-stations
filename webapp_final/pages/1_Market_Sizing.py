import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px




import hub_clustering.params as p
import hub_clustering.utils as f


import hub_clustering.streamlit_function as l

st.header("Market Sizing")


#scenario = "count_moderate"

scenario_displayed = st.radio("Scenario:",
                              ('optimistic', 'moderate', 'conservative'),
                              1, # Setting default scenario to moderate
                              horizontal=True)

scenario = "count_" + scenario_displayed


# Loading Hub Stations data
hub_stations = f.load_data()

df_agg_hub_stations = f.aggregate_hub_stations(hub_stations)
df_agg_hub_stations["label"] = "hub"
df_agg_hub_stations.drop("Code région", axis=1, inplace=True)

df_agg_hub_stations_2040 = f.aggregate_hub_stations(hub_stations, year="2040")
df_agg_hub_stations_2040["label"] = "hub"
df_agg_hub_stations_2040.drop("Code région", axis=1, inplace=True)


# Loading Road Stations data
road_stations = l.load_and_prepare()
df_agg_road_stations = l.aggregate_road_stations(road_stations)
df_agg_road_stations["label"] = "road"

df_agg_road_stations_2040 = l.aggregate_road_stations(road_stations, year="2040")
df_agg_road_stations_2040["label"] = "road"


# Adding both figures
df_all_stations = pd.concat([df_agg_hub_stations, df_agg_road_stations])
df_all_stations_2040 = pd.concat([df_agg_hub_stations_2040, df_agg_road_stations_2040])
# df_all_stations = df_agg_hub_stations + df_agg_road_stations


st.subheader("Number of stations per scenario")


# Displaying a few metrics depending on scenario

all_2030 = int(df_all_stations[scenario].sum())
all_2040 = int(df_all_stations_2040[scenario].sum())
hub_2030 = int(df_agg_hub_stations[scenario].sum())
hub_2040 = int(df_agg_hub_stations_2040[scenario].sum())
road_2030 = int(df_agg_road_stations[scenario].sum())
road_2040 = int(df_agg_road_stations_2040[scenario].sum())

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("**Number of stations in 2030**", all_2030)
    st.metric("**Number of stations in 2040**",
              all_2040,
              f.percentage_change(all_2030, all_2040))
with col2:
    st.metric("Number of hub stations in 2030", hub_2030)
    st.metric("Number of hub stations in 2040",
              hub_2040,
              f.percentage_change(hub_2030, hub_2040))
with col3:
    st.metric("Number of road stations in 2030", road_2030)
    st.metric("Number of road stations in 2040",
              road_2040,
              f.percentage_change(road_2030, road_2040))


## Plot
df_all_stations.sort_index().sort_values(by="label", inplace=True)
bar_plot_per_region = go.Figure()
bar_plot_per_region.add_trace(go.Bar(x=df_all_stations.index,
                                     y=df_all_stations["count_optimistic"],
                                     #name=df_all_stations.label,
                                     marker_color=df_all_stations.label.map({"hub": "blue", "road": "lightblue"}),
                                     showlegend=True,
                                     legendgroup=1,
                                     legendgrouptitle=dict(text="Optimistic"),
                                     hoverinfo='name'))
bar_plot_per_region.add_trace(go.Bar(x=df_all_stations.index,
                                     y=df_all_stations["count_moderate"],
                                     #name=df_all_stations.label,
                                     marker_color=df_all_stations.label.map({"hub": "green", "road": "lightgreen"}),
                                     showlegend=True,
                                     legendgroup=2,
                                     legendgrouptitle=dict(text="Moderate"),
                                     hoverinfo='name'))
bar_plot_per_region.add_trace(go.Bar(x=df_all_stations.index,
                                     y=df_all_stations["count_conservative"],
                                     #name=df_all_stations.label,
                                     marker_color=df_all_stations.label.map({"hub": "yellow", "road": "lightyellow"}),
                                     showlegend=True,
                                     legendgroup=3,
                                     legendgrouptitle=dict(text="Conservative"),
                                     hoverinfo='name'))

bar_plot_per_region.update_layout(template="plotly", barmode="group", xaxis_tickangle=-45)
st.plotly_chart(bar_plot_per_region)




fig = px.bar(df_all_stations,
             x=df_all_stations.index, y=['count_optimistic', "count_moderate", 'count_conservative'],
             color='label', barmode='group',
             height=400)
st.plotly_chart(fig)

st.dataframe(df_all_stations)

st.dataframe(df_all_stations.melt(var_name='count_', value_name='stations', id_vars='label'))


