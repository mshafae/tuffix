##########################################################################
# configuration
# AUTHOR(S): Kevin Wortman
##########################################################################

"""
NOTE:

I attempted to convert these comments to docstrings but this seemed to be
pointless on my part.
It was mostly done to get `help` messages to display nicely and I am a sucker for
nice formatting.
Let me know if I should continue on this endevor.
"""

from Tuffix.Exceptions import *
from Tuffix.Constants import *

import packaging.version
import pathlib
import json

# Configuration defined at build-time. This is a class so that we can
# unit test with dependency injection.


class BuildConfig:
    # version: packaging.Version for the currently-running tuffix
    # state_path: pathlib.Path holding the path to state.json
    def __init__(self,
                 version,
                 state_path):
        if not (isinstance(version, packaging.version.Version) and
                isinstance(state_path, pathlib.Path) and
                state_path.suffix == '.json'):
            raise ValueError
        self.version = version
        self.state_path = state_path


# Singleton BuildConfig object using the constants declared at the top of
# this file.
DEFAULT_BUILD_CONFIG = BuildConfig(VERSION, STATE_PATH)


class State:
    """
    Build_config: a BuildConfig object
    Version: packaging.Version for the tuffix version that created this state
    Installed: list of strings representing the codewords that are currently installed

    NOTE: Current state of tuffix, saved in a .json file under /var.
    """

    def __init__(self, build_config, version, installed):
        if not (isinstance(build_config, BuildConfig) and
                isinstance(version, packaging.version.Version) and
                isinstance(installed, list) and
                all([isinstance(codeword, str) for codeword in installed])):
            raise ValueError
        self.build_config = build_config
        self.version = version
        self.installed = installed

    # Write this state to disk.
    def write(self):
        with open(self.build_config.state_path, 'w') as f:
            document = {
                'version': str(self.version),
                'installed': self.installed
            }
            json.dump(document, f)

# Reads the current state.
# build_config: A BuildConfig object.
# raises EnvironmentError if there is a problem.


def read_state(build_config):
    if not isinstance(build_config, BuildConfig):
        raise ValueError
    try:
        with open(build_config.state_path) as f:
            document = json.load(f)
            return State(build_config,
                         packaging.version.Version(document['version']),
                         document['installed'])
    except (OSError, FileNotFoundError):
        raise EnvironmentError(
            'state file not found, you must run $ tuffix init')
    except json.JSONDecodeError:
        raise EnvironmentError('state file JSON is corrupted')
    except packaging.version.InvalidVersion:
        raise EnvironmentError('version number in state file is invalid')
    except KeyError:
        raise EnvironmentError('state file JSON is missing required keys')
    except ValueError:
        raise EnvironmentError('state file JSON has malformed values')
