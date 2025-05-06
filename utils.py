import subprocess
import requests

import xml

from minecraft_launcher_lib.types import MinecraftOptions
from minecraft_launcher_lib.command import get_minecraft_command

def forge_stable_mc_versions() -> list:
    FORGE_API_URL = 'https://maven.minecraftforge.net/net/minecraftforge/forge/maven-metadata.xml'
    response = requests.get(FORGE_API_URL)
    response.raise_for_status()

    root = xml.etree.fromstring(response.content)

    versions = []
    for game in root.xpath('//version/text()'):
        version = game.split('-')[0]
        if version not in versions:
            versions.append(version)

    return versions

def launch_minecraft(version: str, executable_args: dict) -> None:
    command = get_minecraft_command(version, executable_args['gameDirectory'], MinecraftOptions(**executable_args))
    subprocess.run(command)
