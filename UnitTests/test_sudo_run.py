#!/usr/bin/env python3.9

"""
HARD TO TEST
not yet complete
"""

import os
import unittest

from Tuffix.SudoRun import SudoRun
from Tuffix.Exceptions import *

class TestSudoRun(unittest.TestCase):

    def test_check_user(self):
        param = 100
        runner = SudoRun()

        try:
            _is_root_valid = runner.check_user("root")
            _is_kate_valid = runner.check_user("kate")
        except EnvironmentError as error:
            # cannot find /etc/passwd
            raise AssertionError(f'{error}')
        try:
            _is_params_valid = runner.check_user(param)
        except ValueError:
            # incorrect parameters
            self.assertTrue(True)
        else:
            self.assertTrue(False)

        self.assertTrue(
            _is_root_valid and
            isinstance(_is_root_valid, bool)
        )
        self.assertFalse(
            _is_kate_valid and
            isinstance(_is_kate_valid, bool)
        )

    def test_run(self):

        bad_param = 100
        runner = SudoRun()

        try:
            _are_params_valid = runner.run(command=bad_param, desired_user=bad_param)
        except ValueError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

        try:
           _can_kate_run = runner.run(command="uname -a", desired_user="kate")
        except UnknownUserException:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

        try:
            _can_jared_run_as_root = runner.run(command="whoami", desired_user="root")
        except PrivilageExecutionException:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    # def test_chuser(self):
        # _current_guid, _current_uid = os.getgid(), os.getuid()

        # self.assertTrue(
            # (_current_guid == 0) and
            # (_current_uid == 0)
        # )

if __name__ == '__main__':
    print('[INFO] Please run as root')
    unittest.main()
