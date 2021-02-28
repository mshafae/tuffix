##########################################################################
# constants
# AUTHOR: Kevin Wortman
##########################################################################

import packaging.version
import pathlib

VERSION = packaging.version.parse('0.1.0')

STATE_PATH = pathlib.Path('/var/lib/tuffix/state.json')

KEYWORD_MAX_LENGTH = 8
