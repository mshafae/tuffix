"""
Official driver code for Tuffix
AUTHORS: Kevin Wortman, Jared Dyreson
"""

from Tuffix.Commands import all_commands
from Tuffix.Configuration import BuildConfig, DEFAULT_BUILD_CONFIG
from Tuffix.Exceptions import *
from Tuffix.Status import *

# result of os.uname() from Rapsberry Pi 3 B+

# posix.uname_result(sysname='Linux', nodename='retropie',
# release='5.4.72-v7+', version='#1356 SMP Thu Oct 22 13:56:54 BST 2020',
# machine='armv7l')


def print_usage(build_config):
    if not (isinstance(build_config, BuildConfig)):
        raise ValueError
    output = (
        f'tuffix {build_config.version}\n\n',
        'usage:\n\n',
        '    tuffix <command> [argument...]\n\n',
        'where <command> and [argument...] match one of the following:\n'
    )

    print(''.join(output))

    commands = all_commands(build_config)

    assert(len(commands) > 0)  # for max to be defined
    name_width = 2 + max([len(cmd.name) for cmd in commands])

    for cmd in commands:
        print(f'{cmd.name.ljust(name_width)} {cmd.description}')

    print('')


def main(argv, build_config=DEFAULT_BUILD_CONFIG):
    """
    Run the whole tuffix program. This is a self-contained function for unit
    testing purposes.
    build_config: a BuildConfig object
    argv: a list of commandline argument strings, such as sys.argv

    """
    if not (isinstance(build_config, BuildConfig) and
            isinstance(argv, list) and
            all([isinstance(arg, str) for arg in argv])):
        raise ValueError
    try:
        if(len(argv) <= 1):
            raise UsageError('You must supply a command name')
        command_name = argv[1]  # skip script name at index 0

        # find the AbstractCommand that the user specified
        command_object = None
        for cmd in all_commands(build_config):
            if(cmd.name == command_name):
                command_object = cmd
                break

        # did we find a command?
        if(not command_object):
            raise UsageError(f'unknown command "{command_name}"')

        # peel off the arguments
        arguments = argv[2:]

        # run the command...
        try:
            return command_object.execute(arguments)
        except MessageException as e:
            # general error message
            print(f'[ERROR]: {e.message}')
            return 1

    # commandline interface usage error
    except UsageError as e:
        print(f'[ERROR]: {e.message}')
        print_usage(build_config)
