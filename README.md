# Frost Days App

This app contains code to download and process data related to frost days in France. It includes scripts to download raw data, prepare the data for analysis, and store processed data for further use.

## Use cases

- From there you can build a Streamlit application to visualize and analyze frost days based on the processed data.

- Or you can build an API using FastAPI to serve the processed data for further analysis or integration with other applications.

## Downloading the data

- **Option 1 (easy)**:
The easiest way to get the data is to run the `download_data.py` script which will download data that have been already prepared and stored on a git repo.

- **Option 2 (advanced)**:
- But you can also regenerate the data directly from the source (data.gouv.fr) with running first the script `download_raw_data.py` and then run the `prepare_data.py` script. It usually takes around 10mns to download and prepare the data.
