import os
import pandas as pd
import streamlit as st

import func as f
import config as c

from download_data import download_data
from download_raw_data import download_raw_data
from prepare_raw_data import prepare_raw_data

# Configuration
start_year = c.START_YEAR
end_year = c.END_YEAR

# Download the data already prepared
if not os.path.exists(c.DATA_DIR):
    download_data()

# Load dataframes
station_df = f.load_good_stations_df()
city_df = f.load_cities_with_closest_stations_df()

# Streamlit app
st.title("Frost Days Statistics! ❄️")

city_input = st.text_input("Start typing a city name:")

if city_input:
    # Filter city names that start with the input (case-insensitive)
    matches = city_df[city_df['name'].str.contains(city_input, case=False, na=False)]
    match_names = matches['name'].unique()
    if len(match_names) > 0:
        selected_city = st.selectbox("Select a city:", match_names)
        city_name = city_df[city_df['name'] == selected_city]
        city_dept = city_df[city_df['name'] == selected_city]['dep_code'].values[0]
        st.write("City information:")
        st.write(city_name)
    else:
        st.write("No matching city found.")
        
# Once the user selects a city, we can display the frost days statistics for the nearest weather station.
if 'selected_city' in locals():
    if not city_name.empty:
        num_poste = city_name.iloc[0]['closest_station_num_poste']
        station_dep = num_poste[:2]  # First two characters represent the department code
        
        st.write(f"Fetching frost days data for the nearest station (Index: {num_poste}, Department: {station_dep})...")
        # Adds a loading spinner while processing
        with st.spinner('Processing weather data...'):
        
            df = f.process_weather_data(
                station_dep, # Use the department of the closest weather station and not the city!
                local_file=False,
                start_year=start_year,
                end_year=end_year,
                completion_rate_threshold=c.COMPLETION_RATE_THRESHOLD,
            ).loc[lambda x: x['station_id'] == num_poste]
            
            # Compute frost days per year and mean number of frost days
            station_alti = df.iloc[0]['alti']
            number_of_frost_days_per_year = f.compute_number_of_frost_days_per_year(df)
            mean_number_of_frost_days = f.compute_mean_number_of_frost_days(df)

            # What does the dataframe look like?
            st.write(df.head(3))
            # if everything is correct, display a bar chart of frost days percentage over the years for the selected station
            if not df.empty:

                st.write(
                f"""
                Data for station {df['station_name'].values[0]} - {station_dep} - N°{num_poste}
                Station Altitude : {station_alti}m, Mean of frost days per year: {mean_number_of_frost_days}
                """)
                
                # Get frost days data in chronological order
                frost_per_day = f.compute_frost_days_percentage_per_day(df)
                
                # Display using st.bar_chart - now with day_of_year as numeric index
                st.subheader("Frost Days Percentage Throughout the Year")
                st.bar_chart(frost_per_day)
                
                # Let's use a plot with a curve to better visualize the trend over the years
                # Convert year to string for proper display on x-axis
                frost_by_year_chart = number_of_frost_days_per_year.copy()
                frost_by_year_chart['year'] = frost_by_year_chart['year'].astype(str)
                st.line_chart(frost_by_year_chart.set_index('year')['frost_day'])

    else:
        st.write("City information is not available.")
        