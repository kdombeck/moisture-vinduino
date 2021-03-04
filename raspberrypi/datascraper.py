import logging
import requests
import configparser
import time
import dateutil.parser

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

config = configparser.ConfigParser()
config.read('datascraper.ini')
zipCode = config['Default']['ZipCode']
openWeatherApiKey = config['Default']['OpenWeatherMapApiKey']
theThingsNetworkDataStorageAccessKey = config['Default']['TheThingsNetworkDataStorageAccessKey']

def save_open_weather_data():
    logging.info('Loading data from Open Weather')
    r = requests.get('http://api.openweathermap.org/data/2.5/weather?units=imperial&zip=' + zipCode + ',us&APPID=' + openWeatherApiKey)
    if r.status_code == 200:
        message = create_body_for_db(r.json())
        logging.info(message)
        insert_into_db(message)
        return r.json()
    else:
        logging.warn('Failed to get data from open weather ' + str(r.status_code) + ' ' + r.text)

def insert_into_db(message):
    r = requests.post('http://localhost:8086/write?db=vinduinodb&precision=s', data=message)
    if r.status_code != 204:
        logging.error('Failed to send payload to influxdb: ' + str(r.status_code) + ' ' + r.text)

def create_body_for_db(dict):
    return 'weather,zip=' + zipCode + ' temp=' + str(dict['main']['temp']) \
        + ',humidity=' + str(dict['main']['humidity']) \
        + ',windSpeed=' + str(dict['wind']['speed']) \
        + ',windDirection=' + str(dict['wind']['deg']) \
        + ' ' + str(dict['dt'])

def save_the_things_network_data():
    logging.info('Loading data from The Things Network')
    r = requests.get('https://vinduino-moisture.data.thethingsnetwork.org/api/v2/query?last=12h', headers={'Authorization': 'key ' + theThingsNetworkDataStorageAccessKey})
    if r.status_code == 200:
        message = save_the_thing_network_response_to_db(r.json())
        insert_into_db(message)
        return r.json()
    else:
        logging.warn('Failed to get data from the things network ' + str(r.status_code) + ' ' + r.text)

def save_the_thing_network_response_to_db(dict):
    for entry in dict:
        influxdb = 'vinduino,device=' + str(entry['device_id']) + ' temp=' + str(entry['temp']) \
            + ',voltage=' + str(entry['voltage']) \
            + ',moisture1=' + str(entry['moisture1']) \
            + ',moisture2=' + str(entry['moisture2']) \
            + ',moisture3=' + str(entry['moisture3']) \
            + ',moisture4=' + str(entry['moisture4']) \
            + ' ' + str(int(dateutil.parser.isoparse(str(entry['time'])).timestamp()))
        logging.info('inserting TTN ' + influxdb)
        insert_into_db(influxdb)

if __name__ == "__main__":
    save_the_things_network_data()
    save_open_weather_data()
