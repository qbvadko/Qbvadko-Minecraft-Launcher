from typing import Literal
from dataclasses import asdict

import yaml
from minecraft_launcher_lib.types import MinecraftOptions
from rich.console import Console

from classes import TrackedDict, Settings
from test_utils import launch_minecraft
from scenarios import launching, installing, info


class Launcher:
    def __init__(self):
        self.running = False
        self.console = Console()
        self.console.height = 14
        self.console._emoji = True

    def _config_dump(self, changed_key, dict_name):
        #In Future
        ...

    def config_load(self, name: Literal["executable_args.yaml", "launcher_settings.yaml"]):
        with open(name, 'r') as file:
            cfg = yaml.safe_load(file)

        if name == 'launcher_settings.yaml':
            self.settings = TrackedDict(self, 'settings', asdict(Settings(**cfg)))
            return
        self.executable_args = TrackedDict(self, 'executable_args', MinecraftOptions(**cfg))

    def process_command(self, command: str):
        if command == 'launch':
            launching(self.console, self.executable_args)
            return 1
        if command == 'install':
            version = installing(self.settings, MinecraftOptions(**self.executable_args))
            
            if version is None: return 1

            if self.settings['launch_after_install']:
                launch_minecraft(version, self.executable_args)
        if command == 'info':
            self.console.print(info(self.settings, self.executable_args), justify="center")       
        if command == 'exit':
            return 0
        return 1

    def run(self):
        self.running = True
        try:
            while self.running:
                command = self.console.input('> ')
                self.running = self.process_command(command)
        finally:
            self.console.print('Goodbye my sugar <3')

if __name__ == '__main__':
    launcher = Launcher()
    launcher.config_load('launcher_settings.yaml')
    launcher.config_load('executable_args.yaml')

    launcher.run()
