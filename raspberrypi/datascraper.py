import logging
import requests
import configparser
import time

from timeloop import Timeloop
from datetime import timedelta

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

config = configparser.ConfigParser()
config.read('datascraper.ini')
zipCode = config['Default']['ZipCode']
openWeatherApiKey = config['Default']['OpenWeatherMapApiKey']

tl = Timeloop()

@tl.job(interval=timedelta(minutes=60))
def save_open_weather_data():
    logging.info('Loading data from Open Weather')
    json = find_weather_data()
    if json != None:
        message = create_body_for_db(json)
        insert_into_db(message)
        logging.info(message)

def insert_into_db(message):
    r = requests.post('http://localhost:8086/write?db=vinduinodb&precision=s', data=message)
    if r.status_code != 204:
        logging.error('Failed to send payload to influxdb: ' + str(r.status_code) + ' ' + r.text)

def create_body_for_db(dict):
    return 'weather,host=' + zipCode + ' temp=' + str(dict['main']['temp']) \
        + ',humidity=' + str(dict['main']['humidity']) \
        + ',windSpeed=' + str(dict['wind']['speed']) \
        + ',windDirection=' + str(dict['wind']['deg']) \
        + ' ' + str(dict['dt'])

def find_weather_data():
    r = requests.get('http://api.openweathermap.org/data/2.5/weather?units=imperial&zip=' + zipCode + ',us&APPID=' + openWeatherApiKey)
    if r.status_code == 200:
        return r.json()
    else:
        logging.warn('Failed to get data from open weather ' + str(r.status_code) + ' ' + r.text)
        return None

if __name__ == "__main__":
    tl.start(block=True)
