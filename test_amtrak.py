#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_amtrak

Test methods of amtrack module.
"""

from __future__ import unicode_literals
import unittest
import nose
import arrow
import pprint

from amtrak import AmtrakServiceParser


class AmtrackServiceParserTest(unittest.TestCase):

    def test_parse_services(self):
        parser = AmtrakServiceParser()

        with open("test_trip.txt", 'rb') as f:
            for line in f.readlines():
                new_record = parser.parse(line)
                # print "parser output", new_record, line, parser.__dict__
                if new_record:
                    break

        exp_record = {
            "name": "49 Lake Shore Ltd.",
            "departure_station": "New York (Penn Station), New York",
            "departure_state": "New York",
            "departure_city": "New York",
            "departure_date": '2015-05-18T15:40:00+00:00',
            "arrival_station": "Chicago (Chicago Union Station), Illinois",
            "arrival_state": "Illinois",
            "arrival_city": "Chicago",
            "arrival_date": '2015-05-19T09:45:00+00:00',
            "accommodation": "1 Reserved Coach Seat",
        }

        for item in new_record.items():
            msg = repr(item) + " not in " + pprint.pformat(exp_record.items())
            self.assertTrue(item in exp_record.items(), msg)

    def test_service_info_complete(self):

        parser = AmtrakServiceParser()
        self.assertFalse(parser._service_info_complete())

        parser.__dict__ = {"a": "has_value"}
        self.assertTrue(parser._service_info_complete())


if __name__ == '__main__':
    # nose.run(defaultTest=__name__)
    unittest.main()
