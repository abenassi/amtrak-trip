#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
amtrak_geolocalize

Geolocalize amtrak stations in a json file and add the coordinates.
"""

from __future__ import unicode_literals
import json
import shapefile
from fuzzywuzzy import process


def load_json_services(json_file="amtrak-trip.json"):
    with open(json_file) as f:
        return json.loads(f.read())


def geolocalize_stations(service, shp_file):

    for key, station in service.items():
        if "station" in key:
            coord_key = key.replace("station", "coordinates")
            service[coord_key] = find_coordinates(station, shp_file)


def find_coordinates(station, shp_file):

    sf = shapefile.Reader(shp_file)

    # find index of station
    stations = [record[1] for record in sf.records()]
    station_normalized = process.extractOne(station, stations)[0]
    index = stations.index(station_normalized)

    # get coordinates
    shape = sf.shapes()[index]
    coordinates = shape.points[0]
    coordinates = [round(coord, 6) for coord in coordinates]

    return coordinates


def create_line(service):
    service["the_geom"] = _coords_to_line(service["departure_coordinates"],
                                          service["arrival_coordinates"])


def _coords_to_line(origin, destination):
    return {"type": "LineString", "coordinates": [origin, destination]}


def save_new_json_services(services,
                           json_file_name="amtrak-trip-geoloc.json"):
    with open(json_file_name, "w") as f:
        f.write(json.dumps(services))


def main():
    services = load_json_services()

    for service in services:
        geolocalize_stations(service, "amtrk_sta/amtrk_sta")
        create_line(service)

    save_new_json_services(services)

if __name__ == '__main__':
    main()
