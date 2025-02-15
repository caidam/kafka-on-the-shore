from confluent_kafka import Producer
from openweather_utils import get_weather_data
import time
import datetime
import random
import json
from decouple import config


def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}] {msg.key()}')

# p = Producer({'bootstrap.servers': 'localhost:9093'})
p = Producer({'bootstrap.servers': config('KAFKA_HOST')})

cities = config('CITIES').split(',')

# Assign a fixed partition number to each city
city_partitions = {city: i for i, city in enumerate(cities)}

def send_weather_data(city, data):
    # Use the city's assigned partition number when producing the message
    p.produce('weather', key=city, value=str(data), partition=city_partitions[city], callback=delivery_report)


# group triggers 5, 15 minutes
# while True:
#     try:
#         # Fetch and send weather data for each city
#         for city in cities:
#             data = get_weather_data(city)
#             print(json.loads(data)['name'])
#             send_weather_data(city, data)
#         p.flush()

#         # Sleep for a random interval between 5 to 15 minutes
#         t = random.randint(5, 15) * 60
#         current_time = datetime.datetime.now()
#         next_message_time = current_time + datetime.timedelta(seconds=t)

#         print(f'{current_time.strftime("%H:%M:%S")} | Next messages in {t / 60} mn | @ {next_message_time.strftime("%H:%M:%S")}')
#         time.sleep(t)

#     except KeyboardInterrupt:
#         print("Stopping producer...")
#         break
#     except Exception as e:
#         print(f"An error occurred: {e}")

# sub minute interval
while True:
    try:
        # Fetch and send weather data for each city
        for city in cities:
            data = get_weather_data(city)
            print(json.loads(data)['name'])
            send_weather_data(city, data)
        p.flush()

        # Sleep for a random interval between 10 to 30 seconds
        t = random.randint(10, 30)
        current_time = datetime.datetime.now()
        next_message_time = current_time + datetime.timedelta(seconds=t)

        print(f'{current_time.strftime("%H:%M:%S")} | Next messages in {t} seconds | @ {next_message_time.strftime("%H:%M:%S")}')
        time.sleep(t)

    except KeyboardInterrupt:
        print("Stopping producer...")
        break
    except Exception as e:
        print(f"An error occurred: {e}")

