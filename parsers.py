#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from pprint import pprint
import arrow
import parsedatetime

import strategies_helpers


class BaseParser(object):

    """Base parser class for amtrak service parsers."""

    KEY_WORD = "" or list()
    FIELD_NAME = ""

    @classmethod
    def accepts(cls, line):
        return len(line.strip()) > 0 and cls._accepts(line)

    @classmethod
    def parse(cls, line):
        return cls.FIELD_NAME, cls._parse(line)

    @classmethod
    def _parse(cls, line):
        if type(cls.KEY_WORD) == list:
            for key_word in cls.KEY_WORD:
                if key_word in line:
                    return line.replace(key_word, "").strip()

        return line.replace(cls.KEY_WORD, "").strip()

    @classmethod
    def _accepts(cls, line):
        if type(cls.KEY_WORD) == list:
            for key_word in cls.KEY_WORD:
                if key_word in line:
                    return True
        else:
            return cls.KEY_WORD in line


class Name(BaseParser):
    KEY_WORD = ["Train:", "Service:", "Bus:"]
    FIELD_NAME = "name"


class Accommodation(BaseParser):
    KEY_WORD = "Accommodation:"
    FIELD_NAME = "accommodation"


class BaseDeparture(BaseParser):
    KEY_WORD = "Departure:"


class BaseArrival(BaseParser):
    KEY_WORD = "Arrival:"


class BaseCity(BaseParser):

    @classmethod
    def _parse(cls, line):
        return line.replace(cls.KEY_WORD, "").strip().split(",")[1].strip()


class DepartureStation(BaseDeparture):
    FIELD_NAME = "departure_station"


class DepartureCity(BaseCity, BaseDeparture):
    FIELD_NAME = "departure_city"


class ArrivalStation(BaseArrival):
    FIELD_NAME = "arrival_station"


class ArrivalCity(BaseCity, BaseArrival):
    FIELD_NAME = "arrival_city"


class Date(BaseParser):
    """Parse amtrak style dates."""
    FIELD_NAME = "date"

    @classmethod
    def _accepts(cls, line):
        # print "LINE: ", line, line.split()[0] in arrow.locales.EnglishLocale.day_names
        # print "line", line, len(line)
        return line.split()[0].strip() in arrow.locales.EnglishLocale.day_names

    @classmethod
    def _parse(cls, line):
        cal = parsedatetime.Calendar()
        line_without_day = " ".join(line.split()[1:])
        dt_tuple = cal.parse(line_without_day)[0][:5]
        return arrow.get(*dt_tuple)


def get_parsers():
    return strategies_helpers.get_strategies()

if __name__ == '__main__':
    pprint(sorted(strategies_helpers.get_strategies_names()))
