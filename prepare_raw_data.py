import os
import pandas as pd

import func as f
import config as c

def prepare_raw_data():
    # Good stations file creation
    if not os.path.exists(os.path.join(c.PROCESSED_DATA_PATH, c.GOOD_STATIONS_FILENAME)):
        print(f"{c.GOOD_STATIONS_FILENAME} doesn't exist. Creating the file...")
        try:
            station_df = f.get_all_good_stations()
            station_df.to_csv(os.path.join(c.PROCESSED_DATA_PATH, c.GOOD_STATIONS_FILENAME), index=False)
            print("Good stations file created.")
        except Exception as e:
            print(f"An error occurred while creating {c.GOOD_STATIONS_FILENAME}: {e}")
        
    # City dataframe creation with closest stations
    if not os.path.exists(os.path.join(c.PROCESSED_DATA_PATH,c.CITY_WITH_CLOSEST_STATIONS_DF_FILENAME)):
        print(f"{c.CITY_WITH_CLOSEST_STATIONS_DF_FILENAME} doesn't exist. Creating the file...")
        try:
            city_df = f.process_cities_data()
            station_df = f.load_good_stations_df()
            city_with_closest_stations_df = f.add_closest_stations(city_df, station_df, method='haversine')
            city_with_closest_stations_df.to_csv(os.path.join(c.PROCESSED_DATA_PATH, c.CITY_WITH_CLOSEST_STATIONS_DF_FILENAME), index=False)
            print(f" {c.CITY_WITH_CLOSEST_STATIONS_DF_FILENAME} created.")
        except Exception as e:
            print(f"An error occurred while creating {c.CITY_WITH_CLOSEST_STATIONS_DF_FILENAME}: {e}")

if __name__ == "__main__":
    prepare_raw_data()