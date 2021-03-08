#!/bin/bash -e

influxd backup -portable -db vinduinodb  -host localhost:8088 .
