# Hydrogen Trucks Charging Stations - Group 6


This application has been developed to visualize the locations where to implement hydrogen stations in 2030 and 2040, according to different parameters and scenarios.

## Quick start

The applicaition is deployed at [this adress](https://pointing9212-airliquide-webapp-finalhome-65qg7b.streamlit.app).

Alternatively, to run it locally:

- Clone this github repository or upload all of its files to the folder where you want to place this project.

- Install the necessary packages from the requirements.txt file provided in the *webapp_final* folder. In the terminal, replacing path with the path of your dedicated folder:
```
pip install -r path/webapp_final/requirements.txt
```

- Launch the application:
```
streamlit run path/webapp_final/home.py
```


## Features

This application offers the following three features, each on one page:
- a sizing of the market according to the scenario envisaged - optimistic, moderate or conservative (see the slides for more information), including
  - the number of stations
  - their distribution by region;
- the location and size of the stations
- a dashboard of the profitability of each station, according to the following competitive scenarios:
  - 1: A single network in France
  - 2: Two players entering the market simultaneously (Air Liquide in blue and Red Team in red)
  - 3: Air Liquide arriving after an incumbent operator transformed its network of oil stations into H2.


## Background

This project was created for a challenge run by Digital Value, Air Liquide and the Ministry of Ecological Transition.
