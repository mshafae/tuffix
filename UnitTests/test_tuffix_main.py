#!/usr/bin/env python3.9

from tuffixdriver import main
from Tuffix.Configuration import BuildConfig, DEFAULT_BUILD_CONFIG
from Tuffix.Exceptions import *

import unittest

class TestTuffixMain(unittest.TestCase):
    def test_input(self):
        try:
            arguments = ['help']
            main(DEFAULT_BUILD_CONFIG, arguments)
        except ValueError:
            self.assertTrue(False)
        else:
            self.assertTrue(True)

    def test_amount_of_arguments_empty(self):
        try:
            arguments = []
            main(DEFAULT_BUILD_CONFIG, arguments)
        except UsageError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_unavailable_command(self):
        """
        test if command does not work or the command is unavailable
        """

        try:
            arguments = ["eat", "cookies"]
            main(DEFAULT_BUILD_CONFIG, argument)
        except (MessageException, UsageError):
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_install_test_package(self):
        """
        test if command does not work or the command is unavailable
        """

        try:
            arguments = ["install", "test"]
            main(DEFAULT_BUILD_CONFIG, argument)
        except (MessageException, UsageError):
            self.assertTrue(True)
        else:
            self.assertTrue(False)

if __name__ == '__main__':
    unittest.main()
