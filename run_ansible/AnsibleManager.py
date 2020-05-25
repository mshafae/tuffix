#!/usr/bin/env python3.8

from subprocess import call

class AnsibleManager():
    def __init__(self, file_path: str):
        self.path = file_path
    def run(self):
        call(["ansible_playbook", "-i", "hosts", "{}".format(self.path)])

manager = AnsibleManager("HelloWorld.yml")
manager.run()
