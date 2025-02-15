import random
import pandas as pd


def check_surreal_event(df):
    temp = df['main_temp'].values[0]
    weather_main = df['weather_main'].values[0]
    weather_desc = df['weather_description'].values[0]
    wind_speed = df['wind_speed'].values[0]
    clouds_all = df['clouds_all'].values[0]
    current_time = pd.to_datetime(df['current_time_utc'].values[0])
    hour = current_time.hour

    # Define the events
    # events = {
    #     0: ("None", "None", "None"),
    #     1: ("The Cat Whisperer", "When the temperature drops below freezing, a local resident starts speaking in 'cat language'.", "Reports are coming in of a local resident communicating in an uncharacteristic manner, reminiscent of feline communication patterns, as temperatures drop below freezing."),
    #     2: ("The Two Moons Appearance", "On clear nights with no cloud cover, two moons appear in the sky.", "Astronomical observations reveal an unusual phenomenon tonight - two celestial bodies resembling our moon are visible in the clear night sky."),
    #     3: ("The Fish Rain", "When there's a sudden downpour after a long dry spell, it 'rains' fish in a local park.", "Following a sudden downpour after a prolonged dry spell, local park-goers report an unusual occurrence - it appears to be raining fish."),
    #     4: ("The Living Spirit Walk", "On foggy mornings, residents report seeing their own spirits walking around town.", "In the early foggy morning, residents have reported sightings of apparitions bearing their own likeness wandering around town."),
    #     5: ("The Oedipus Prophecy", "When there's a thunderstorm, a local resident reports being haunted by a prophecy similar to Kafka's Oedipus prophecy.", "Amidst the thunderstorm, a local resident reports experiencing a haunting prophecy, bearing striking similarities to the Oedipus prophecy from Kafka's works."),
    #     6: ("The Entrance Stone", "On windy days, a stone in a local park is said to become a portal to another realm.", "On this windy day, a seemingly ordinary stone in a local park is reported to exhibit extraordinary properties, potentially acting as a portal to another realm."),
    #     7: ("The Timeless Library", "On days with perfect weather (not too hot, not too cold, with a light breeze), a local library is said to become timeless, with patrons losing track of time once they enter.", "On this day of perfect weather, patrons of a local library report a peculiar phenomenon - a distortion of their perception of time within the library premises."),
    #     8: ("The Music of the Wind", "When there's a strong wind, residents report hearing a beautiful, otherworldly melody carried by the wind.", "As the wind picks up, residents report hearing a captivating melody, seemingly carried by the wind itself, resonating through the air."),
    #     9: ("The Shadowless Man", "On extremely sunny days, a man is seen walking around town without casting a shadow.", "On this extremely sunny day, a man has been observed walking around town, curiously, without casting a shadow."),
    #     10: ("The Talking Crow", "During a snowfall, a crow is seen giving wise advice to passersby.", "In the midst of a snowfall, a crow has been observed engaging with passersby, seemingly imparting words of wisdom.")
    # }

    events = {
        0: ("None", "None", "None"),
        1: ("The Cat Whisperer", "A local resident starts speaking in 'cat language', leaving everyone puzzled.", "Reports are coming in of a local resident communicating in an uncharacteristic manner, reminiscent of feline communication patterns."),
        2: ("The Two Moons Appearance", "Two moons appear in the sky, causing astonishment among the locals.", "Astronomical observations reveal an unusual phenomenon tonight - two celestial bodies resembling our moon are visible."),
        3: ("The Fish Rain", "It 'rains' fish in a local park, baffling everyone present.", "Local park-goers report an unusual occurrence - it appears to be raining fish."),
        4: ("The Living Spirit Walk", "Residents report seeing their own spirits walking around town.", "Residents have reported sightings of apparitions bearing their own likeness wandering around town."),
        5: ("The Oedipus Prophecy", "A local resident reports being haunted by a prophecy similar to Kafka's Oedipus prophecy.", "A local resident reports experiencing a haunting prophecy, bearing striking similarities to the Oedipus prophecy from Kafka's works."),
        6: ("The Entrance Stone", "A stone in a local park is said to become a portal to another realm.", "A seemingly ordinary stone in a local park is reported to exhibit extraordinary properties, potentially acting as a portal to another realm."),
        7: ("The Timeless Library", "A local library is said to become timeless, with patrons losing track of time once they enter.", "Patrons of a local library report a peculiar phenomenon - a distortion of their perception of time within the library premises."),
        8: ("The Music of the Wind", "Residents report hearing a beautiful, otherworldly melody.", "Residents report hearing a captivating melody, seemingly carried by an unseen force, resonating through the air."),
        9: ("The Shadowless Man", "A man is seen walking around town without casting a shadow.", "A man has been observed walking around town, curiously, without casting a shadow."),
        10: ("The Talking Crow", "A crow is seen giving wise advice to passersby.", "A crow has been observed engaging with passersby, seemingly imparting words of wisdom.")
    }


    # Check the conditions
    if temp < 273.15 and random.random() < 0.3:  # 30% chance
        return 1, events[1]
    elif weather_main == 'Clear' and 20 <= hour < 22:  # between 8pm and 10pm
        return 2, events[2]
    elif weather_main == 'Rain' and weather_desc == 'heavy intensity rain' and random.random() < 0.25:  # 25% chance
        return 3, events[3]
    elif weather_main == 'Fog' and 6 <= hour < 9:  # between 6am and 9am
        return 4, events[4]
    elif weather_main == 'Thunderstorm' and random.random() < 0.4:  # 40% chance
        return 5, events[5]
    elif wind_speed > 6 and random.random() < 0.35:  # 35% chance
        return 6, events[6]
    elif 293.15 < temp < 298.15 and wind_speed < 3.5 and random.random() < 0.45:  # 45% chance
        return 7, events[7]
    elif wind_speed > 8 and random.random() < 0.5:  # 50% chance
        return 8, events[8]
    elif weather_main == 'Clear' and temp > 303.15 and random.random() < 0.4:  # 40% chance
        return 9, events[9]
    elif weather_main == 'Snow' and random.random() < 0.3:  # 30% chance
        return 10, events[10]
    else:
        return 0, events[0]

def process_data(data):
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
