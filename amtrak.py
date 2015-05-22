#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
amtrak

Parse a trip itinerary of amtrak services copied into a text file.

Running the file will take a trip.txt file and output a .json with one record
for each amtrak service in the trip. You can also use the main method of the
module. Both cases, the first parameter would be the input and the second one
would be the output.

Example:
    $ python amtrak.py
    $ python amtrak.py trip.txt
    $ python amtrak.py trip.txt /json/amtrak-trip.json

    import amtrak
    amtrak.main()
    amtrak.main("trip.txt")
    amtrak.main("trip.txt", "/json/amtrak-trip.json")

See the "trip.txt" file in this directory for an example of the type of amtrak
itinerary e-mail that is supported for the parsers in this repo.
"""

from __future__ import unicode_literals
import copy
import json
import arrow
import sys

from modules import parsers


class AmtrakServiceParser(object):

    """Parse Amtrak service information from confirmation email lines.

    Attributes:
        name (str): Name of the service.
        departure_station (str): Station where the service starts.
        departure_state (str): State where the service starts.
        departure_city (str): City where the service starts.
        departure_date (str): Date and time when the service starts.
        arrival_station (str): Station where the service ends.
        arrival_state (str): State where the service ends.
        arrival_city (str): City where the service ends.
        arrival_date (str): Date and time when the service ends.
        accommodation (str): Type of accommodation.
    """

    def __init__(self):
        self.name = None
        self.departure_station = None
        self.departure_state = None
        self.departure_city = None
        self.departure_date = None
        self.arrival_station = None
        self.arrival_state = None
        self.arrival_city = None
        self.arrival_date = None
        self.accommodation = None

    def parse(self, line):
        """Parse one line of the amtrak itinerary.

        It will add information to the parser until last item has been parsed,
        then it will return a new record and clean the parser from any data.

        Args:
            line (str): A line of an amtrak itinerary.

        Returns:
            dict: All the information parsed of a single service.

            Example:
                {"name": "49 Lake Shore Ltd.",
                "departure_station": "New York (Penn Station), New York",
                "departure_state": "New York",
                "departure_city": "New York",
                "departure_date": '2015-05-18T15:40:00+00:00',
                "arrival_station": "Chicago (Chicago Union Station), Illinois",
                "arrival_state": "Illinois",
                "arrival_city": "Chicago",
                "arrival_date": '2015-05-19T09:45:00+00:00',
                "accommodation": "1 Reserved Coach Seat"}
        """

        for parser in parsers.get_parsers():
            if parser.accepts(line):
                key, value = parser.parse(line)

                if not key == "date":
                    self.__dict__[key] = value

                # date could be departure or arrival, departure is always first
                else:
                    if not self.departure_date:
                        self.departure_date = value.isoformat()
                    else:
                        self.arrival_date = value.isoformat()

        if self._service_info_complete():
            RV = copy.copy(self.__dict__)
            self.__init__()
        else:
            RV = None

        return RV

    def _service_info_complete(self):
        for value in self.__dict__.values():
            if not value:
                return False
        return True


def parse_services(filename='trip.txt'):
    """Parse all services from an amtrak itinerary.

    Args:
        filename (str): Path to a text file with an amtrak itinerary.

    Yields:
        dict: New record with data about a service.
    """

    parser = AmtrakServiceParser()

    with open(filename, 'rb') as f:
        for line in f.readlines():
            new_record = parser.parse(line)

            if new_record:
                yield new_record


def add_calc_fields(service):
    """Write the duration of a service into an new field."""
    service["duration"] = _calc_duration(service)
    return service


def _calc_duration(service):
    """Calculates the duration of a service."""
    duration = arrow.get(service["arrival_date"]) - \
        arrow.get(service["departure_date"])
    return round(duration.total_seconds() / 60 / 60, 1)


def write_services_to_json(services, file_name="./json/amtrak-trip.json"):
    """Write parsed services to a json file.

    Args:
        services (dict): Parsed services.
        file_name (str): Path of the json file to write in.
    """
    with open(file_name, "w") as f:
        f.write(json.dumps(services, indent=4))


def main(filename='trip.txt', file_name="./json/amtrak-trip.json"):
    services = [add_calc_fields(service) for service
                in parse_services(filename)]
    write_services_to_json(services, file_name)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        main()
