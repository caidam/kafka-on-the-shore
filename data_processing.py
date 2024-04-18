import os
import pandas as pd
# import boto3
from openweather_utils import get_weather_data
from surreal_events import check_surreal_event
import datetime
import io
import json

def process_data(data):
    # Convert JSON string to dictionary if necessary
    if isinstance(data, str):
        data = json.loads(data)
    # Check if 'weather' is a list and extract the first dictionary
    if isinstance(data['weather'], list) and len(data['weather']) > 0:
        data['weather'] = data['weather'][0]

    # Convert data to DataFrame
    df = pd.json_normalize([data])
    
    # Replace '.' with '_' in column names
    df.columns = df.columns.str.replace('.', '_')
    
    # Check conditions and add information to DataFrame
    event_id, (event_name, event_description, event_newsflash) = check_surreal_event(df)
    df['event_id'] = event_id
    df['event_name'] = event_name
    df['event_description'] = event_description
    df['event_newsflash'] = event_newsflash
    
    return df

def store_data_s3(df, bucket, s3):
    
    # Use the city name and current timestamp as the key (file name)
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    key = f"raw_cities/{df['name'].values[0]}_{timestamp}.csv"
    
    # Convert DataFrame to CSV
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    
    # Upload to S3
    s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket, Key=key)

def store_data_local(df, directory):
    # Use the city name and current timestamp as the file name
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    file_name = f"{df['name'].values[0]}_{timestamp}.csv"
    file_path = os.path.join(directory, file_name)
    
    # Write to the file
    df.to_csv(file_path, index=False)

if __name__ == "__main__":

    data = process_data(get_weather_data('Paris'))

    store_data_local(data, 'data')