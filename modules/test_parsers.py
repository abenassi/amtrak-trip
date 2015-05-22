#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_parsers

Tests for `parsers` module.
"""

from __future__ import unicode_literals
import unittest
import nose
import arrow

from parsers import Date, Accommodation


class ParsersTest(unittest.TestCase):

    def test_date(self):

        dates = ["Monday  May 18, 2015         3:40PM",
                 "Tuesday May 19, 2015         9:45AM"]

        self.assertTrue(Date.accepts(dates[0]))
        self.assertFalse(Date.accepts("Train: 49 Lake Shore Ltd."))
        self.assertEqual(Date._parse(dates[0]), arrow.get(2015, 5, 18, 15, 40))
        self.assertEqual(Date._parse(dates[1]), arrow.get(2015, 5, 19, 9, 45))

    def test_accommodation(self):
        self.assertEqual(
            Accommodation._parse("Accommodation: 1 Reserved Coach Seat"),
            "1 Reserved Coach Seat"
        )


if __name__ == '__main__':
    nose.run(defaultTest=__name__)
