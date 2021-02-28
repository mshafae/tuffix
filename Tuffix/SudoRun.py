##################################
# shell command wrapper in Python
# AUTHOR: Jared Dyreson
##################################

from Tuffix.Exceptions import *

import os
import pathlib
import subprocess
import re


class SudoRun():
    def __init__(self):
        self.whoami = os.getlogin()

    def chuser(self, user_id: int, user_gid: int, permanent: bool):
        """
        GOAL: permanently change the user in the context of the running program
        """

        if not(isinstance(user_id, int) and
                isinstance(user_gid, int)):
            raise ValueError

        os.setgid(user_gid)
        os.setuid(user_id)

    def check_user(self, user: str):
        """
        Check the passwd file to see if a given user a valid user
        """

        if not(isinstance(user, str)):
            raise ValueError

        passwd_path = "/etc/passwd"

        with open(passwd_path, "r") as fp:
            contents = fp.readlines()
        return user in [
            re.search(
                '^(?P<name>.+?)\\:',
                line).group("name") for line in contents]

    def run(self, command: str, desired_user: str) -> list:
        """
        Run a shell command as another user using sudo
        Check if the desired user is a valid user.
        If permission is denied, throw a descriptive error why
        """

        if not(isinstance(command, str) and
               isinstance(desired_user, str)):
            raise ValueError

        if not(self.check_user(desired_user)):
            raise UnknownUserException(f'Unknown user: {desired_user}')

        current_user = os.getlogin()

        if((current_user == "root") and (os.getuid() != 0)):
            raise PrivilageExecutionException(
                f'{current_user} does not have permission to run the command {command} as the user {desired_user}')

        command = f'sudo -H -u {desired_user} bash -c \'{command}\''

        return [
            line for line in subprocess.check_output(
                command,
                shell=True,
                encoding="utf-8").split('\n') if line]
