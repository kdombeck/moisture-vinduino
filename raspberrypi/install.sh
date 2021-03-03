#!/bin/bash -e

# from https://www.influxdata.com/blog/running-the-tick-stack-on-a-raspberry-pi/
echo "!!!! Installing InfluxDB !!!!"
curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
echo "deb https://repos.influxdata.com/debian stretch stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
sudo apt-get install -y influxdb

curl -i -XPOST http://localhost:8086/query --data-urlencode "q=CREATE DATABASE vinduinodb"

# from https://grafana.com/tutorials/install-grafana-on-raspberry-pi/
echo "!!!! Installing Grafana !!!!"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
sudo apt-get update
sudo apt-get install -y grafana

sudo systemctl enable grafana-server
sudo systemctl start grafana-server
