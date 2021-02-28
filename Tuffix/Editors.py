##########################################################################
# editors
# AUTHOR: Jared Dyreson
##########################################################################


"""
Supported:
- atom
- emacs
- vi(m)
- vscode
"""


class Editors():
    def __init__(self):
        self.supported = [
            'atom',
            'emacs',
            'vim',
            'vscode'
        ]

        self.executor = SudoRun()
        self.normal_user = self.executor.whoami

    def atom(self):
        """
        GOAL: Get and install Atom
        """

        packages = ['atom']

        atom_plugins = ['dbg-gdb',
                        'dbg',
                        'output-panel']

        self.executor.run(
            'sudo add-apt-repository -y ppa:webupd8team/atom',
            normal_user)
        atom_conf_dir = pathlib.Path(f'/home/{self.normal_user}/.atom')
        edit_deb_packages(packages, is_installing=True)

        # print("[INFO] Downloading Atom Debian installer....")
        # content = request.get(atom_url).content

        # with open(atom_dest, 'wb') as fp:
        # fp.write(content)

        # print("[INFO] Finished downloading and proceeding to install...")
        # apt.debfile.DebPackage(filename=atom_dest).install()
        for plugin in atom_plugins:
            print(f'[INFO] Installing {plugin}...')
            executor.run(f'/usr/bin/apm install {plugin}', self.normal_user)
            executor.run(
                f'chown {normal_user} -R {atom_conf_dir}',
                self.normal_user)
        print("[INFO] Finished installing Atom")

    def emacs(self):
        packages = ['emacs']
        self.executor.run(
            'sudo add-apt-repository -y ppa:kelleyk/emacs',
            normal_user)
        edit_deb_packages(packages, is_installing=True)

    def vim(self):
        packages = ['vim']
        edit_deb_packages(packages, is_installing=True)

    def vscode(self):
        packages = ['vscode']  # please check the name of VSCode

        print("[INFO] Adding Microsoft repository...")
        sudo_install_command = "sudo install -o root -g root -m 644 /tmp/packages.microsoft.gpg /etc/apt/trusted.gpg.d/"

        url = "https://packages.microsoft.com/keys/microsoft.asc"

        asc_path = pathlib.Path("/tmp/microsoft.asc")
        gpg_path = pathlib.Path("/tmp/packages.microsoft.gpg")

        content = request.get(url).content.decode("utf-8")

        with open(asc_path, "w") as f:
            f.write(content)

        subprocess.check_output(
            ('gpg', '--output', f'{gpg_path}', '--dearmor', f'{asc_path}'))
        subprocess.run(sudo_install_command.split())

        vscode_source = pathlib.Path("/etc/apt/sources.list.d/vscode.list")
        vscode_ppa = "deb [arch=amd64 signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/vscode stable main"
        with open(vscode_source, "a") as fp:
            fp.write(vscode_ppa)
