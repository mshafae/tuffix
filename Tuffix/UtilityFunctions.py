################################################################################
# miscellaneous utility functions
# AUTHORS: Kevin Wortman, Jared Dyreson
################################################################################

import re
import subprocess
import os
from apt import apt_pkg

from Tuffix.Exceptions import *

def distrib_codename():
    """
    Read and parse the release codename from /etc/lsb-release .
    """

    try:
        with open('/etc/lsb-release') as stream:
            return parse_distrib_codename(stream)
    except (OSError, FileNotFoundError):
        raise EnvironmentError("[ERROR] Cannot process /etc/lsb-release, not found. Is this Ubuntu?")

def is_deb_package_installed(package_name):
    try:
        apt_pkg.init()
        cache = apt_pkg.Cache()
        package = cache[package_name]
        return (package.current_state == apt_pkg.CURSTATE_INSTALLED)
    except KeyError:
        raise EnvironmentError(f'[ERROR] No such package "{package_name}"; is this Ubuntu?')

def parse_distrib_codename(stream):
    """
    Parse the DISTRIB_CODENAME from a file formatted like /etc/lsb-release .
    This is factored out into its own function for unit testing.
    stream: a readable stream to /etc/lsb-release, or a similar file.
    """

    _re = re.compile("DISTRIB_CODENAME=(?P<name>[a-zA-Z]+)")
    _match = None

    for line in stream.readlines():
        match = _re.match(line)
        if(match):
            _match = match.group("name")

    if not(_match):
        raise EnvironmentError("[ERROR] Could not find a distrib name")
    if(len(_match.split(' ') > 1)):
        raise EnvironmentError("[ERROR] /etc/lsb-release syntax error")
    return _match

################################################################################
# system probing functions (gathering info about the environment)
################################################################################

def ensure_root_access():
    """
    Raises UsageError if we do not have root access.
    """

    if os.getuid() != 0:
        raise UsageError('you do not have root access; run this command like $ sudo tuffix ...')

def ensure_shell_command_exists(name):
    """
    Raise EnvironemntError if the given shell command name is not an executable
    program.
    name: a string containing a shell program name, e.g. 'ping'.
    """

    if not (isinstance(name, str)):
        raise ValueError
    try:
        result = subprocess.run(['which', name])
        if result.returncode != 0:
            raise EnvironmentError(f'command "{name}" not found; this does not seem to be Ubuntu')
    except FileNotFoundError:
        raise EnvironmentError("no 'which' command; this does not seem to be Linux")

def create_state_directory(build_config):
    """
    Create the directory for the state file, unless it already exists
    """

    ensure_root_access()
    dir_path = os.path.dirname(build_config.state_path)
    os.makedirs(dir_path, exist_ok=True)

def set_background(path: str):
    if not(isinstance(path, str)):
        raise ValueError

    SCHEMA = "org.gnome.desktop.background"
    KEY = "picture-uri"

    gsettings = Gio.Settings.new(SCHEMA)
    gsettings.set_string(KEY, f'file://{path}')
