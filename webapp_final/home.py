import streamlit as st
from streamlit_folium import folium_static

st.write("""This application has been developed to visualize the locations where to implement hydrogen stations in 2030 and 2040, according to different parameters and scenarios.
It offers the following three features, each on one page:
- a sizing of the market according to the scenario envisaged - optimistic, moderate or conservative (see the slides for more information), including:
        - the number of stations,
        - their distribution by region;
- the location and size of the stations;
- a dashboard of the profitability of each station, according to the following competitive scenarios:
        - 1: A single network in France
        - 2: Two players entering the market simultaneously (Air Liquide in blue and Red Team in red)
        - 3: Air Liquide arriving after an incumbent operator transformed its network of oil stations into H2.""")
        
# def app():
    

# if __name__ == "__app__":
#     app()
