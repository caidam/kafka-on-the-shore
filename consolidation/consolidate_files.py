import pandas as pd
import os
import boto3
import glob
import io
from decouple import config

def consolidate_files_local(directory, city):
    # Get a list of all the files for the city
    files = glob.glob(os.path.join(directory, f"{city}_*.csv"))
    
    # Concatenate all the files into a single DataFrame
    df = pd.concat((pd.read_csv(file) for file in files))
    
    # Write the DataFrame to a new file
    df.to_csv(os.path.join(directory, f"{city}.csv"), index=False)

def consolidate_files_s3(city):

    # Initialize S3 client
    # Create a new boto3 session and S3 client
    session = boto3.Session(
        aws_access_key_id=config('AWS_ACCESS_KEY'),
        aws_secret_access_key=config('AWS_SECRET_KEY'),
        region_name=config('AWS_DEFAUL_REGION')  # e.g., 'us-west-2'
    )
    s3 = session.client('s3')

    bucket = config('S3_BUCKET_NAME')
    
    # Get a list of all the keys for the city
    keys = [obj['Key'] for obj in s3.list_objects(Bucket=bucket)['Contents'] if obj['Key'].startswith(f"raw_cities/{city}_")]
    # print(keys)
    
    # Concatenate all the files into a single DataFrame
    df = pd.concat((pd.read_csv(s3.get_object(Bucket=bucket, Key=key)['Body']) for key in keys))
    
    # Write the DataFrame to a new file in S3
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket, Key=f"consolidated_cities/{city}.csv")

def consolidate_cities() :
    cities = config('CITIES').split(',')
    for city in cities:
        consolidate_files_s3(city)
        print(f'Processed files for {city}')

if __name__ == "__main__" :

    consolidate_cities()