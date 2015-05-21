#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
amtrak_geolocalize

Geolocalize amtrak stations in a json file, add their coordinates, add the_geom
field with a LineString.

TODO: find amtrak real rail path.
"""

from __future__ import unicode_literals
import json
import shapefile
from fuzzywuzzy import process
from pprint import pprint

# from graph import rail_graph


def load_json_services(json_file="amtrak-trip.json"):
    with open(json_file) as f:
        return json.loads(f.read())


def geolocalize_stations(service, shp_file="amtrk_sta/amtrk_sta"):

    for key, station in service.items():
        if "station" in key:
            coord_key = key.replace("station", "coordinates")
            service[coord_key] = find_coordinates(station, shp_file)


def find_coordinates(station, shp_file="amtrk_sta/amtrk_sta"):

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
    return _coords_to_line(service["departure_coordinates"],
                           service["arrival_coordinates"])


def _coords_to_line(origin, destination):
    return {"type": "MultiLineString", "coordinates": [[origin, destination]]}


def create_point(coordinates):
    return {"type": "Point", "coordinates": coordinates}


def load_amtrak_path(service, graph):
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

    id_origin = _get_amtrak_node_id(origin)
    id_destination = _get_amtrak_node_id(destination)
    path = graph.find_shortest_path(id_origin, id_destination)
#
    return _path_to_geojson(path)


def _get_amtrak_node_id(coordinates):

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

    return_index, min_diff = -1, threshold
    for index, coord in enumerate(points_generator):
        diff = _calculate_coord_diff(coordinates, coord)
        if diff < min_diff:
            return_index, min_diff = index, diff

    return return_index


def _calculate_coord_diff(coord_a, coord_b):
    diff_x = abs(float(coord_a[0]) / coord_b[0] - 1)
    diff_y = abs(float(coord_a[1]) / coord_b[1] - 1)
    # print coord_a, coord_b, diff_x, diff_y
    return max(diff_x, diff_y)


def _path_to_geojson(path):
    pass


def to_geojson_format(services):
    geojson_dict = {"type": "FeatureCollection",
                    "features": []}
    for service in services:
        geometry = service["the_geom"]
        del service["the_geom"]
        geojson_service = {"type": "Feature", "geometry": geometry,
                           "properties": service}
        geojson_dict["features"].append(geojson_service)

    return geojson_dict


def save_new_json_services(services,
                           json_file_name="amtrak-trip-geoloc.json"):
    with open(json_file_name, "w") as f:
        f.write(json.dumps(services, indent=4))


def main():
    services = load_json_services()

    points_dict = {}
    for service in services:

        # create lines dict
        geolocalize_stations(service)
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
        points_dict[service["departure_city"]]["departure_station"] = \
            service["departure_station"]
        points_dict[service["departure_city"]]["departure_date"] = \
            service["departure_date"]
        points_dict[service["departure_city"]]["the_geom"] = \
            create_point(service["departure_coordinates"])

        # process arrival data of the service
        points_dict[service["arrival_city"]]["state"] = \
            service["arrival_state"]
        points_dict[service["arrival_city"]]["arrival_station"] = \
            service["arrival_station"]
        points_dict[service["arrival_city"]]["arrival_date"] = \
            service["arrival_date"]
        points_dict[service["arrival_city"]]["the_geom"] = \
            create_point(service["arrival_coordinates"])


    # create points json and geojson files
    # pprint(points_dict)
    save_new_json_services(points_dict.values(), "amtrak-trip-points.json")
    geojson_dict = to_geojson_format(points_dict.values())
    save_new_json_services(geojson_dict, "amtrak-trip-points.geojson")

    # create lines json and geojson files
    save_new_json_services(services, "amtrak-trip-lines.json")
    # pprint(services)
    geojson_dict = to_geojson_format(services)
    save_new_json_services(geojson_dict, "amtrak-trip-lines.geojson")


if __name__ == '__main__':
    main()
