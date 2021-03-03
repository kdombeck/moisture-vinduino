#!/bin/bash -e

# from https://www.influxdata.com/blog/running-the-tick-stack-on-a-raspberry-pi/
echo "!!!! Installing InfluxDB !!!!"
curl -sL https://repos.influxdata.com/influxdb.key | apt-key add -
echo "deb https://repos.influxdata.com/debian stretch stable" | tee /etc/apt/sources.list.d/influxdb.list
apt-get install -y influxdb

curl -i -XPOST http://localhost:8086/query --data-urlencode "q=CREATE DATABASE vinduinodb"

# from https://grafana.com/tutorials/install-grafana-on-raspberry-pi/
echo "!!!! Installing Grafana !!!!"
wget -q -O - https://packages.grafana.com/gpg.key | apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | tee -a /etc/apt/sources.list.d/grafana.list
apt-get update
apt-get install -y grafana

systemctl enable grafana-server
systemctl start grafana-server

curl -X POST --user admin:admin localhost:3000/api/datasources -H 'Content-Type: application/json' -d '{"name":"Sensor Database","type":"influxdb","access":"proxy","url":"http://localhost:8086","database":"vinduinodb"}'
# curl -X POST --user admin:admin localhost:3000/api/dashboards/db -H 'Content-Type: application/json' -d @grafanaDashboard.json

echo "!!!! Installing Data Scraper !!!!"
apt install python3-pip
pip install requests timeloop

cp datascraper.py /usr/bin/datascraper.py
cp datascraper.ini /usr/bin/datascraper.ini
cp datascraper.service /etc/systemd/system/datascraper.service

echo 'Enter in your zip code:'
read zipCode
sed -i "s/ZipCode =/ZipCode = $zipCode/" /usr/bin/datascraper.ini

echo 'Enter in your http://openweathermap.org/ api key:'
read apiKey
sed -i "s/OpenWeatherMapApiKey =/OpenWeatherMapApiKey = $apiKey/" /usr/bin/datascraper.ini

systemctl enable datascraper
systemctl start datascraper
