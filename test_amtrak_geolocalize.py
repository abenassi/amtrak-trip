#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_amatrak_geolocalize

Tests for `amatrak_geolocalize` module.
"""

from __future__ import unicode_literals
import unittest
# import nose

from amtrak_geolocalize import find_coordinates, _calculate_coord_diff


class AmtrakGeolocalizeTest(unittest.TestCase):

    def test_find_coordinates(self):

        coord = find_coordinates("New York (Penn Station)",
                                 "amtrk_sta/amtrk_sta")
        exp_coord = ([-73.991867, 40.74968])
        self.assertEqual(coord, exp_coord)

        coord = find_coordinates("Chicago (Chicago Union Station)",
                                 "amtrk_sta/amtrk_sta")
        exp_coord = ([-87.639168, 41.878731])
        self.assertEqual(coord, exp_coord)

    def test_calculate_coord_diff(self):

        self.assertEqual(round(_calculate_coord_diff([9, 10], [10, 10]), 7),
                         0.1)
        self.assertEqual(round(_calculate_coord_diff([9, 8], [10, 10]), 7),
                         0.2)
        self.assertEqual(round(_calculate_coord_diff([8, 9], [10, 10]), 7),
                         0.2)


if __name__ == '__main__':
    # nose.run(defaultTest=__name__)
    unittest.main()
