import pandas as pd
from sklearn.cluster import KMeans
import geopy.distance
import numpy as np
import plotly.express as px
import params as p

import warnings
from pandas.errors import SettingWithCopyWarning

warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

def load_data():
    data = pd.read_csv("donnees_entrepot_location.csv")
    data["location"] = data.apply(lambda x: (x.latitude, x.longitude), axis=1)
    return data

def _load_region_transco():
    xls = pd.ExcelFile('donnees_entrepots.xls')
    region = pd.read_excel(xls, "Données régionales")
    region.columns = region.iloc[1]
    region = region.drop([0,1], axis=0).reset_index(drop=True)
    region = region.iloc[:12,:]
    return region


def filter_dataset(dataset, scenario, hub_size_thresholds=p.HUB_SIZE_THRESHOLDS):
    hub_size_threshold = hub_size_thresholds[scenario]
    return dataset[dataset["Surface totale"] > hub_size_threshold]

def run_kmeans(data, threshold_km=p.DISTANCE_THRESHOLD_KM,threshold_nb_areas_by_centroid=p.THRESHOLD_NB_AREAS_BY_CENTROID):
    """
    For each region, runs KMEANS (starting with 1 centroid and adding one at each step) until the 2 conditions are met :
    - distance to centroids < threshold_km
    - nb of hubs by centroid < threshold_nb_areas_by_centroid

    Returns
     - a dataset with all hubs, associated centroids, its location and the distance to the centroid
     - a dataframe where each row correspond to a centroid with its region and coordinates
    """

    data = data[["Identifiant aire logistique dense (e1)", "Région d'implantation", "location", "longitude", "latitude"]]
    region_list = list(data["Région d'implantation"].unique())

    final_dataset = pd.DataFrame()
    centroid_by_region = {}

    #Computing centroids region by region
    for region in region_list :
        dataset = data[data["Région d'implantation"] == region]
        
        # initialising limiting factors for KMeans
        areas_not_served = len(dataset)         
        nb_areas_by_centroid = len(dataset)
        
        # set the initial number of clusters at sufficient amount to satisfy max number of areas by station
        i = 1
        
        # if the region has only 1 area, run KMeans with 1 centroid
        threshold_not_served = int(0.2*len(dataset)) + 1 if len(dataset)>1 else 0
        
        while (areas_not_served > threshold_not_served) | (nb_areas_by_centroid > threshold_nb_areas_by_centroid) :
            kmeans = KMeans(
                init="random",
                n_clusters=i,
                n_init=10,
                max_iter=300,
                random_state=42
            )

            kmeans.fit(dataset[["latitude", "longitude"]])

            # Store the centroid information for each area
            dataset["centroid"] = kmeans.labels_
            dataset["centroid_coord"] = dataset["centroid"].apply(lambda x : kmeans.cluster_centers_[x])
            dataset["distance_to_centroid"] = dataset.apply(lambda x : geopy.distance.geodesic(x["location"], kmeans.cluster_centers_[x["centroid"]]).km, axis=1)
            
            # Increase nb of centroids by 1
            i += 1

            # Recompute limiting factors
            areas_not_served = sum(dataset["distance_to_centroid"]>threshold_km)
            nb_areas_by_centroid = max(dataset.groupby("centroid")["Identifiant aire logistique dense (e1)"].count().reset_index()["Identifiant aire logistique dense (e1)"])
        
        # Store the centroid information aside
        centroid_by_region[region] = kmeans.cluster_centers_
        
        # Build the final dataset with all information
        final_dataset = pd.concat([final_dataset, dataset], axis=0)
    
    # Create dataframe with coord of each centroid and associated region
    centroids_df = pd.DataFrame(
        [(k, i[0], i[1]) for k, v in centroid_by_region.items() for i in v], 
        columns=['region', 'latitude', "longitude"]
    )

    return final_dataset, centroids_df

def count_centroid_by_region(centroids_df):
    region = _load_region_transco()
    count_by_region = centroids_df.groupby("region").agg(count=("latitude", 'count')).reset_index()
    count_by_region["region"] = count_by_region["region"].astype(str)
    count_by_region = count_by_region.merge(region[["Code région", "Libellé des régions"]], left_on='region', right_on="Code région", how="left")
    count_by_region.sort_values(by="count", ascending=False)
    return count_by_region[["Libellé des régions", "Code région", "count"]]


def compute_centroid_size(final_dataset):
    # Number of areas by centroid
    nb_areas_by_centroid = final_dataset.groupby(["Région d'implantation", "centroid"])["Identifiant aire logistique dense (e1)"].count().reset_index()
    nb_areas_by_centroid["station_size"] = nb_areas_by_centroid["Identifiant aire logistique dense (e1)"].apply(lambda x : (x > 2) + (x > 4))
    nb_areas_by_centroid.rename(columns = {"Identifiant aire logistique dense (e1)" : "area_count"}, inplace=True)
    return nb_areas_by_centroid

def compute_nb_centroids(centroids_df):
    return len(centroids_df)

def visualize_on_map(final_dataset, centroids_df):
    fig = px.scatter_mapbox(final_dataset, 
                            lat="latitude", 
                            lon="longitude", 
                            zoom=8, 
                            height=800,
                            width=800)

    fig.add_scattermapbox(lat = centroids_df["latitude"]
                        ,lon = centroids_df["longitude"]
                        ,marker_size = 6
                        ,marker_color = 'red'
    #                       ,marker_symbol = 'star'
                        ,showlegend = True
                        )

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()