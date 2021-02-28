##########################################################################
# user-facing commands (init, add, etc.)
# AUTHORS: Kevin Wortman, Jared Dyreson
##########################################################################

from Tuffix.Configuration import BuildConfig, State
from Tuffix.Constants import *
from Tuffix.Exceptions import *
from Tuffix.Keywords import *
from Tuffix.Status import status
from Tuffix.UtilityFunctions import *
import os

# abstract base class for one of the user-visible tuffix commands, e.g.
# init, status, etc.


class AbstractCommand:
    # build_config: a BuildConfig object
    # name: the string used for the command one the commandline, e.g 'init'.
    #   Must be a non-empty string of lower-case letters.
    # description: description of the command printed in usage help. Must be
    #   a nonempty string.
    def __init__(self, build_config, name, description):
        if not (isinstance(build_config, BuildConfig) and
                isinstance(name, str) and
                len(name) > 0 and
                name.isalpha() and
                name.islower() and
                isinstance(description, str)):
            raise ValueError
        self.build_config = build_config
        self.name = name
        self.description = description

    def __repr__(self):
        return f"""
        Class: {self.__name__}
        Name: {self.name}
        Description: {self.description}
        """

    # Execute the command.
    # arguments: list of commandline arguments after the command name.
    # A concrete implementation should:
    # Execute the command, then return and int for the exit code that tuffix
    # should return to the OS.
    # Raise UsageError if arguments are invalid commandline arguments.
    # Raise another kind of MessageException in any other error case.
    # execute may only throw MessageException subtypes (including UsageError);
    # other exceptions should be caught and rethrown as a MessageException.
    def execute(self, arguments):
        raise NotImplementedError

# not meant to be added to list of commands


class MarkCommand(AbstractCommand):
    """
    GOAL: combine both the add and remove keywords
    This prevents us for not writing the same code twice.
    They are essentially the same function but they just call a different method
    """

    def __init__(self, build_config, command):
        super().__init__(build_config, 'mark', 'mark (install/remove) one or more keywords')
        if not(isinstance(command, str)):
            raise ValueError
        # either select the add or remove from the Keywords
        self.command = command

    def execute(self, arguments):
        if not (isinstance(arguments, list) and
                all([isinstance(argument, str) for argument in arguments])):
            raise ValueError

        if not(arguments):
            raise UsageError("you must supply at least one keyword to mark")

        # ./tuffix add base media latex
        collection = [
            find_keyword(
                self.build_config,
                arguments[x]) for x,
            _ in enumerate(arguments)]

        state = read_state(self.build_config)
        first_arg = arguments[0]
        install = True if self.command == "add" else False

        # for console messages
        verb, past = (
            "installing", "installed") if install else (
            "removing", "removed")

        # ./tuffix add all
        # ./tuffix remove all

        if(first_arg == "all"):
            try:
                input(
                    "are you sure you want to install/remove all packages? Press enter to continue or CTRL-D to exit: ")
            except EOFError:
                quit()
            if(install):
                collection = [
                    word for word in all_keywords(
                        self.build_config) if word.name != first_arg]
            else:
                collection = [
                    find_keyword(
                        self.build_config,
                        element) for element in state.installed]

        ensure_root_access()

        for element in collection:
            if((element.name in state.installed)):
                if(install):
                    raise UsageError(
                        f'tuffix: cannot add {element.name}, it is already installed')
            elif((element.name not in state.installed) and (not install)):
                raise UsageError(
                    f'cannot remove candidate {element.name}; not installed')

            print(f'[INFO] Tuffix: {verb} {element.name}')

            try:
                getattr(element, self.command)()
            except AttributeError:
                raise UsageError(
                    f'{element.__name__} does not have the function {self.command}')

            new_action = state.installed

            if(not install):
                new_action.remove(element.name)
            else:
                new_action.append(element.name)

            new_state = State(self.build_config,
                              self.build_config.version,
                              new_action)
            new_state.write()

            os.system("apt autoremove")

            print(f'[INFO] Tuffix: successfully {past} {element.name}')


class AddCommand(AbstractCommand):
    def __init__(self, build_config):
        super().__init__(build_config, 'add', 'add (install) one or more keywords')
        self.mark = MarkCommand(build_config, self.name)

    def execute(self, arguments):
        self.mark.execute(arguments)


class DescribeCommand(AbstractCommand):

    def __init__(self, build_config):
        super().__init__(build_config, 'describe', 'describe a given keyword')

    def execute(self, arguments):
        if not (isinstance(arguments, list) and
                all([isinstance(argument, str) for argument in arguments])):
            raise ValueError
        if(len(arguments) != 1):
            raise UsageError("Please supply at only one keyword to describe")

        keyword = find_keyword(self.build_config, arguments[0])
        print(f'{keyword.name}: {keyword.description}')


class RekeyCommand(AbstractCommand):

    whoami = os.getlogin()
    # name, email, passphrase = input("Name: "), input("Email: "), getpass.getpass("Passphrase: ")

    def __init__(self, build_config):
        super().__init__(build_config, 'rekey', 'regenerate ssh and/or gpg key')

    def ssh_gen(self):
        ssh_dir = pathlib.Path(f'/home/{self.whoami}/.ssh')
        key = RSA.generate(4096)
        private_path = pathlib.Path(os.path.join(ssh_dir, 'id_rsa'))
        with open(private_path, "wb") as fp:
            fp.write(key.exportKey('PEM'))

        public_key = key.publickey()
        public_path = pathlib.Path(os.path.join(ssh_dir, 'id_rsa.pub'))
        with open(public_path, "wb") as fp:
            fp.write(public_key.exportKey('OpenSSH'))
        os.chmod(public_path, 0o600)
        os.chmod(private_path, 0o600)
        print(f'sending keys to {self.build_config.server_path}')
        subprocess.call(
            f'ssh-copy-id -i {public_path} {self.build_config.server_path}'.split())

    def gpg_gen(self):

        gpg = gnupg.GPG(gnupghome=f'/home/{self.whoami}/.gnupg')
        gpg.encoding = 'utf-8'
        gpg_file = pathlib.Path(os.path.join(gpg.gnupghome, 'tuffix_key.asc'))

        print("[INFO] Please wait a moment, this may take some time")
        input_data = gpg.gen_key_input(
            key_type="RSA",
            key_length=4096,
            name_real=self.name,
            name_comment=f'Autogenerated by tuffix for {self.name}',
            name_email=self.email,
            passphrase=self.passphrase
        )
        key = gpg.gen_key(input_data)
        public = gpg.export_keys(key.fingerprint, False)
        private = gpg.export_keys(
            key.fingerprint,
            False,
            passphrase=self.passphrase
        )

        with open(gpg_file, 'w') as fp:
            fp.write(public)
            fp.write(private)
        print(f'sending the keys to {self.build_config.server_path}')
        os.system("ssh-add")

        # not sure how this entirely works.....
        # gpg.send_keys(f'{self.build_config.server_path}', key.fingerprint)

    def execute(self, arguments):
        if not (isinstance(arguments, list) and
                all([isinstance(argument, str) for argument in arguments])):
            raise ValueError
        if(len(arguments) != 1):
            raise UsageError("Please supply at only one keyword to regen")

        regen_entity = arguments[0]

        if((regen_entity == "ssh")):
            self.ssh_gen()

        elif((regen_entity == "gpg")):
            self.gpg_gen()

        else:
            raise UsageError(
                f'[ERROR] Invalid selection {regen_entity}. "ssh" and "gpg" are the only valid selectors')


class InitCommand(AbstractCommand):
    def __init__(self, build_config):
        super().__init__(build_config, 'init', 'initialize tuffix')

    def execute(self, arguments):
        if not (isinstance(arguments, list) and
                all([isinstance(argument, str) for argument in arguments])):
            raise ValueError

        if len(arguments) != 0:
            raise UsageError("init command does not accept arguments")
        if(STATE_PATH.exists()):
            raise UsageError("init has already been done")

        create_state_directory(self.build_config)

        state = State(self.build_config, self.build_config.version, [])
        state.write()

        print('[INFO] Tuffix init succeeded')


class InstalledCommand(AbstractCommand):
    def __init__(self, build_config):
        super().__init__(build_config, 'installed', 'list all currently-installed keywords')

    def execute(self, arguments):
        if not (isinstance(arguments, list) and
                all([isinstance(argument, str) for argument in arguments])):
            raise ValueError

        if len(arguments) != 0:
            raise UsageError("installed command does not accept arguments")

        state = read_state(self.build_config)

        if len(state.installed) == 0:
            print('no keywords are installed')
        else:
            print('tuffix installed keywords:')
            for name in state.installed:
                print(name)


class ListCommand(AbstractCommand):
    def __init__(self, build_config):
        super().__init__(build_config, 'list', 'list all available keywords')

    def execute(self, arguments):
        if not (isinstance(arguments, list) and
                all([isinstance(argument, str) for argument in arguments])):
            raise ValueError

        if len(arguments) != 0:
            raise UsageError("list command does not accept arguments")

        print('tuffix list of keywords:')
        for keyword in all_keywords(self.build_config):
            print(keyword.name.ljust(KEYWORD_MAX_LENGTH) +
                  '  ' +
                  keyword.description)


class StatusCommand(AbstractCommand):
    def __init__(self, build_config):
        super().__init__(build_config, 'status', 'status of the current host')

    def execute(self, arguments):
        if not (isinstance(arguments, list) and
                all([isinstance(argument, str) for argument in arguments])):
            raise ValueError

        if len(arguments) != 0:
            raise UsageError("status command does not accept arguments")

        for line in status():
            print(line)


class RemoveCommand(AbstractCommand):
    def __init__(self, build_config):
        super().__init__(build_config, 'remove', 'remove (uninstall) one or more keywords')
        self.mark = MarkCommand(build_config, self.name)

    def execute(self, arguments):
        self.mark.execute(arguments)

# CURRENT COMMANDS SUPPORTED


# Create and return a list containing one instance of every known
# AbstractCommand, using build_config and state for each.
def all_commands(build_config):
    if not isinstance(build_config, BuildConfig):
        raise ValueError
    # alphabetical order
    return [AddCommand(build_config),
            DescribeCommand(build_config),
            InitCommand(build_config),
            InstalledCommand(build_config),
            ListCommand(build_config),
            StatusCommand(build_config),
            RemoveCommand(build_config),
            RekeyCommand(build_config)]
