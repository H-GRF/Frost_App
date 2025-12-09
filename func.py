import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from haversine import haversine, Unit
from scipy.spatial import cKDTree

import config as c


def compute_missing_values_over_time(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate the percentage of missing values over time and the number of stations in activity each year.

    Args:
        df (pd.DataFrame): Input dataframe containing weather data.

    Returns:
        pd.DataFrame: Dataframe with missing values percentage and stations in activity.
    """

    missing_values_df = (
        df.groupby(df["date"].dt.year).agg(
            {"tmin": lambda x: x.isnull().mean() * 100, "station_id": "nunique"}
        )
    ).rename(columns={"tmin": "missing_values", "station_id": "stations_in_activity"})
    return missing_values_df


def plot_missing_values_and_stations(df: pd.DataFrame) -> None:
    """Plot the percentage of missing values and the number of stations in activity over time."""
    plt.figure(figsize=(12, 6))
    sns.barplot(x=df.index, y=df["missing_values"])
    plt.xticks(rotation=90)
    plt.title("Percentage of Missing Values by Year")
    plt.xlabel("Year")
    plt.ylabel("Percentage of Missing Values")
    plt.show()


def plot_completion_rate_distribution(df: pd.DataFrame) -> None:
    """Plot the distribution of completion rate per station."""
    completion_rate = df.groupby("station_id")["tmin"].apply(
        lambda x: x.notnull().mean() * 100
    )
    plt.figure(figsize=(12, 6))
    sns.histplot(completion_rate, bins=100, kde=True)
    plt.title("Distribution of Completion Rate per Station")
    plt.xlabel("Completion Rate (%)")
    plt.ylabel("Number of Stations")
    plt.show()


def process_weather_data(
    dept: str,
    local_file: bool = False,
    start_year: int = c.START_YEAR,
    end_year: int = c.END_YEAR,
    completion_rate_threshold: float = c.COMPLETION_RATE_THRESHOLD,
    remove_stations_below_threshold: bool = True,
    raw_data_path: str = c.RAW_DATA_PATH,
    default_url: str = c.DEFAULT_WEATHER_URL,
) -> pd.DataFrame:
    """Process weather data for a specific department."""

    filename = f"Q_{dept}_previous-1950-2023_RR-T-Vent.csv.gz"
    if local_file:
        weather_filename = os.path.join(raw_data_path, filename)
    else:
        weather_filename = f"{default_url}{filename}"

    d = {
        "NUM_POSTE": (str, "station_id"),
        "NOM_USUEL": (str, "station_name"),
        "LAT": (float, "latitude"),
        "LON": (float, "longitude"),
        "ALTI": (float, "alti"),
        "AAAAMMJJ": (str, "date"),
        "TN": (float, "tmin"),
    }

    # 1. Load the file with only the necessary columns and appropriate data types
    weather_df = pd.read_csv(
        weather_filename,
        compression="gzip",
        sep=";",
        usecols=d.keys(),
        dtype={k: v[0] for k, v in d.items()},
    ).rename(columns={k: v[1] for k, v in d.items()})

    weather_df["date"] = pd.to_datetime(weather_df["date"], format="%Y%m%d")

    # 2. Slice the dataframe to keep only the data from start_year to end_year
    weather_df = weather_df.loc[
        weather_df["date"].dt.year.between(start_year, end_year, inclusive="both")
    ]

    # 3. Remove all observations from stations that have a completion rate lower than the threshold
    if remove_stations_below_threshold:
        completion_rate = weather_df.groupby("station_id")["tmin"].apply(
            lambda x: x.notnull().mean()
        )
        valid_stations = completion_rate[
            completion_rate >= completion_rate_threshold
        ].index
        weather_df = weather_df[weather_df["station_id"].isin(valid_stations)]

    # 4. Create 'frost_day', 'year', 'month', 'day' columns
    
    weather_df['frost_day'] = weather_df['tmin'] < 0
    weather_df['year'] = weather_df['date'].dt.year
    weather_df['month'] = weather_df['date'].dt.month
    weather_df['day'] = weather_df['date'].dt.day
    
    # Compute for each station the % of frost of each day over the years
    # This will be useful to plot the frost days over a typical year later on

    # 5. Reset index
    weather_df = weather_df.reset_index(drop=True)

    return weather_df


def process_cities_data(
    raw_data_path: str = c.RAW_DATA_PATH,
    filename: str = "communes-france-2025.csv.gz",
    dept_list: list | None = None,
) -> pd.DataFrame:
    """Process cities data, filling missing lat/lon values and filtering by department list if provided."""

    d = {
            "code_insee": ["string", "insee_code"],
            "nom_standard": ["string", "name"],
            "dep_code": ["string", "dep_code"],
            "dep_nom": ["string", "dep_name"],
            "latitude_centre": ["float32", "lat"],
            "longitude_centre": ["float32", "lon"],
        }

    # 1. Load the file with only the necessary columns and appropriate data types
    city_df = pd.read_csv(
        os.path.join(raw_data_path, filename),
        compression="gzip",
        usecols=d.keys(),
        dtype={k: v[0] for k, v in d.items()},
    ).rename(columns={k: v[1] for k, v in d.items()})

    # 2. Modify the dataframe to fill in the missing lat/lon values
    # The dictionary MISSING_CITIES_LAT_LON contains the missing values and is stored in config.py
    for city, (lat, lon) in c.MISSING_CITIES_LAT_LON.items():
        city_df.loc[city_df["name"] == city, "lat"] = lat
        city_df.loc[city_df["name"] == city, "lon"] = lon

    if dept_list is None:
        dept_list = [adds_zero_if_needed(i) for i in range(1, 96)]  # Metropolitan France departments from 01 to 95 
    
    city_df = city_df[city_df["insee_code"].str[:2].isin(dept_list)]

    return city_df


def adds_zero_if_needed(x: int) -> str:
    if x < 10:
        return "0" + str(x)
    return str(x)


def get_all_good_stations(dept_list: list | None = None) -> pd.DataFrame:

    # If no department list is provided
    # use all metropolitan France departments (01 to 95)
    if dept_list is None:
        dept_list = [
            adds_zero_if_needed(i) for i in range(1, 96)
        ]  # Metropolitan France departments from 01 to 95

    dfs = []
    for dept in dept_list:
        df = process_weather_data(dept=dept, remove_stations_below_threshold=True)
        dfs.append(
            df[
                ["station_id", "station_name", "latitude", "longitude", "alti"]
            ].drop_duplicates()
        )
        print(f"Done with dept N° {dept}")
    return pd.concat(dfs)


# def create_good_stations_df_file(dept_list: list|None=None, filename='stations_df.csv'):
#     stations_df = get_all_good_stations(dept_list).reset_index(drop=True)
#     stations_df.to_csv(filename, index=False)


# Let's make a function that does all this process and add it in func.py
def add_closest_stations(
    city_df: pd.DataFrame,
    stations_df: pd.DataFrame,
    method: str = "kdtree",
    add_station_info: bool = True,
) -> pd.DataFrame:

    # Prepare city and station coordinates as arrays
    city_coords = city_df[["lat", "lon"]].to_numpy()
    station_coords = stations_df[["latitude", "longitude"]].to_numpy()

    if method == "kdtree":
        # Build a KDTree for station coordinates
        tree = cKDTree(station_coords)

        # For each city, find the index of the closest station
        distances, indices = tree.query(city_coords)

        # Add the closest station index and distance to city_df
        city_df["closest_station_idx"] = indices
        city_df["closest_station_distance_km"] = distances * 100

        # Optionally, add station info (e.g., station name or properties)
        if add_station_info:
            city_df["closest_station_name"] = stations_df.iloc[indices][
                "station_name"
            ].values
            city_df["closest_station_num_poste"] = stations_df.iloc[indices][
                "station_id"
            ].values
            # city_df['closest_station_num_dep'] = stations_df.iloc[indices]['station_id'].str[:2].values
            city_df["closest_station_alti"] = stations_df.iloc[indices]["alti"].values

    elif method == "haversine":

        closest_station_idx = []
        closest_station_distance = []

        for city in city_coords:
            # Compute all distances from this city to all stations
            distances = [
                haversine(city, station, unit=Unit.KILOMETERS)
                for station in station_coords
            ]
            min_idx = np.argmin(distances)
            closest_station_idx.append(min_idx)
            closest_station_distance.append(distances[min_idx])

        # Add the closest station index and distance to city_df
        city_df["closest_station_idx"] = closest_station_idx
        city_df["closest_station_distance_km"] = closest_station_distance

        if add_station_info:
            city_df["closest_station_name"] = stations_df.iloc[closest_station_idx][
                "station_name"
            ].values
            city_df["closest_station_num_poste"] = stations_df.iloc[
                closest_station_idx
            ]["station_id"].values
            city_df["closest_station_alti"] = stations_df.iloc[closest_station_idx][
                "alti"
            ].values

    return city_df

def load_cities_with_closest_stations_df(
    filename: str = c.CITY_WITH_CLOSEST_STATIONS_DF_FILENAME,
    path: str = c.PROCESSED_DATA_PATH,
) -> pd.DataFrame:
    """Load the cities with closest stations dataframe from a CSV file."""

    d = {
        "insee_code": "string",
        "name": "string",
        "dep_code": "string",
        "dep_name": "string",
        "lat": "float",
        "lon": "float",
        "closest_station_idx": "int",
        "closest_station_distance_km": "float",
        "closest_station_name": "string",
        "closest_station_num_poste": "string",
        "closest_station_alti": "float",
    }

    return pd.read_csv(os.path.join(path, filename), dtype=d)

def load_good_stations_df(
    filename: str = c.GOOD_STATIONS_FILENAME,
    path: str = c.PROCESSED_DATA_PATH,
) -> pd.DataFrame:
    """Load the good stations dataframe from a CSV file."""

    d = {
        "station_id": "string",
        "station_name": "string",
        "latitude": "float",
        "longitude": "float",
        "alti": "float",
    }

    return pd.read_csv(os.path.join(path, filename), dtype=d)

def compute_number_of_frost_days_per_year(df: pd.DataFrame) -> pd.DataFrame:
    """Compute the number of frost days per year from the weather DataFrame.
    Make sure the DataFrame contains 'date' and 'tmin' columns and that the
    dataframe has been filtered beforehand, in you want to compute on a single station.
    """
    frost_days_per_year = df.groupby('year')['frost_day'].sum().reset_index()
    # Convert year to int to avoid decimal display in charts
    frost_days_per_year['year'] = frost_days_per_year['year'].astype(int)
    return frost_days_per_year

def compute_mean_number_of_frost_days(df: pd.DataFrame) -> float:
    """Compute the average number of frost days per year from a DataFrame containing 'frost_day' and 'year' columns.
    Make sure your dataframe has been filtered beforehand, if you want to compute on a single station."""
    frost_days_per_year = df.groupby('year')['frost_day'].sum()
    return frost_days_per_year.mean()

def compute_frost_days_percentage_per_day(df: pd.DataFrame) -> pd.DataFrame:
    """Compute the percentage of frost days for each day of the year over all years.
    Returns a DataFrame with day_of_year as index for proper chronological ordering in charts.
    """
    # Add day of year for proper ordering
    df_temp = df.copy()
    df_temp['day_of_year'] = df_temp['date'].dt.dayofyear
    
    # Group by day of year and calculate frost day percentage
    frost_by_day = df_temp.groupby('day_of_year').agg({
        'frost_day': lambda x: (x.sum() / len(x)) * 100,
        'month': 'first',
        'day': 'first'
    }).reset_index()

    # Create the DD/MM format for display
    frost_by_day['date_str'] = frost_by_day['day'].astype(str).str.zfill(2) + '/' + frost_by_day['month'].astype(str).str.zfill(2)

    # Use day_of_year as index to preserve chronological order
    frost_by_day = frost_by_day.set_index('day_of_year')[['frost_day']].rename(columns={'frost_day': 'Frost Days (%)'})

    return frost_by_day