#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
amtrak

Parse a trip itinerary of amtrak services copied into a text file.

Example:
    $ python amtrak.py
    whill take a trip.txt file and output a .json with one record for each
    amtrak service in the trip.
"""

from __future__ import unicode_literals
import copy
import json
import parsers
import arrow
import sys


class AmtrakServiceParser(object):

    """Parse Amtrak service information from confirmation email lines."""

    def __init__(self):
        self.name = None
        self.departure_station = None
        self.departure_state = None
        self.departure_date = None
        self.arrival_station = None
        self.arrival_state = None
        self.arrival_date = None
        self.accommodation = None

    def parse(self, line):

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

    parser = AmtrakServiceParser()

    with open(filename, 'rb') as f:
        for line in f.readlines():
            new_record = parser.parse(line)

            if new_record:
                yield new_record


def add_calc_fields(service):
    service["duration"] = calc_duration(service)
    return service


def calc_duration(service):
    duration = arrow.get(service["arrival_date"]) - \
        arrow.get(service["departure_date"])
    return round(duration.total_seconds() / 60 / 60, 1)


def save_new_json_services(services, json_file_name="amtrak-trip.json"):
    with open(json_file_name, "w") as f:
        f.write(json.dumps(services))


def main(filename='trip.txt'):
    services = [add_calc_fields(service) for service
                in parse_services(filename)]
    save_new_json_services(services)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[2])
    else:
        main()
