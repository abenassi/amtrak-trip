#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
amtrak_geolocalize

Geolocalize amtrak stations in a json file and create a line for each service.

This module takes a json file of amtrak services parsed with `amtrak.py` and
creates two new georreferenced files: one with points (being the stations of
the trip) and one with lines (being the services between the stations). Both
files are dumped into geojson (usable with CartoDB and other mapping services)
and json (easier to read the information if is not to be used for mapping)
formats.

You should first use `amtrak.py` to parse the itinerary.
Example:
    $ python amtrak.py

and then use `amtrak_geolocalize.py` to convert it into something mappable.
Example:
    $ python amtrak_geolocalize.py

    import amtrak_geolocalize
    amtrak_geolocalize.main()

TODO: find amtrak real rail path (shortest path? amtrak routes dataset? after
trip data?).
"""

from __future__ import unicode_literals
import json
import shapefile
from fuzzywuzzy import process
import arrow
import requests
import os
from pprint import pprint
# from graph import rail_graph


def load_services(file_name="./json/amtrak-trip.json"):
    """Load a json file with parsed services from an amtrak itinerary."""
    with open(file_name) as f:
        return json.loads(f.read())


def geolocalize_stations(service, shp_file="amtrk_sta/amtrk_sta"):
    """Add coordinates to each station found in a service.

    Args:
        service (dict): A parsed amtrak service.
        shp_file (str): Path to a shapefile of amtrak stations.
    """

    for key, station in service.items():
        if "station" in key:
            coord_key = key.replace("station", "coordinates")
            service[coord_key] = find_coordinates(station, shp_file)


def correct_time_zones(service):
    """Correct parsed dates with corresponding time zones.

    Uses the coordinates found for every station and the Google Time Zone API
    to rewrite the dates adding time zone information

    Args:
        service (dict): A parsed amtrak service.
    """

    for key, coordinates in service.items():
        if "coordinates" in key:
            arrival_or_depart = key.replace("_coordinates", "")
            date_key = arrival_or_depart + "_date"
            date = arrow.get(service[date_key])
            timestamp = date.timestamp

            tzinfo = _get_tz(coordinates, timestamp)
            dt_tuple = (date.year, date.month, date.day, date.hour,
                        date.minute)

            service[date_key] = arrow.get(*dt_tuple, tzinfo=tzinfo).isoformat()


def _get_tz(coordinates, timestamp):
    """Get the timezone of a point in a certain time.

    Use the Google Time Zone API to get it.

    Args:
        coordinates (list): Given coordinates [lon, lat].
        timestamp (int): Unix timestamp (necessary to retrieve take into
            account Daylight Saving Time schemes).
    """

    payload = {"location": ",".join([unicode(i) for i in
                                     reversed(coordinates)]),
               "timestamp": timestamp,
               "key": os.environ["GOOGLE_API_KEY"]}
    url = "https://maps.googleapis.com/maps/api/timezone/json"

    return requests.get(url, payload).json()["timeZoneId"]


def add_duration(service):
    """Write the duration of a service into an new field."""
    service["duration"] = _calc_duration(service)
    return service


def _calc_duration(service):
    """Calculates the duration of a service."""
    duration = arrow.get(service["arrival_date"]) - \
        arrow.get(service["departure_date"])
    return round(duration.total_seconds() / 60 / 60, 1)


def find_coordinates(station, shp_file="amtrk_sta/amtrk_sta"):
    """Find coordinates for a given amtrak station.

    Args:
        station (str): Amtrak station.
        shp_file (str): Path to a shapefile of amtrak stations.
    Returns:
        list: Coordinates pulled from the amtrak stations shapefile
            [-122.29068, 37.840679]
            [lon, lat]
    """

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
    """Create a line from departure station to arrival station of a service."""
    return _coords_to_line(service["departure_coordinates"],
                           service["arrival_coordinates"])


def _coords_to_line(origin, destination):
    """Create geojson formated line from 2 points."""
    return {"type": "MultiLineString", "coordinates": [[origin, destination]]}


def create_point(coordinates):
    """Create geojson formated point from lon and lat coordiantes."""
    return {"type": "Point", "coordinates": coordinates}


def load_amtrak_path(service, graph):
    """TODO: It will load a real amtrak path for a service."""
    return _find_amtrak_path(service["departure_coordinates"],
                             service["arrival_coordinates"],
                             graph)


def _find_amtrak_path(origin, destination, graph):
    """
    TODO

    1. Identify origin and destination ids in rail_nodes shapefile
    2. Build rail_lines graph
    3. Find shortest path in rail_lines graph from O to D
    4. Build MultiLineString geojson from rail_lines graph shortest path
        identified
    """

    id_origin = _get_node_id(origin)
    id_destination = _get_node_id(destination)
    path = graph.find_shortest_path(id_origin, id_destination)
#
    return _path_to_geojson(path)


def _get_node_id(coordinates):
    """Find a node id in the US rail_nodes shapefile given some coordinates."""

    sf_nodes = shapefile.Reader("rail/rail_nodes")
    points_generator = (shape.points[0] for shape in sf_nodes.iterShapes())
    index = _find_aprox_coord(coordinates, points_generator)

    if index != -1:
        # return (sf_nodes.record(index), coordinates,
                # sf_nodes.shape(index).points[0])
        return sf_nodes.record(index)[0]
    else:
        return None


def _find_aprox_coord(coordinates, points_generator, threshold=0.001):
    """Find the index of the closest point given some coordinates.

    Iterate a points generator based on a shapefile trying to find the closest
    point to some coordiantes with a threshold of maximum difference between
    any of the coordinates (lon or lat).

    Args:
        coordinates (list): Given coordinates [lon, lat]
        points_generator (generator): Yields coordinates [lon, lat] from a
            shapefile.
        threshold (float): Maximum percentual difference acceptable between any
            coordinate (lon or lat).
    Returns:
        int: Index of the closest point or -1 if none is found within the
            constraint given by the difference threshold.
    """

    return_index, min_diff = -1, threshold
    for index, coord in enumerate(points_generator):
        diff = _calculate_coord_diff(coordinates, coord)
        if diff < min_diff:
            return_index, min_diff = index, diff

    return return_index


def _calculate_coord_diff(coord_a, coord_b):
    """Calculate the percentual difference between two coordinates.

    It will be the maximum after comparing lon and lat coordinates.

    Args:
        coord_a, coord_b (list): Given coordinates [lon, lat]
    """
    diff_x = abs(float(coord_a[0]) / coord_b[0] - 1)
    diff_y = abs(float(coord_a[1]) / coord_b[1] - 1)
    # print coord_a, coord_b, diff_x, diff_y
    return max(diff_x, diff_y)


def _path_to_geojson(path):
    pass


def to_geojson_format(services):
    """Convert a services list in a geojson formated dict.

    Args:
        services (list): Services with a geojson formated 'the_geom' field.
    Returns:
        dict: Formated like a geojson file.
    """
    geojson_dict = {"type": "FeatureCollection",
                    "features": []}
    for service in services:
        geometry = service["the_geom"]
        del service["the_geom"]
        geojson_service = {"type": "Feature", "geometry": geometry,
                           "properties": service}
        geojson_dict["features"].append(geojson_service)

    return geojson_dict


def write_services_to_json(services,
                           file_name="./json/amtrak-trip-geoloc.json"):
    with open(file_name, "w") as f:
        f.write(json.dumps(services, indent=4))


def main():
    services = load_services()

    points_dict = {}
    for service in services:

        # create lines dict
        geolocalize_stations(service)
        correct_time_zones(service)
        add_duration(service)
        service["the_geom"] = create_line(service)
        # service["the_geom"] = load_amtrak_path(service)

        # create points dict
        if service["departure_city"] not in points_dict:
            points_dict[service["departure_city"]] = {}
        if service["arrival_city"] not in points_dict:
            points_dict[service["arrival_city"]] = {}

        # process departure data of the service
        points_dict[service["departure_city"]]["state"] = \
            service["departure_state"]
        points_dict[service["departure_city"]]["city"] = \
            service["departure_city"]
        points_dict[service["departure_city"]]["departure_station"] = \
            service["departure_station"]
        points_dict[service["departure_city"]]["departure_date"] = \
            service["departure_date"]
        points_dict[service["departure_city"]]["the_geom"] = \
            create_point(service["departure_coordinates"])

        # process arrival data of the service
        points_dict[service["arrival_city"]]["state"] = \
            service["arrival_state"]
        points_dict[service["arrival_city"]]["city"] = \
            service["arrival_city"]
        points_dict[service["arrival_city"]]["arrival_station"] = \
            service["arrival_station"]
        points_dict[service["arrival_city"]]["arrival_date"] = \
            service["arrival_date"]
        points_dict[service["arrival_city"]]["the_geom"] = \
            create_point(service["arrival_coordinates"])

    # create points json and geojson files
    # pprint(points_dict)
    write_services_to_json(points_dict.values(),
                           "./json/amtrak-trip-points.json")
    geojson_dict = to_geojson_format(points_dict.values())
    write_services_to_json(geojson_dict,
                           "./geojson/amtrak-trip-points.geojson")

    # create lines json and geojson files
    write_services_to_json(services, "./json/amtrak-trip-lines.json")
    # pprint(services)
    geojson_dict = to_geojson_format(services)
    write_services_to_json(geojson_dict, "./geojson/amtrak-trip-lines.geojson")


if __name__ == '__main__':
    main()
