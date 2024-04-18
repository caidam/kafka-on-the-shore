import pandas as pd
from confluent_kafka import Consumer, Producer,TopicPartition, KafkaException
from concurrent.futures import ThreadPoolExecutor
import signal
# import sys
import os
import threading
import json
# import time
from data_processing import process_data, store_data_s3
import traceback
import boto3
from decouple import config

def notify_event(df, producer, topic):
    # If event is 'High temperature', produce a message to another topic
    if df['event_id'].values[0] != 0:
        json_data = df.to_json()
        producer.produce(topic, value=json_data)
        print(f"Sent message for {df['name'].values[0]} with event : {df['event_name'].values[0]}")

# Create a shared flag
stop_flag = threading.Event()

# Inside your consume function
def consume(city, partition):
    c = Consumer({
        'bootstrap.servers': config('KAFKA_HOST'), #'localhost:9093',
        'group.id': 'weather-consumer-group',
        'auto.offset.reset': 'earliest'
    })

    producer = Producer({
        'bootstrap.servers': config('KAFKA_HOST'), #'localhost:9093',
        'message.timeout.ms': 5000  # Wait up to 5 seconds for message acknowledgements
        })
    
    c.assign([TopicPartition('weather', partition)])

    # Create a new boto3 session and S3 client for this consumer
    session = boto3.Session(
        aws_access_key_id=config('AWS_ACCESS_KEY'),
        aws_secret_access_key=config('AWS_SECRET_KEY'),
        region_name=config('AWS_DEFAUL_REGION')  # e.g., 'us-west-2'
    )
    s3 = session.client('s3')

    try:
        while not stop_flag.is_set():
            msg = c.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                # Proper message
                data = json.loads(msg.value().decode('utf-8'))
                # data = process_weather_data(data)
                # print(f"Processed message: {data}")
                ##

                data = process_data(data)
                print(f"Processed message for {data['name'].values[0]}, event_tracking : {data['event_name'].values[0]}")
                store_data_s3(data, config('S3_BUCKET_NAME'), s3)

                notify_event(data, producer, 'test_topic')

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"An error occurred in consumer thread: {e}")
        traceback.print_exc()
    finally:
        # Flush the producer with a timeout
        producer.flush(timeout=5.0)
        # If flush didn't finish within the timeout, purge the messages
        if len(producer) > 0:
            producer.purge()
        c.close()

# Create executor
executor = ThreadPoolExecutor(max_workers=10)

def signal_handler(signum, frame):
    print("Signal received, shutting down...")
    os._exit(0)

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)

cities = config('CITIES').split(',')  # Add more cities as needed

try:
    # Start consumers for 10 cities
    for i, city in enumerate(cities):
        executor.submit(consume, city, i)
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    executor.shutdown(wait=False)
