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

    cores = None
    name = None

    for line in contents:
        core_match = _r_cpu_core_count.match(line)
        model_match = _r_general_model_name.match(line)
        if(core_match and cores is None):
            cores = core_match.group("count")
        elif(model_match and name is None):
            name = model_match.group("name")
        elif(cores and name):
            return f"{' '.join(name.split())} ({cores} cores)"

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
    _r_OS = r'NAME\=\"(?P<release>[a-zA-Z].*)\"'
    with open(path, "r") as fp: line = fp.readline()
    return re.compile(_r_OS).match(line).group("release")

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
    with open(product_name, "r") as fp:
        name = fp.readline().strip('\n')
    with open(product_family, "r") as fp:
        family = fp.readline().strip('\n')
    with open(vendor_name, "r") as fp:
        vendor = fp.read().split()[0].strip('\n')

    vendor = "" if vendor in name else vendor
    family = "" if name not in family else family
    return f"{vendor} {name}{family}"

def current_uptime() -> str:
    """
    Goal: pretty print the contents of /proc/uptime
    Source: https://thesmithfam.org/blog/2005/11/19/python-uptime-script/
    """

    path = "/proc/uptime"
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
    with open(path, "r") as fp:
        total = int(fp.readline().split()[1])
    return int(formatting(total, 2))

def graphics_information() -> str:
    """
    Use lspci to get the current graphics card in use
    Requires pciutils to be installed (seems to be installed by default on Ubuntu)
    Source: https://stackoverflow.com/questions/13867696/python-in-linux-obtain-vga-specifications-via-lspci-or-hal
    """

    primary, secondary = None, None
    vga_regex, controller_regex = re.compile("VGA.*\:(?P<model>(?:(?!\s\().)*)"), re.compile("3D.*\:(?P<model>(?:(?!\s\().)*)")

    for line in subprocess.check_output("lspci", shell=True, executable='/bin/bash').decode("utf-8").splitlines():
        primary_match, secondary_match = vga_regex.search(line), controller_regex.search(line)
        if(primary_match and not primary):
            primary = primary_match.group("model").strip()
        elif(secondary_match and not secondary):
            secondary = secondary_match.group("model").strip()
        elif(primary and secondary):
            break

    return colored(primary, 'green'), colored("None" if not secondary else secondary, 'red')


def list_git_configuration() -> tuple:
    """
    Retrieve Git configuration information about the current user
    """
    keeper = SudoRun()

    username_regex = re.compile("user.name\=(?P<user>.*$)")
    email_regex = re.compile("user.email\=(?P<email>.*$)")
    out = keeper.run(command="git --no-pager config --list", desired_user=keeper.whoami)
    u, e = None, None
    for line in out:
        u_match = username_regex.match(line)
        e_match = email_regex.match(line)
        if(u is None and u_match):
            u = u_match.group("user")
        elif(e is None and e_match):
            e = e_match.group("email")

    return (u, e) if(u and e) else ("None", "None")

def has_internet() -> bool:

    PARENT_DIR = '/sys/class/net'
    LOOPBACK_ADAPTER = 'lo'
    if not os.path.isdir(PARENT_DIR):
        raise EnvironmentError('no ' + PARENT_DIR + '; this does not seem to be Linux')
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
        except OSError: # file not found
            pass
        except ValueError: # int(...) parse error
            pass
    raise EnvironmentError('no connected network adapter, internet is down')

def currently_installed_targets() -> list:
    """
    GOAL: list all installed codewords in a formatted list
    """
    return [f'{"- ": >4} {element}' for element in read_state(DEFAULT_BUILD_CONFIG).installed]


def status() -> str:
    """
    GOAL: Driver code for all the components defined above
    """
    try:
        git_username, git_email = list_git_configuration()
    except Exception as e:
        print('[ERROR]: git is not configured')
        git_email, git_username = "None", "None"
    list_git_configuration()
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
