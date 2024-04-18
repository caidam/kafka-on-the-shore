
import requests
import datetime
import json
from decouple import config

def get_weather_data(city_name) :
    # Replace 'your_api_key' with your actual API key
    api_key = config('WEATHER_API_KEY')
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    # Given a city name
    # city_name = city_name

    # complete_url variable to store complete url address
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name

    # get method of requests module and return response object
    response = requests.get(complete_url)

    # json method of response object convert json format data into python format data
    data = response.json()
    # print(data)

    # Get the current time in ISO format
    current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Add the current time to your data
    data['current_time_utc'] = current_time 

    json_output = json.dumps(data, indent=4)
    print(json_output)
    # print(data)
    return json_output
    # return data

if __name__ == "__main__":
    
    # city_name = 'London, uk'
    cities = config('CITIES').split(',')
    city = cities[0]
    get_weather_data(city)