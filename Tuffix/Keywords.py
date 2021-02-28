##########################################################################
# keywords
# AUTHORS: Kevin Wortman, Jared Dyreson
##########################################################################

from Tuffix.Configuration import *
from Tuffix.SudoRun import SudoRun
from Tuffix.KeywordHelperFunctions import *
from Tuffix.Status import *
from zipfile import Zipfile
import requests
import json


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
        super().__init__(
            build_config,
            'all',
            'all keywords available (glob pattern); to be used in conjunction with remove or add respectively')

    def add(self):
        edit_deb_packages(self.packages, is_installing=True)

    def remove(self):
        edit_deb_packages(self.packages, is_installing=False)


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
        super().__init__(
            build_config,
            'general',
            'General configuration, not tied to any specific course')

    def add(self):
        edit_deb_packages(self.packages, is_installing=True)

    def remove(self):
        edit_deb_packages(self.packages, is_installing=False)


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
        edit_deb_packages(self.packages, is_installing=True)
        self.atom()
        self.google_test_attempt()
        self.configure_git()

    def remove(self):
        edit_deb_packages(self.packages, is_installing=False)

    def add_vscode_repository(self):
        print("[INFO] Adding Microsoft repository...")
        sudo_install_command = "sudo install -o root -g root -m 644 /tmp/packages.microsoft.gpg /etc/apt/trusted.gpg.d/"

        url = "https://packages.microsoft.com/keys/microsoft.asc"

        asc_path = pathlib.Path("/tmp/m.asc")
        gpg_path = pathlib.Path("/tmp/packages.microsoft.gpg")

        with open(asc_path, "w") as f:
            f.write(requests.get(url).content.decode("utf-8"))

        subprocess.check_output(
            ('gpg', '--output', f'{gpg_path}', '--dearmor', f'{asc_path}'))
        subprocess.run(sudo_install_command.split())

        vscode_source = pathlib.Path("/etc/apt/sources.list.d/vscode.list")
        vscode_ppa = "deb [arch=amd64 signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/vscode stable main"
        with open(vscode_source, "a") as fp:
            fp.write(vscode_ppa)

    def configure_git(self, username=None, mail=None):
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
            executor.run(
                f'chown {normal_user} -R {atom_conf_dir}',
                normal_user)
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
        subprocess.check_output(
            f'sudo apt-key add {google_sources_path}'.split())

    def remove(self):
        edit_deb_packages(self.packages, is_installing=False)


class C121Keyword(AbstractKeyword):

    packages = ['cimg-dev']

    def __init__(self, build_config):
        super().__init__(build_config, 'C121', 'CPSC 121 (Object-Oriented Programming)')

    def add(self):
        # edit_deb_packages(self.packages, is_installing=True)
        edit_deb_packages(self.packages, is_installing=True)

    def remove(self):
        edit_deb_packages(self.packages, is_installing=False)


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
        edit_deb_packages(self.packages, is_installing=True)

    def remove(self):
        edit_deb_packages(self.packages, is_installing=False)


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
        edit_deb_packages(self.packages, is_installing=True)

    def remove(self):
        edit_deb_packages(self.packages, is_installing=False)


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
        edit_deb_packages(self.packages, is_installing=True)

    def remove(self):
        edit_deb_packages(self.packages, is_installing=False)


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
        edit_deb_packages(self.packages, is_installing=True)

    def remove(self):
        edit_deb_packages(self.packages, is_installing=False)


class C240Keyword(AbstractKeyword):

    """
    Point person: Floyd Holliday
    """

    packages = ['intel2gas',
                'nasm']

    def __init__(self, build_config):
        super().__init__(build_config, 'C240', 'CPSC 240 (Assembler)')

    def add(self):
        edit_deb_packages(self.packages, is_installing=True)

    def remove(self):
        edit_deb_packages(self.packages, is_installing=False)


class C351Keyword(AbstractKeyword):

    """
    Point person: William McCarthy
    """
    # TODO: testing and doing

    packages = [f'linux-headers-{current_kernel_revision()}']

    def __init__(self, build_config):
        super().__init__(build_config, 'C351', 'CPSC 351 (Operating Systems)')

    def add(self):
        print('important that you make a save state in your VM of tuffix or just install the tuffix installers scripts in another VM if you have a native install. You can mess up your main OS')
        edit_deb_packages(self.packages, is_installing=True)
        silberschatz_url = "http://cs.westminstercollege.edu/~greg/osc10e/final-src-osc10e.zip"
        r = requests.get(silberschatz_url)
        stored = "/tmp/kernel-exercises.zip"
        with open(stored, 'wb') as f:
            f.write(r.content)

        with ZipFile(stored, 'r') as zipObj:
            zipObj.extractAll()

    def remove(self):
        edit_deb_packages(self.packages, is_installing=False)


class C439Keyword(AbstractKeyword):

    """
    Point person: <++>
    """

    packages = ['minisat2']

    def __init__(self, build_config):
        super().__init__(build_config, 'C439', 'CPSC 439 (Theory of Computation)')

    def add(self):
        edit_deb_packages(self.packages, is_installing=True)

    def remove(self):
        edit_deb_packages(self.packages, is_installing=False)


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
        edit_deb_packages(self.packages, is_installing=True)

    def remove(self):
        edit_deb_packages(self.packages, is_installing=False)


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
        edit_deb_packages(self.packages, is_installing=True)
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
                raise EnvironmentError(
                    "cannot access link to get Eclipse, please tell your instructor immediately")
            fp.write(r.content)
        os.mkdir("/tmp/eclipse")
        subprocess.check_output(
            f'tar -xzvf {eclipse_download} -C /tmp/eclipse'.split())
        """
        Here is where I need help
        https://linoxide.com/linux-how-to/learn-how-install-latest-eclipse-ubuntu/
        We might need to provide documentation
        """

    def remove(self):
        edit_deb_packages(self.packages, is_installing=False)


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
        edit_deb_packages(self.packages, is_installing=True)

    def remove(self):
        edit_deb_packages(self.packages, is_installing=False)


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
        edit_deb_packages(self.packages, is_installing=True)

    def remove(self):
        edit_deb_packages(self.packages, is_installing=False)


class LatexKeyword(AbstractKeyword):
    packages = ['texlive-full']

    def __init__(self, build_config):
        super().__init__(build_config,
                         'latex',
                         'LaTeX typesetting environment (large)')

    def add(self):
        edit_deb_packages(self.packages, is_installing=True)

    def remove(self):
        edit_deb_packages(self.packages, is_installing=False)


class SystemUpgradeKeyword(AbstractKeyword):
    packages = []

    def __init__(self, build_config):
        super().__init__(build_config,
                         'sysupgrade',
                         'Upgrade the entire system')

    def add(self):
        # edit_deb_packages(self.packages, is_installing=True)
        # TODO
        # source :
        # https://stackoverflow.com/questions/3092613/python-apt-get-list-upgrades
        cache = apt.Cache()
        cache.update()
        cache.open(None)
        cache.upgrade()
        for pkg in cache.get_changes():  # changed from getChanges
            try:
                if(pkg.isUpgradeable):
                    print(f'[INFO] Upgrading {pkg.sourcePackageName}....')
                    pkg.mark_install()
                    cache.commit()
            except Exception as error:
                raise EnvironmentError(
                    f'[ERROR] Could not install {pkg.sourcePackageName}. Got error of {error}')

    def remove(self):
        print(f'[INFO] Nothing to remove for system upgrade, ignoring request')
        pass
        # edit_deb_packages(self.packages, is_installing=False)


class VirtualBoxKeyword(AbstractKeyword):
    packages = ['virtualbox-6.1']

    def __init__(self, build_config):
        super().__init__(
            build_config,
            'vbox',
            'A powerful x86 and AMD64/Intel64 virtualization product')

    def add(self):
        if(subprocess.run("grep hypervisor /proc/cpuinfo".split(), stdout=subprocess.DEVNULL).returncode == 0):
            raise EnvironmentError(
                "This is a virtual enviornment, not proceeding")

        sources_path = pathlib.Path("/etc/apt/sources.list")
        source_link = f'deb [arch=amd64] https://download.virtualbox.org/virtualbox/debian {distrib_codename()} contrib'
        with open(sources_path, "a") as fp:
            fp.write(source_link)

        wget_request = subprocess.Popen(
            ("wget",
             "-q",
             "https://www.virtualbox.org/download/oracle_vbox_2016.asc",
             "-O-"),
            stdout=subprocess.PIPE)
        apt_key = subprocess.check_output(
            ('sudo', 'apt-key', 'add', '-'), stdin=wget_request.stdout)

        edit_deb_packages(self.packages, is_installing=True)

    def remove(self):
        edit_deb_packages(self.packages, is_installing=False)


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
        edit_deb_packages(self.packages[:3], is_installing=True)
        url = "https://zoom.us/client/latest/zoom_amd64.deb"
        file_path = "/tmp/zoom"
        with open(file_path, 'wb') as fp:
            fp.write(requests.get(url).content)
        apt.debfile.DebPackage(filename=file_path).install()

    def remove(self):
        edit_deb_packages(self.packages, is_installing=False)


class TestKeyword(AbstractKeyword):
    packages = ['cowsay']

    def __init__(self, build_config):
        super().__init__(build_config,
                         'test',
                         'for testing purposes')

    def add(self):
        edit_deb_packages(self.packages, is_installing=True)

    def remove(self):
        edit_deb_packages(self.packages, is_installing=False)


class CustomKeyword(AbstractKeyword):
    # NOTE: these are not officially supported by the developers of Tuffix
    # this is merely to allow flexibility
    # TODO : testing

    """
    IDEA: if you have multiple instructors wanting to have different configurations for the same class
    Use a json file that can be loaded

    {
        "name": "Under Water Basket Weaving",
        "instructor": "Tony Stark",
        "packages": ["needles", "wool", "scuba-mask"]
    }
    """

    def __init__(self, build_config):
        super().__init__(
            build_config,
            'custom',
            'run custom keywords given by an instructor or written by a student')

    def add(self):
        path = "/tmp/example.json"  # some how loaded from CLI
        if(not os.path.exists(path)):
            raise EnvironmentError(f'[ERROR] Could not find {path}')
        with open(path, "r") as fp:
            content = json.load(fp)
        name, instructor, self.packages = content["name"].replace(
            ' ', ''), content["instructor"], content["packages"]

        print(
            f'[INFO] Installing custom keyword {name} from instructor/student {instructor}')

        edit_deb_packages(self.packages, is_installing=True)

    def remove(self):
        edit_deb_packages(self.packages, is_installing=False)


def all_keywords(build_config):
    if not isinstance(build_config, BuildConfig):
        raise ValueError
    # alphabetical order, but put digits after letters
    # TODO: all keywords commented out have not been fully developed
    return [AllKeyword(build_config),
            BaseKeyword(build_config),
            # CustomKeyword(build_config),
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
            C484Keyword(build_config),
            TestKeyword(build_config)
            ]


def find_keyword(build_config, name):
    if not (isinstance(build_config, BuildConfig) and
            isinstance(name, str)):
        raise ValueError
    for keyword in all_keywords(build_config):
        if keyword.name == name:
            return keyword
    raise UsageError(
        'unknown keyword "' +
        name +
        '", see valid keyword names with $ tuffix list')
