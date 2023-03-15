HUB_SIZE_THRESHOLDS_2030 = {
    "optimistic": 0,
    "moderate": 75_000,
    "conservative": 100_000,
}
HUB_SIZE_THRESHOLDS_2040 = {"optimistic": 0, "moderate": 25_000, "conservative": 75_000}
HUB_SIZE_THRESHOLDS = {
    "2030": HUB_SIZE_THRESHOLDS_2030,
    "2040": HUB_SIZE_THRESHOLDS_2040,
}
DISTANCE_THRESHOLD_KM_2030 = {"optimistic": 20, "moderate": 20, "conservative": 20}
DISTANCE_THRESHOLD_KM_2040 = {"optimistic": 0, "moderate": 20, "conservative": 20}
DISTANCE_THRESHOLD_KM = {
    "2030": DISTANCE_THRESHOLD_KM_2030,
    "2040": DISTANCE_THRESHOLD_KM_2040,
}

THRESHOLD_NB_AREAS_BY_CENTROID = 5

ROAD_HUB_THRESHOLDS = {
    "2030": [(125, 0.2), (150, 0.25), (200, 0.3)],
    "2040": [(50, 0.0), (75, 0.0), (100, 0.25)],
}
HYDROGENE_SERVED_BY_HUBS = {"2030": 60_000, "2040": 360_000}

60_000
NUMBER_OF_TRUCKS = {"2030": 10_000, "2040": 60_000}
