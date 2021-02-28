import os
import re

"""
pure Python equivalent of lsb_release
inspiration from this: https://chromium.googlesource.com/chromiumos/docs/+/HEAD/lsb-release.md
AUTHOR: Jared Dyreson
"""


class lsb_parser():
    def __init__(self):
        self.path = "/etc/lsb-release"
        if not(os.path.exists(self.path)):
            raise EnvironmentError(f'cannot find {self.path}; is this unix?')

        self.placeholder = "n/a"
        try:
            self.file_map = self.load()
            self.version = self.lsb_version()
            self.id = self.lsb_id()
            self.release_type = self.lsb_release_type()
        except KeyError:
            raise EnvironmentError(
                '/etc/lsb-release syntax errors, please consult file')

    def load(self):
        with open(self.path, 'r') as fp:
            lines = [line.rstrip() for line in fp]

        content = {}
        _value_re = re.compile("[\'|\"](?P<content>(\\w+\\s*)*)[\'|\"]")
        for line in lines:
            if not(line.startswith('#')):
                key, value = line.partition('=')[::2]
                _value_match = _value_re.match(value)
                content[key] = _value_match.group(
                    "content") if (_value_match) else value
        return content

    def lsb_version(self) -> float:
        return float(self.file_map["LSB_VERSION"])

    def lsb_id(self) -> str:
        return self.file_map["DISTRIB_ID"]

    def lsb_release_type(self) -> str:
        return self.file_map["DISTRIB_RELEASE"]

    def lsb_distrib_description(self) -> str:
        return self.file_map["DISTRIB_DESCRIPTION"]
