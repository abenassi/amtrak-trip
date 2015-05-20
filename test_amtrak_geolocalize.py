#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_amatrak_geolocalize

Tests for `amatrak_geolocalize` module.
"""

from __future__ import unicode_literals
import unittest
import nose

from amtrak_geolocalize import find_coordinates


class AmtrakGeolocalizeTest(unittest.TestCase):

    def test_find_coordinates(self):

        coord = find_coordinates("New York (Penn Station)")
        exp_coord = ()
        self.assertEqual(coord, exp_coord)

        coord = find_coordinates("Chicago (Chicago Union Station)")
        exp_coord = ()
        self.assertEqual(coord, exp_coord)


if __name__ == '__main__':
    nose.run(defaultTest=__name__)
