import streamlit as st
import sys
import os
from streamlit_folium import folium_static


sys.path.append("/Users/antoinerazeghi/Documents/Projects/AirLiquide/airliquide/")



import hub_clustering.streamlit_function as l
import plotly.graph_objects as go
import plotly.express as px

df = l.load_and_prepare()

df_bis = df.copy()
df_bis['Highway'] = df_bis.route.apply(lambda x:"Highway" if x[0]=='A' else "Other")

select_options = st.multiselect(
  'Select the roads you want to focus on',
  ["All", "Highways", "Other"] + list(df_bis.route.unique()),
   default='All')

if 'All' in select_options:
  df_bis = df_bis
elif 'Highways' in select_options:
  df_bis = df_bis[df_bis.Highway == "Highway"]
elif 'Other' in select_options:
  df_bis = df_bis[df_bis.Highway != "Highway"]
else:
   df_bis = df_bis[df_bis.route.isin(select_options)]

default_frequency = 150
default_affluence = 0.25

options = ('Optimistic', 'Moderate', 'Conservative')
selected_option = st.sidebar.radio('Select a traffic scenario', options)


# Set the default values for the sliders based on the selected option
if selected_option == 'Optimistic':
    default_frequency = 100
    default_affluence = 0.2
elif selected_option == 'Moderate':
    default_frequency = 150
    default_affluence = 0.25
else:
    default_frequency = 200
    default_affluence = 0.3

# Display the sliders for frequency and affluence
frequency = st.sidebar.slider("Custom Frequency", 50, 300, default_frequency, step=25)
affluence = st.sidebar.slider("Custom Affluence", float(0), float(1), default_affluence, step=0.05)

st.title("Intermediate stations repartition : stations on roads & highways")

try: 
  m, df_info = l.intermediateStations(df_bis, frequency, affluence)
  folium_static(m)
except IndexError:
    st.write('Please select atleast one road')
    

df_info = df_info.groupby('region_name')['is_stationable'].sum().reset_index()

st.write('Total number of stations : ', int(df_info.is_stationable.sum()))

options_regions = st.multiselect("What scenario would you like to stimulate?", ('Optimistic', 'Moderate', 'Conservative'), ('Optimistic', 'Moderate', 'Conservative'))

l.intermediateStations_region(df).to_csv("test.csv")

fig3 = go.Figure()
if "Optimistic" in options_regions:
    temp = l.intermediateStations_region(df)[0]
    fig3.add_trace(
        go.Bar(
            x=temp['region_name'],
            y=temp['is_stationable'],
            name="Optimistic",
            marker_color=px.colors.qualitative.Plotly[0],
        )
    )
if "Moderate" in options_regions:
    temp = l.intermediateStations_region(df)[1]
    fig3.add_trace(
        go.Bar(
            x=temp['region_name'],
            y=temp['is_stationable'],
            name="Moderate",
            marker_color=px.colors.qualitative.Plotly[1],
        )
    )
if "Conservative" in options_regions:
    temp = l.intermediateStations_region(df)[2]
    fig3.add_trace(
        go.Bar(
            x=temp['region_name'],
            y=temp['is_stationable'],
            name="Conservative",
            marker_color=px.colors.qualitative.Plotly[3],
        )
    )
fig3.update_layout(barmode="group", xaxis_tickangle=-45)
st.plotly_chart(fig3)


