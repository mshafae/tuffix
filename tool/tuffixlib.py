
################################################################################
# imports
################################################################################

# standard library

from datetime import datetime
import io
import json
import os
import pathlib
import re
import shutil
import socket
import subprocess
import sys
import unittest

# packages

try:
    import apt.cache
    import apt.debfile
    import packaging.version
except ImportError:
    print("[+] Running in development environment (most likely Arch), doing dummy imports for this to work")

from termcolor import colored
import requests
from Crypto.PublicKey import RSA
import gnupg
import getpass

# our new imports
# README:
# these are the things I have compartmentalized, please do testing to ensure all moving parts work

from Tuffix.Commands import *
from Tuffix.Configuration import *
from Tuffix.Constants import VERSION, STATE_PATH, KEYWORD_MAX_LENGTH
from Tuffix.Exceptions import *
from Tuffix.SudoRun import SudoRun

print('things work from here')

quit()


# TODO: all the other commands...


################################################################################
# keywords
################################################################################

class AbstractKeyword:
    def __init__(self, build_config, name, description):
        if not (isinstance(build_config, BuildConfig) and
                isinstance(name, str) and
                len(name) <= KEYWORD_MAX_LENGTH and
                isinstance(description, str)):
            raise ValueError
        self.name = name
        self.description = description

    def add(self):
        raise NotImplementedError
        
    def remove(self):
        raise NotImplementedError

# Keyword names may begin with a course code (digits), but Python
# identifiers may not. If a keyword name starts with a digit, prepend
# the class name with C (for Course).

class AllKeyword(AbstractKeyword):
    packages = []

    def __init__(self, build_config):
        super().__init__(build_config, 'all', 'all keywords available (glob pattern); to be used in conjunction with remove or add respectively')
 
    def add(self):
        add_deb_packages(self.packages)

    def remove(self):
        remove_deb_packages(self.packages)

class GeneralKeyword(AbstractKeyword):

    """
    Point person: undergraduate committee
    SRC: sub-tuffix/min-tuffix.yml (Kitchen sink)
    """

    packages = ['autoconf',
                'automake',
                'a2ps',
                'cscope',
                'curl',
                'dkms',
                'emacs',
                'enscript',
                'glibc-doc',
                'gpg',
                'graphviz',
                'gthumb',
                'libreadline-dev',
                'manpages-posix',
                'manpages-posix-dev',
                'meld',
                'nfs-common',
                'openssh-client',
                'openssh-server',
                'seahorse',
                'synaptic',
                'vim',
                'vim-gtk3']

    def __init__(self, build_config):
        super().__init__(build_config, 'general', 'General configuration, not tied to any specific course')
 
    def add(self):
        add_deb_packages(self.packages)

    def remove(self):
        remove_deb_packages(self.packages)

class BaseKeyword(AbstractKeyword):

    """
    Point person: undergraduate committee
    """

    packages = ['build-essential',
              'clang',
              'clang-format',
              'clang-tidy',
              'cmake',
              'code',
              'gdb',
              'gcc',
              'git',
              'g++',
              'libc++-dev',
              'libc++abi-dev',
              'libgconf-2-4',
              'libgtest-dev',
              'libgmock-dev',
              'lldb',
              'python2']

  
    def __init__(self, build_config):
        super().__init__(build_config,
                       'base',
                       'CPSC 120-121-131-301 C++ development environment')
      
    def add(self):
        self.add_vscode_repository()
        add_deb_packages(self.packages)
        self.atom()
        self.google_test_attempt()
        self.configure_git()
      
    def remove(self):
        remove_deb_packages(self.packages)

    def add_vscode_repository(self):
        print("[INFO] Adding Microsoft repository...")
        sudo_install_command = "sudo install -o root -g root -m 644 /tmp/packages.microsoft.gpg /etc/apt/trusted.gpg.d/"
        
        url = "https://packages.microsoft.com/keys/microsoft.asc"

        asc_path = pathlib.Path("/tmp/m.asc")
        gpg_path = pathlib.Path("/tmp/packages.microsoft.gpg")

        with open(asc_path, "w") as f:
            f.write(requests.get(url).content.decode("utf-8"))

        subprocess.check_output(('gpg', '--output', f'{gpg_path}', '--dearmor', f'{asc_path}'))
        subprocess.run(sudo_install_command.split())

        vscode_source = pathlib.Path("/etc/apt/sources.list.d/vscode.list")
        vscode_ppa = "deb [arch=amd64 signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/vscode stable main"
        with open(vscode_source, "a") as fp:
            fp.write(vscode_ppa)


    def configure_git(self):
        """
        GOAL: Configure git
        """ 

        keeper = SudoRun()
        whoami = keeper.whoami

        username = input("Git username: ")
        mail = input("Git email: ")
        git_conf_file = pathlib.Path(f'/home/{whoami}/.gitconfig')
        commands = [
            f'git config --file {git_conf_file} user.name {username}',
            f'git config --file {git_conf_file} user.email {mail}'
        ]
        for command in commands:
            keeper.run(command, whoami)
        print(colored("Successfully configured git", 'green'))

    def atom(self):
        """
        GOAL: Get and install Atom
        """

        atom_url = "https://atom.io/download/deb"
        atom_dest = "/tmp/atom.deb"
        atom_plugins = ['dbg-gdb', 
                        'dbg', 
                        'output-panel']

        executor = SudoRun()
        normal_user = executor.whoami
        atom_conf_dir = pathlib.Path(f'/home/{normal_user}/.atom')

        print("[INFO] Downloading Atom Debian installer....")
        with open(atom_dest, 'wb') as fp:
            fp.write(requests.get(atom_url).content)
        print("[INFO] Finished downloading...")
        print("[INFO] Installing atom....")
        apt.debfile.DebPackage(filename=atom_dest).install()
        for plugin in atom_plugins:
            print(f'[INFO] Installing {plugin}...')
            executor.run(f'/usr/bin/apm install {plugin}', normal_user)
            executor.run(f'chown {normal_user} -R {atom_conf_dir}', normal_user)
        print("[INFO] Finished installing Atom")

    def google_test_build(self):
        """
        GOAL: Get and install GoogleTest
        """

        GOOGLE_TEST_URL = "https://github.com/google/googletest.git"
        GOOGLE_DEST = "google"

        os.chdir("/tmp")
        if(os.path.isdir(GOOGLE_DEST)):
            shutil.rmtree(GOOGLE_DEST)
        subprocess.run(['git', 'clone', GOOGLE_TEST_URL, GOOGLE_DEST])
        os.chdir(GOOGLE_DEST)
        script = ["cmake CMakeLists.txt",
                   "make -j8",
                   "sudo cp -r -v googletest/include/. /usr/include",
                   "sudo cp -r -v googlemock/include/. /usr/include",
                   "sudo chown -v root:root /usr/lib"]
        for command in script:
          subprocess.run(command.split())

    def google_test_attempt(self):
        """
        Goal: small test to check if Google Test works after install
        """ 

        TEST_URL = "https://github.com/JaredDyreson/tuffix-google-test.git"
        TEST_DEST = "test"

        os.chdir("/tmp")
        if(os.path.isdir(TEST_DEST)):
            shutil.rmtree(TEST_DEST)
        subprocess.run(['git', 'clone', TEST_URL, TEST_DEST])
        os.chdir(TEST_DEST)
        subprocess.check_output(['clang++', '-v', 'main.cpp', '-o', 'main'])
        ret_code = subprocess.run(['make', 'all']).returncode
        if(ret_code != 0):
          print(colored("[ERROR] Google Unit test failed!", "red"))
        else:
          print(colored("[SUCCESS] Google unit test succeeded!", "green"))

    def google_test_all(self):
        """
        Goal: make and test Google Test library install
        """

        self.google_test_build()
        self.google_test_attempt()


class ChromeKeyword(AbstractKeyword):

    """
    Point person: anyone
    SRC: sub-tuffix/chrome.yml
    """

    packages = ['google-chrome-stable']

    def __init__(self, build_config):
        super().__init__(build_config, 'chrome', 'Google Chrome')
 
    def add(self):
        google_chrome = "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
        dest = "/tmp/chrome.deb"

        print("[INFO] Downloading Chrome Debian installer....")
        with open(dest, 'wb') as fp:
            fp.write(requests.get(google_chrome).content)
        print("[INFO] Finished downloading...")
        print("[INFO] Installing Chrome....")
        apt.debfile.DebPackage(filename=dest).install()

        google_sources = "https://dl.google.com/linux/linux_signing_key.pub"
        google_sources_path = pathlib.Path("/tmp/linux_signing_key.pub")

        with open(google_sources_path, 'wb') as fp:
            fp.write(requests.get(google_sources).content)
        subprocess.check_output(f'sudo apt-key add {google_sources_path}'.split())

    def remove(self):
        remove_deb_packages(self.packages)

class C121Keyword(AbstractKeyword):

    packages = ['cimg-dev']

    def __init__(self, build_config):
        super().__init__(build_config, 'C121', 'CPSC 121 (Object-Oriented Programming)')
 
    def add(self):
        add_deb_packages(self.packages)

    def remove(self):
        remove_deb_packages(self.packages)

class C223JKeyword(AbstractKeyword):

    """
    NOTE: do you want to use a newer version of Java?
    Or are the IDE's dependent on a certain version?
    Point Person: Floyd Holliday
    SRC: sub-tuffix/cpsc223j.yml
    """

    packages = ['geany',
                'gthumb',
                'netbeans',
                'openjdk-8-jdk',
                'openjdk-8-jre']

    def __init__(self, build_config):
        super().__init__(build_config, 'C223J', 'CPSC 223J (Java Programming)')
 
    def add(self):
        add_deb_packages(self.packages)

    def remove(self):
        remove_deb_packages(self.packages)

class C223NKeyword(AbstractKeyword):
    """
    Point person: Floyd Holliday
    SRC: sub-tuffix/cpsc223n.yml
    """
    packages = ['mono-complete',
                'netbeans']

    def __init__(self, build_config):
        super().__init__(build_config, 'C223N', 'CPSC 223N (C# Programming)')
 
    def add(self):
        add_deb_packages(self.packages)

    def remove(self):
        remove_deb_packages(self.packages)

class C223PKeyword(AbstractKeyword):
    """
    python 2.7 and lower pip no longer exists
    has been superseeded by python3-pip
    also python-virtualenv no longer exists
    Point person: Michael Shafae
    SRC: sub-tuffix/cpsc223p.yml
    """

    packages = ['python2',
                'python2-dev',
                # 'python-pip',
                # 'python-virtualenv',
                'python3',
                'python3-dev',
                'python3-pip',
                'virtualenvwrapper']

    def __init__(self, build_config):
        super().__init__(build_config, 'C223P', 'CPSC 223P (Python Programming)')
 
    def add(self):
        add_deb_packages(self.packages)

    def remove(self):
        remove_deb_packages(self.packages)

class C223WKeyword(AbstractKeyword):
    
    """
    Point person: Paul Inventado
    """

    packages = ['binutils',
                'curl',
                'gnupg2',
                'libc6-dev',
                'libcurl4',
                'libedit2',
                'libgcc-9-dev',
                'libpython2.7',
                'libsqlite3-0',
                'libstdc++-9-dev',
                'libxml2',
                'libz3-dev',
                'pkg-config',
                'tzdata',
                'zlib1g-dev']

    def __init__(self, build_config):
        super().__init__(build_config, 'C223W', 'CPSC 223W (Swift Programming)')
 
    def add(self):
        add_deb_packages(self.packages)

    def remove(self):
        remove_deb_packages(self.packages)


class C240Keyword(AbstractKeyword):

    """
    Point person: Floyd Holliday
    """

    packages = ['intel2gas',
                'nasm']

    def __init__(self, build_config):
        super().__init__(build_config, 'C240', 'CPSC 240 (Assembler)')
 
    def add(self):
        add_deb_packages(self.packages)

    def remove(self):
        remove_deb_packages(self.packages)

class C439Keyword(AbstractKeyword):

    """
    Point person: <++>
    """

    packages = ['minisat2']

    def __init__(self, build_config):
        super().__init__(build_config, 'C439', 'CPSC 439 (Theory of Computation)')

    def add(self):
        add_deb_packages(self.packages)

    def remove(self):
        remove_deb_packages(self.packages)

class C474Keyword(AbstractKeyword):

    """
    Point person: <++>
    """

    packages = ['libopenmpi-dev',
                'mpi-default-dev',
                'mpich',
                'openmpi-bin',
                'openmpi-common']
    
    def __init__(self, build_config):
        super().__init__(build_config, 'C474', 'CPSC 474 (Parallel and Distributed Computing)')
         
    def add(self):
        add_deb_packages(self.packages)
        
    def remove(self):
        remove_deb_packages(self.packages)

class C481Keyword(AbstractKeyword):

    """
    Java dependency is not installed by default
    Adding it so testing will work but needs to be addressed
    Point person: Paul Inventado
    """

    packages = ['openjdk-8-jdk',
                'openjdk-8-jre',
                'sbcl',
                'swi-prolog-nox',
                'swi-prolog-x']

    def __init__(self, build_config):
        super().__init__(build_config, 'C481', 'CPSC 481 (Artificial Intelligence)')
 
    def add(self):
        add_deb_packages(self.packages)
        """
        You are going to need to get the most up to date
        link because the original one broke and this one currently works.
        """
        eclipse_download = pathlib.Path("/tmp/eclipse.tar.gz")

        """
        might need to change because development was done in Idaho
        """

        eclipse_link = "http://mirror.umd.edu/eclipse/oomph/epp/2020-06/R/eclipse-inst-linux64.tar.gz"
        with open(eclipse_download, 'wb') as fp:
            r = requests.get(eclipse_link)
            if(r.status_code == 404):
                raise EnvironmentError("cannot access link to get Eclipse, please tell your instructor immediately")
            fp.write(r.content)
        os.mkdir("/tmp/eclipse")
        subprocess.check_output(f'tar -xzvf {eclipse_download} -C /tmp/eclipse'.split())
        """
        Here is where I need help
        https://linoxide.com/linux-how-to/learn-how-install-latest-eclipse-ubuntu/
        We might need to provide documentation
        """

    def remove(self):
        remove_deb_packages(self.packages)

class C484Keyword(AbstractKeyword):

    """
    Point persons: Michael Shafae, Kevin Wortman
    """

    packages = ['freeglut3-dev',
                'libfreeimage-dev',
                'libgl1-mesa-dev',
                'libglew-dev',
                'libglu1-mesa-dev',
                'libopenctm-dev',
                'libx11-dev',
                'libxi-dev',
                'libxrandr-dev',
                'mesa-utils',
                'mesa-utils-extra',
                'openctm-doc',
                'openctm-tools']
                # 'python-openctm']

    def __init__(self, build_config):
        super().__init__(build_config, 'C484', 'CPSC 484 (Principles of Computer Graphics)')
 
    def add(self):
        add_deb_packages(self.packages)

    def remove(self):
        remove_deb_packages(self.packages)

class MediaKeyword(AbstractKeyword):

    packages = ['audacity',
                'blender',
                'gimp',
                'imagemagick',
                'sox',
                'vlc']

    def __init__(self, build_config):
        super().__init__(build_config, 'media', 'Media Computation Tools')
 
    def add(self):
        add_deb_packages(self.packages)

    def remove(self):
        remove_deb_packages(self.packages)

class LatexKeyword(AbstractKeyword):
    packages = ['texlive-full']

    def __init__(self, build_config):
        super().__init__(build_config,
                         'latex',
                         'LaTeX typesetting environment (large)')
         
    def add(self):
        add_deb_packages(self.packages)
        
    def remove(self):
        remove_deb_packages(self.packages)

class VirtualBoxKeyword(AbstractKeyword):
    packages = ['virtualbox-6.1']

    def __init__(self, build_config):
        super().__init__(build_config,
                         'vbox',
                         'A powerful x86 and AMD64/Intel64 virtualization product')
         
    def add(self):
        if(subprocess.run("grep hypervisor /proc/cpuinfo".split(), stdout=subprocess.DEVNULL).returncode == 0):
            raise EnvironmentError("This is a virtual enviornment, not proceeding")

        sources_path = pathlib.Path("/etc/apt/sources.list")
        source_link = f'deb [arch=amd64] https://download.virtualbox.org/virtualbox/debian {distrib_codename()} contrib'
        with open(sources_path, "a") as fp:
            fp.write(source_link)
        
        wget_request = subprocess.Popen(("wget", "-q", "https://www.virtualbox.org/download/oracle_vbox_2016.asc", "-O-"),
                                        stdout=subprocess.PIPE)
        apt_key = subprocess.check_output(('sudo', 'apt-key', 'add', '-'), stdin=wget_request.stdout)

        add_deb_packages(self.packages)
        
    def remove(self):
        remove_deb_packages(self.packages)

class ZoomKeyword(AbstractKeyword):
    packages = ['libgl1-mesa-glx',
                'libegl1-mesa',
                'libxcb-xtest0',
                'zoom']

    def __init__(self, build_config):
        super().__init__(build_config,
                         'zoom',
                         'Video conferencing software')
         
    def add(self):
        add_deb_packages(self.packages[:3])
        url = "https://zoom.us/client/latest/zoom_amd64.deb"
        file_path = "/tmp/zoom"
        with open(file_path, 'wb') as fp:
            fp.write(requests.get(url).content)
        apt.debfile.DebPackage(filename=file_path).install()
        
    def remove(self):
        remove_deb_packages(self.packages)


# TODO: more keywords...

def all_keywords(build_config):
    if not isinstance(build_config, BuildConfig):
        raise ValueError
    # alphabetical order, but put digits after letters
    return [ AllKeyword(build_config),
             BaseKeyword(build_config),
             # ChromeKeyword(build_config),
             # GeneralKeyword(build_config),
             LatexKeyword(build_config),
             ZoomKeyword(build_config),
             # MediaKeyword(build_config),
             # VirtualBoxKeyword(build_config),
             # C223JKeyword(build_config),
             # C223NKeyword(build_config),
             # C223PKeyword(build_config),
             # C223WKeyword(build_config),
             # C240Keyword(build_config),
             C121Keyword(build_config),
             C439Keyword(build_config),
             C474Keyword(build_config),
             # C481Keyword(build_config), 
             C484Keyword(build_config)
             ]

def find_keyword(build_config, name):
    if not (isinstance(build_config, BuildConfig) and
            isinstance(name, str)):
        raise ValueError
    for keyword in all_keywords(build_config):
        if keyword.name == name:
            return keyword
    raise UsageError('unknown keyword "' + name + '", see valid keyword names with $ tuffix list')

################################################################################
# system probing functions (gathering info about the environment)
################################################################################

# Return the Debian-style release codename, e.g. 'focal'.
# Raises EnvironmentError if this cannot be determined (most likely this is not
# a Debian-based OS).
def distrib_codename():
    try:
        with open('/etc/lsb-release') as stream:
            return parse_distrib_codename(stream)
    except OSError:
        raise EnvironmentError('no /etc/lsb-release; this does not seem to be Linux')

# Raises EnvironmentError if there is no connected network adapter.
def ensure_network_connected():
    """
    NOTE: has been duplicated in has_internet
    Please discard when necessary
    """

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
                    return # found one, stop
        except OSError: # file not found
            pass
        except ValueError: # int(...) parse error
            pass
    raise EnvironmentError('no connected network adapter, internet is down')

# Raises UsageError if we do not have root access.
def ensure_root_access():
    if os.getuid() != 0:
        raise UsageError('you do not have root access; run this command like $ sudo tuffix ...')

# Raise EnvironemntError if the given shell command name is not an executable
# program.
# name: a string containing a shell program name, e.g. 'ping'.
def ensure_shell_command_exists(name):
    if not (isinstance(name, str)):
        raise ValueError
    try:
        result = subprocess.run(['which', name])
        if result.returncode != 0:
            raise EnvironmentError('command "' + name + '" not found; this does not seem to be Ubuntu')
    except FileNotFoundError:
        raise EnvironmentError("no 'which' command; this does not seem to be Linux")

################################################################################
# changing the system during keyword add/remove
################################################################################

def add_deb_packages(package_names):
    if not (isinstance(package_names, list) and
            all(isinstance(name, str) for name in package_names)):
        raise ValueError
    print(f'[INFO] Adding all packages to the APT queue ({len(package_names)})')
    cache = apt.cache.Cache()
    cache.update()
    cache.open()
    for name in package_names:
        print(f'adding {name}')
        try:
            cache[name].mark_install()
        except KeyError:
            raise EnvironmentError('deb package "' + name + '" not found, is this Ubuntu?')
    try:
        cache.commit()
    except Exception as e:
        raise EnvironmentError('error installing package "' + name + '": ' + str(e))

# create the directory for the state file, unless it already exists
def create_state_directory(build_config):
    ensure_root_access()
    dir_path = os.path.dirname(build_config.state_path)
    os.makedirs(dir_path, exist_ok=True)

def remove_deb_packages(package_names):
    if not (isinstance(package_names, list) and
            all(isinstance(name, str) for name in package_names)):
        raise ValueError
    cache = apt.cache.Cache()
    cache.update()
    cache.open()
    for name in package_names:
        try:
            cache[name].mark_delete()
        except KeyError:
            raise EnvironmentError('deb package "' + name + '" not found, is this Ubuntu?')
    try:
        cache.commit()
    except Exception as e:
        raise EnvironmentError('error removing package "' + name + '": ' + str(e))

################################################################################
# miscellaneous utility functions
################################################################################

# Read and parse the release codename from /etc/lsb-release .
def distrib_codename():
    with open('/etc/lsb-release') as f:
        return parse_distrib_codename(f)

def is_deb_package_installed(package_name):
    try:
        apt_pkg.init()
        cache = apt_pkg.Cache()
        package = cache[package_name]
        return (package.current_state == apt_pkg.CURSTATE_INSTALLED)
    except KeyError:
        raise EnvironmentError('no such package "' + package_name + '"; is this Ubuntu?')
    
# Parse the DISTRIB_CODENAME from a file formatted like /etc/lsb-release .
# This is factored out into its own function for unit testing.
# stream: a readable stream to /etc/lsb-release, or a similar file.
def parse_distrib_codename(stream):
    # find a line with DISTRIB_CODENAME=...
    line = None
    for l in stream.readlines():
        if l.startswith('DISTRIB_CODENAME'):
            line = l
            break
    if not line:
        raise EnvironmentError('/etc/lsb-release has no DISTRIB_CODENAME')
    # return the word after =, with whitespace removed
    tokens = line.split('=')
    if len(tokens) != 2:
        raise EnvironmentError('/etc/lsb-release syntax error')
    codename = tokens[1].strip()
    return codename



################################################################################
# main, argument parsing, and usage errors
################################################################################



