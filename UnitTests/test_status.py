"""
Unit tests for Status API
AUTHOR: Jared Dyreson
"""

import unittest
from Tuffix.Status import *
from Tuffix.Exceptions import *
from subprocess import CalledProcessError

class TestCommands(unittest.TestCase):
    def test_in_VM(self):
        """
        Assuming we are running in a VM for testing
        """
        _out = in_VM()
        self.assertTrue(isinstance(_out, bool)) #change to true
        self.assertFalse(_out)

    def test_cpu_information(self):
        _out = cpu_information()
        self.assertTrue(
            isinstance(_out, str)
        )
        self.assertFalse(
            isinstance(_out, tuple)
        )

    def test_host(self):
        _out = host()
        self.assertTrue(isinstance(_out, str))

        _re = re.compile("([\w|\W]+)\@([\w|\W]+)")
        _match = _re.match(_out)
        self.assertTrue(
            _match
        )

    def test_current_operating_system(self):
        try:
            _os = current_operating_system()
        except EnvironmentError as error:
            raise AssertionError(f'{error}')

        self.assertTrue(isinstance(_os, str))

    def test_current_kernel_revision(self):
        self.assertTrue(isinstance(current_kernel_revision(), str))

    def test_current_time(self):
        self.assertTrue(isinstance(current_time(), str))

    def test_current_model(self):

        try:
            _model = current_model()
        except EnvironmentError as error:
            raise AssertionError(f'{error}')
        self.assertTrue(isinstance(_model, str))

    def test_current_uptime(self):
        try:
            _time = current_uptime()
        except(EnvironmentError, ValueError) as error:
            # cannot find proper device files (see Tuffix/Status:114-116)
            # parsing error in /proc/uptime
            raise AssertionError(f'{error}')

        self.assertTrue(isinstance(_time, str))

    def test_memory_information(self):
        try:
            _mem_info = memory_information()
        except(EnvironmentError, ValueError) as error:
            # cannot find meminfo
            # parsing error in /proc/meminfo
            raise AssertionError(f'{error}')

        self.assertTrue(isinstance(_mem_info, int))

    def test_graphics_information(self):
        try:
            _graphics_information = graphics_information()
        except EnvironmentError as error:
            # could not find bash or lspci
            raise AssertionError(f'{error}')

        self.assertTrue(
            isinstance(_graphics_information, tuple) and
            (len(_graphics_information) == 2)
        )
        _mem_info = [True if(isinstance(element, str)) else False for element in _graphics_information]

        self.assertTrue(
            all(_mem_info)
        )

    def test_git_configuration(self):
        try:
            _git_information = list_git_configuration()
        except EnvironmentError as error:
            raise AssertionError(f'{error}')

        self.assertTrue(
            isinstance(_git_information, tuple) and
            (len(_git_information) == 2)
        )

        _git_information = [True if(isinstance(element, str)) else False for element in _git_information]
        self.assertTrue(
            all(_git_information)
        )

    def test_has_internet(self):
        try:
            _internet_information = has_internet()
        except (EnvironmentError, ValueError) as error:
            # not linux
            # parsing error

            raise AssertionError(f'{error}')

        self.assertTrue(
            isinstance(_internet_information, bool)
        )

    def test_currently_installed_targets(self):
        try:
            _targets = currently_installed_targets()
        except Exception as error:
            # error in read_state
            raise AssertionError(f'{error}')
        self.assertTrue(
            isinstance(_targets, list)
        )

    def test_status(self):
        try:
            _status = status()
        except Exception as error:
            # general exception, too much can go wrong here
            raise AssertionError(f'{error}')
        self.assertTrue(
            isinstance(_status, tuple)
        )

    def test_system_shell(self):
        try:
            _shell = system_shell()
        except (EnvironmentError, ValueError) as error:
            # not unix
            # cannot parse /etc/passwd or shell version
            raise AssertionError(f'{error}')
        self.assertTrue(
            isinstance(_shell, str)
        )

    def test_terminal_emulator(self):
        try:
            _emulator = system_terminal_emulator()
        except ValueError as error:
            # shell output parsing error
            raise AssertionError(f'{error}')
        self.assertTrue(
            isinstance(_emulator, str)
        )

if __name__ == '__main__':
    unittest.main()
