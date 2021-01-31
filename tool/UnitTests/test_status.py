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
        self.assertTrue(isinstance(_out, bool))
        self.assertTrue(_out)

    def test_cpu_information(self):
        _out = cpu_information()
        self.assertTrue(
            isinstance(_out, bool)
        )
        self.assertFalse(
            isinstance(_out, tuple)
        )

    def test_host(self):
        _out = host()
        self.assertTrue(isinstance(_out, bool))

        _re = re.compile("([\w|\W]+)\@([\w|\W]+)")
        _match = _re.match(_out)
        self.assertTrue(
            _match
        )

    def test_current_operating_system(self):
        with self.assertRaises(EnvironmentError) as context:
            current_operating_system()
        self.assertFalse(context.exception == EnvironmentError)

        _os = current_operating_system()
        self.assertTrue(isinstance(_os, str))

    def test_current_kernel_revision(self):
        self.assertTrue(isinstance(current_kernel_revision(), str))

    def test_current_time(self):
        self.assertTrue(isinstance(current_time(), str))

    def test_current_model(self):
        with self.assertRaises(EnvironmentError) as context:
            model = current_operating_system()
        self.assertFalse(context.exception == EnvironmentError)
        self.assertTrue(isinstance(model, str))

    def test_current_uptime(self):
        with self.assertRaises((EnvironmentError, ValueError)) as context:
            _time = current_uptime()
        self.assertFalse(
            (context.exception == EnvironmentError) or
            (context.exception == ValueError) # parsing error in /proc/uptime
        )
        self.assertTrue(isinstance(_time, str))

    def test_memory_information(self):
        with self.assertRaises((EnvironmentError, ValueError)) as context:
            _mem_info = memory_information()
        self.assertFalse(
            (context.exception == EnvironmentError) or
            (context.exception == ValueError) # parsing error in /proc/meminfo
        )
        self.assertTrue(isinstance(_mem_info, int))

    def test_graphics_information(self):
        with self.assertRaises(EnvironmentError) as context:
            _mem_info = graphics_information()
        self.assertFalse(
            (context.exception == EnvironmentError)
        )
        self.assertTrue(
            isinstance(_mem_info, tuple) and
            (len(_mem_info) == 2)
        )
        primary, secondary = _mem_info
        _mem_info = [True for element in _mem_info if isinstance(element, str) else  False]

        self.assertTrue(
            all(_mem_info)
        )

    def test_git_configuration(self):
        with self.assertRaises(EnvironmentError) as context: # git not installed
            _git_information = list_git_configuration()

        self.assertFalse(
            (context.exception == EnvironmentError)
        )
        self.assertTrue(
            isinstance(_git_information, tuple) and
            (len(_git_information) == 2)
        )

        _git_information = [True for element in _git_information if isinstance(element, str) else False]

        self.assertTrue(
            all(_git_information)
        )

    def test_has_internet(self):
        with self.assertRaises((EnvironmentError, OSError, ValueError)) as context:
            _internet_information = has_internet()
        self.assertFalse(
            (context.exception == EnvironmentError) and # not linux
            (context.exception == OSError) and # file not found
            (context.exception == ValueError) # parsing error
        )
        self.assertTrue(
            isinstance(_internet_information, bool)
        )

if __name__ == '__main__':
    unittest.main()
