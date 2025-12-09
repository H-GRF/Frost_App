import os
import requests
import zipfile
import shutil
import config as c

def download_data():
    """
    Downloads and unzips the frost days data from the specified URL in the config.
    The data is extracted into the RAW_DATA_PATH and PROCESSED_DATA_PATH defined in the config.
    """
    DATA_ZIP_FILENAME = "frost-app-data.zip"
    response = requests.get(c.DATA_URL)

    os.makedirs(c.TEMP_FOLDER, exist_ok=True)
    if os.path.exists(c.RAW_DATA_PATH) is False:
        os.makedirs(c.RAW_DATA_PATH)

    if response.status_code == 200:
        zip_path = os.path.join(c.TEMP_FOLDER, DATA_ZIP_FILENAME)
        with open(zip_path, 'wb') as file:
            print(f"Downloading file : {c.DATA_URL}")
            file.write(response.content)
            print(f"File downloaded and saved to {zip_path}")
            print("Unzipping file...")
        
        # Unzip the file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(c.TEMP_FOLDER)
        
        # Get the extracted data folder path
        extracted_data_folder = os.path.join(c.TEMP_FOLDER, 'data')
        
        # Move raw and processed folders to their destinations
        raw_folder_source = os.path.join(extracted_data_folder, 'raw')
        processed_folder_source = os.path.join(extracted_data_folder, 'processed')
        
        if os.path.exists(raw_folder_source):
            # Remove existing raw folder if it exists
            if os.path.exists(c.RAW_DATA_PATH):
                shutil.rmtree(c.RAW_DATA_PATH)
            shutil.move(raw_folder_source, c.RAW_DATA_PATH)
            print(f"Raw data moved to {c.RAW_DATA_PATH}")
        
        if os.path.exists(processed_folder_source):
            # Remove existing processed folder if it exists
            if os.path.exists(c.PROCESSED_DATA_PATH):
                shutil.rmtree(c.PROCESSED_DATA_PATH)
            shutil.move(processed_folder_source, c.PROCESSED_DATA_PATH)
            print(f"Processed data moved to {c.PROCESSED_DATA_PATH}")
        
        # Clean up temp folder
        shutil.rmtree(c.TEMP_FOLDER)
        print("Temporary files cleaned up")
        
    else:
        print(f"Failed to download raw data. Status code: {response.status_code}")

if __name__ == "__main__":
    download_data()        