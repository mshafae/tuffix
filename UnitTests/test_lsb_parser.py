#!/usr/bin/env python3.9

"""
pure Python equivalent of lsb_release, because I wanted to OKAY?
inspiration from this: https://chromium.googlesource.com/chromiumos/docs/+/HEAD/lsb-release.md
AUTHOR: Jared Dyreson
"""

from Tuffix.LSBParser import lsb_parser
import unittest

class LSBTest(unittest.TestCase):
    def test_constructor(self):
        try:
            # I don't want to keep instaiting it each time
            # we know it works because it is the first test
            # I KNOW THIS IS BAD PRACTICE

            global _lsb_parser
            _lsb_parser = lsb_parser()
        # cannot find the file or syntax error
        except EnvironmentError as error:
            raise AssertionError(f'{error}')

    def test_load(self):
        global _lsb_content
        _lsb_content = _lsb_parser.file_map

        self.assertTrue(
            isinstance(_lsb_content, dict)
        )

    def test_lsb_version(self):
        try:
            _version = _lsb_parser.lsb_version()
        except ValueError as error:
            # parsing error
            self.assertTrue(False)
        else:
            self.assertTrue(True)

        self.assertTrue(
            isinstance(_version, float)
        )

    def test_lsb_id(self):
        _id = _lsb_parser.lsb_id()

        self.assertTrue(
            isinstance(_id, str)
        )

    def test_lsb_type(self):
        _type = _lsb_parser.lsb_release_type()

        self.assertTrue(
            isinstance(_type, str)
        )

    def test_lsb_description(self):
        _description = _lsb_parser.lsb_distrib_description()

        self.assertTrue(
            isinstance(_description, str)
        )

if __name__ == '__main__':
    unittest.main()
