################################################################################
# status API
# AUTHORS: Jared Dyreson, Kevin Wortman
################################################################################

"""
Used for managing code execution by one user on the behalf of another
For example: root creating a file in Jared's home directory but Jared is still the sole owner of the file
We probably should instantiate a global SudoRun instead of re running it everytime in each function it's used in
^ This is going to be put inside the SiteConfig and BuildConfig later so it can be referenced for unit testing

NOTE: update this section with https://github.com/JaredDyreson/SudoRun/
"""

from Tuffix.SudoRun import SudoRun
from Tuffix.Configuration import read_state, DEFAULT_BUILD_CONFIG
from Tuffix.Exceptions import *

import re
import subprocess
from termcolor import colored
import os
import socket
from datetime import datetime
from shutil import which

def is_tool(command: str) -> bool:
    """
    Goal: Check if command exists
    Source: https://stackoverflow.com/questions/11210104/check-if-a-program-exists-from-a-python-script#34177358
    """

    if not(isinstance(command, str)):
        raise ValueError
    return which(command) is not None

def in_VM() -> bool:
    """
    Goal: check if we're in a VM. Probably the most unreliable way to do this.
    """

    path = "/proc/scsi/scsi"
    with open(path) as f:
        contents = f.readlines()
    return (len(contents) > 1)

def cpu_information() -> str:
    """
    Goal: get current CPU model name and the amount of cores
    """

    path = "/proc/cpuinfo"
    _r_cpu_core_count = re.compile("cpu cores.*(?P<count>[0-9].*)")
    _r_general_model_name = re.compile("model name.*\:(?P<name>.*)")
    with open(path, "r") as fp:
        contents = fp.readlines()

    cores, name = None, None

    for line in contents:
        core_match = _r_cpu_core_count.match(line)
        model_match = _r_general_model_name.match(line)
        if(core_match and cores is None):
            cores = core_match.group("count")
        elif(model_match and name is None):
            name = model_match.group("name")
        elif(cores and name):
            return f"{' '.join(name.split())} ({cores} cores)"

    return (cores, name)

def host() -> str:
    """
    Goal: get the current user logged in and the computer they are logged into
    """

    return f"{os.getlogin()}@{socket.gethostname()}"

def current_operating_system() -> str:
    """
    Goal: get current Linux distribution name
    """

    path = "/etc/os-release"
    if not(os.path.exists(path)):
        raise EnvironmentError(f'could not get release information, {path} does not exist')
    _r_OS = re.compile('NAME\=\"(?P<release>[a-zA-Z].*)\"')
    with open(path, "r") as fp:
        line = fp.readline()
    _match = _r_OS.match(line)
    if(isinstance(_match, None)):
        raise EnvironmentError(f'could not parse release information')
    return _match.group("release")

def current_kernel_revision() -> str:
    """
    Goal: get the current kernel version
    """

    return os.uname().release

def current_time() -> str:
    """
    Goal: return the current date and time
    """

    return datetime.now().strftime("%a %d %B %Y %H:%M:%S")

def current_model() -> str:
    """
    Goal: retrieve the current make and model of the host
    """

    product_name = "/sys/devices/virtual/dmi/id/product_name"
    product_family = "/sys/devices/virtual/dmi/id/product_family"
    vendor_name = "/sys/devices/virtual/dmi/id/sys_vendor"

    if not(
        os.path.exists(product_name) or
        os.path.exists(product_family) or
        os.path.exists(vendor_name)):
        raise EnvironmentError(f'could not find system information files')

    with open(product_name, "r") as pn, open(product_family, "r") as pf, open(vendor_name, "r") as vn:
        name   = pn.readline().strip('\n')
        family = pf.readline().strip('\n')
        vendor = vn.readline().strip('\n')

    vendor = "" if vendor in name else vendor
    family = "" if name not in family else family
    return f"{vendor} {name}{family}"

def current_uptime() -> str:
    """
    Goal: pretty print the contents of /proc/uptime
    Source: https://thesmithfam.org/blog/2005/11/19/python-uptime-script/
    """

    path = "/proc/uptime"
    if not(os.path.exists(path)):
        raise EnvironmentError(f'could not open {path}, is this unix?')

    with open(path, 'r') as f:
        total_seconds = float(f.readline().split()[0])


    MINUTE  = 60
    HOUR    = MINUTE * 60
    DAY     = HOUR * 24

    days    = int( total_seconds / DAY )
    hours   = int( ( total_seconds % DAY ) / HOUR )
    minutes = int( ( total_seconds % HOUR ) / MINUTE )
    seconds = int( total_seconds % MINUTE )

    return f"{days} day(s), {hours} hour(s), {minutes} minute(s), {seconds} second(s)"

def memory_information() -> int:
    """
    Goal: get total amount of ram on system
    """

    formatting = lambda quantity, power: quantity/(1000**power)
    path = "/proc/meminfo"
    if not(os.path.exists(path)):
        raise EnvironmentError(f'could not open {path}, is this unix?')

    with open(path, "r") as fp:
        total = int(fp.readline().split()[1])

    return int(formatting(total, 2))

def graphics_information() -> tuple:
    """
    Use lspci to get the current graphics card in use
    Requires pciutils to be installed (seems to be installed by default on Ubuntu)
    Source: https://stackoverflow.com/questions/13867696/python-in-linux-obtain-vga-specifications-via-lspci-or-hal
    """

    primary, secondary = None, None
    vga_regex, controller_regex = re.compile("VGA.*\:(?P<model>(?:(?!\s\().)*)"), re.compile("3D.*\:(?P<model>(?:(?!\s\().)*)")

    _default_shell_path, _lspci_path = which("bash"), which("lspci")

    if(not _default_shell_path):
        raise EnvironmentError(f'could not find bash')
    if(not _lspci_path):
        raise EnvironmentError(f'could not find lspci')

    _lspci_output = subprocess.check_output(_lspci_path,
                                            shell=True,
                                            executable=_default_shell_path,
                                            encoding="utf-8",
                                            universal_newlines="\n").splitlines()

    for line in _lspci_output:
        primary_match, secondary_match = vga_regex.search(line), controller_regex.search(line)
        if(primary_match and not primary):
            primary = primary_match.group("model").strip()
        elif(secondary_match and not secondary):
            secondary = secondary_match.group("model").strip()
        elif(primary and secondary):
            break

    if(not primary and
       not secondary):
       raise EnvironmentError('could not identify primary or secondary video out source')

    primary, secondary = colored(primary, 'green'), colored("None" if not secondary else secondary, 'red')
    return (primary, secondary)


def list_git_configuration() -> tuple:
    """
    Retrieve Git configuration information about the current user
    """
    keeper = SudoRun()
    _git_path = which("git")
    if not(_git_path):
        raise EnvironmentError('could not find git')

    username_regex = re.compile("user.name\=(?P<user>.*$)")
    email_regex = re.compile("user.email\=(?P<email>.*$)")

    out = keeper.run(command=f"{_git_path} --no-pager config --list", desired_user=keeper.whoami)
    user, email = None, None

    for line in out:
        user_match = username_regex.match(line)
        email_match = email_regex.match(line)
        if(user_match):
            user = user_match.group("user")
        elif(email_match):
            email = email_match.group("email")

    return (user, email) if(user and email) else ("None", "None")

def has_internet() -> bool:
    """
    i dont think throwing exception if no internet is good
    setting as bool for unit tests
    """

    PARENT_DIR = '/sys/class/net'
    LOOPBACK_ADAPTER = 'lo'
    if not os.path.isdir(PARENT_DIR):
        raise EnvironmentError(f'no {PARENT_DIR}; this does not seem to be Linux')
    adapter_path = None
    for entry in os.listdir(PARENT_DIR):
        subdir_path = os.path.join(PARENT_DIR, entry)
        if (entry.startswith('.') or
            entry == LOOPBACK_ADAPTER or
            not os.path.isdir(subdir_path)):
            continue
        carrier_path = os.path.join(subdir_path, 'carrier')
        try:
            with open(carrier_path) as f:
                state = int(f.read())
                if state != 0:
                    return True# found one, stop
        # except OSError: # file not found
            # pass
        # except ValueError: # int(...) parse error
            # pass
    # raise EnvironmentError('no connected network adapter, internet is down')
    return False

def currently_installed_targets() -> list:
    """
    GOAL: list all installed codewords in a formatted list
    """

    return [f'{"- ": >4} {element}' for element in read_state(DEFAULT_BUILD_CONFIG).installed]


def status() -> tuple:
    """
    GOAL: Driver code for all the components defined above
    """

    git_email, git_username = list_git_configuration()
    primary, secondary = graphics_information()
    installed_targets = currently_installed_targets()
    installed_targets = '\n'.join(installed_targets).strip() if (installed_targets) else "None"

    return (
        f'{host()}',
        '-----',
        f'OS: {current_operating_system()}',
        f'Model: {current_model()}',
        f'Kernel: {current_kernel_revision()}',
        f'Uptime: {current_uptime()}',
        f'Shell: {system_shell()}',
        f'Terminal: {system_terminal_emulator()}',
        f'CPU: {cpu_information()}',
        'GPU:',
        f'  - Primary: {primary}',
        f'  - Secondary: {secondary}',
        f'Memory: {memory_information()} GB',
        f'Current Time: {current_time()}',
        'Git Configuration:',
        f'  - Email: {git_email}',
        f'  - Username: {git_username}',
        'Installed keywords:',
        f'{installed_targets}',
        f'Connected to Internet: {"Yes" if has_internet() else "No"}'
    )

def system_shell():
    """
    Goal: find the current shell of the user, rather than assuming they are using Bash
    """

    path = "/etc/passwd"
    cu = os.getlogin()
    _r_shell = re.compile(f"^{cu}.*\:\/home\/{cu}\:(?P<path>.*)")
    shell_name = None
    with open(path, "r") as fp:
        contents = fp.readlines()
    for line in contents:
        shell_match = _r_shell.match(line)
        if(shell_match):
              shell_path = shell_match.group("path")
              version, _ = subprocess.Popen([shell_path, '--version'],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT).communicate()
              shell_name = os.path.basename(shell_path)

    version = version.decode("utf-8").splitlines()[0]

    return version


def system_terminal_emulator() -> str:
    """
    Goal: find the default terminal emulator
    """
    try:
        return os.environ["TERM"]
    except KeyError:
        raise EnvironmentError("Cannot find default terminal")
