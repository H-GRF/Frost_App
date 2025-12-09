import os

DATA_DIR = "data"
RAW_DATA_PATH = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_PATH = os.path.join(DATA_DIR, "processed")
CITY_DF_FILENAME = "city_df.csv"
CITY_FILENAME = "communes-france-2025.csv.gz"
CITY_WITH_CLOSEST_STATIONS_DF_FILENAME = "city_with_closest_stations_df.csv"
GOOD_STATIONS_FILENAME = "good_stations_df.csv"
DATA_URL = 'https://github.com/virgilus/data/raw/refs/heads/main/frost-app-data.zip'
TEMP_FOLDER = "temp"
START_YEAR = 2014
END_YEAR = 2023
DEFAULT_WEATHER_FILENAME = "Q_13_previous-1950-2023_RR-T-Vent.csv.gz"
COMPLETION_RATE_THRESHOLD = 0.65
DEFAULT_WEATHER_URL = "https://object.files.data.gouv.fr/meteofrance/data/synchro_ftp/BASE/QUOT/"
MISSING_CITIES_LAT_LON = {
    "Marseille": [43.295, 5.372],
    "Paris": [48.866, 2.333],
    "Culey": [48.755, 5.266],
    "Les Hauts-Talican": [49.3436, 2.0193],
    "Lyon": [45.75, 4.85],
    "Bihorel": [49.4542, 1.1162],
    "Saint-Lucien": [48.6480, 1.6229],
    "L'Oie": [46.7982, -1.1302],
    "Sainte-Florence": [46.7965, -1.1520],
}