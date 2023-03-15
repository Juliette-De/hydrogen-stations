import streamlit as st
from IPython.display import display
import os
import sys
from streamlit_folium import folium_static

sys.path.append("/Users/antoinerazeghi/Documents/Projects/AirLiquide/airliquide/")


import hub_clustering.streamlit_function as l


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

print(df_bis)

st.title('Global traffic information')
folium_static(l.globalTraffic(df_bis))

