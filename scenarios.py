from pathlib import Path
import uuid
import os

from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.syntax import Syntax
from rich.text import Text
from rich.style import Style
from rich.align import Align
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from simple_term_menu import TerminalMenu
from faker import Faker
from minecraft_launcher_lib.utils import get_version_list
from minecraft_launcher_lib import (fabric, quilt, forge, install)

from test_utils import forge_stable_mc_versions, launch_minecraft

def info(launcher_settings: dict, executable_args: dict) -> None:
    body_left = Panel(
        Align.center(
            renderable=Text(f'minecraft_v: 1.21.5\nloader: fabric\nloader_v: 0.12.05', justify='left'), 
            vertical='middle'
        ),
        title='launcher',
        style=Style(color='steel_blue')
    )
    body_middle = Panel(
        Align.left(
            renderable=Syntax(code='\n'.join([f'{key}: {val}' for key, val in launcher_settings.items()]), lexer='yaml', line_numbers=True, theme='ansi_dark'),
            vertical='middle'
        ),
        title='settings.yaml',
        style=Style(color='magenta')
    )
    body_right = Panel(
        Align.left(
            renderable=Syntax(code='\n'.join([f'{key}: {val}' for key, val in executable_args.items()]), lexer='yaml', line_numbers=True, theme='ansi_dark'), 
            vertical='middle'
        ),
        title='executable_args.yaml',
        style=Style(color='red')
    ) 

    body = Layout(ratio=4)
    body.split_row(body_left, body_middle, body_right) 

    footer = Layout(
        renderable=Panel("Qbvadko Minecraft Launcher"),
        ratio=1 
    )

    root = Layout()
    root.split_column(body, footer)

    return root

def installing(launcher_settings: dict, executable_args: dict) -> str|None:
    menu_entries = ['without loader', 'fabric loader', 'quilt loader', 'forge loader']
    menu_entries.insert(0, 'cancel')

    menu = TerminalMenu(
        title='Select the mod loader (that will be installed with Minecraft):',
        menu_entries=menu_entries
    )
    menu.show()

    if menu.chosen_menu_entry == 'cancel': return

    if 'fabric' in menu.chosen_menu_entry:
        menu_entries, loader = fabric.get_stable_minecraft_versions(), 'fabric'
        
    elif 'quilt' in menu.chosen_menu_entry:
        menu_entries, loader = quilt.get_stable_minecraft_versions(), 'quilt'

    elif 'forge' in menu.chosen_menu_entry:
        menu_entries, loader = forge_stable_mc_versions(), 'forge'
    
    elif 'without' in  menu.chosen_menu_entry:
        menu_entries, loader = [], 'vanilla'
        for i in get_version_list():
            if i['type'] in launcher_settings['show_in_vanilla']:
                menu_entries.append(i['id'])

    else: return

    menu = TerminalMenu(
        title='Select Minecraft version:',
        menu_entries=menu_entries
    )
    menu.show()

    match loader:
        case 'fabric':
            fabric.install_fabric(
                menu.chosen_menu_entry, 
                executable_args['gameDirectory'], 
                callback={'setStatus': lambda logs: print(logs)}
            )
        case 'quilt':
            quilt.install_quilt(
                menu.chosen_menu_entry, 
                executable_args['gameDirectory'],
                callback={'setStatus': lambda logs: print(logs)}
            )
        case 'forge':
            forge.install_forge_version(
                menu.chosen_menu_entry, 
                executable_args['gameDirectory'], 
                callback={'setStatus': lambda logs: print(logs)}
            )
        case 'vanilla':
            install.install_minecraft_version(
                menu.chosen_menu_entry, 
                executable_args['gameDirectory'], 
                callback={'setStatus': lambda logs: print(logs)}
            )

    versions_dir = Path(executable_args['gameDirectory'], 'versions')

    dirs = [d for d in versions_dir.iterdir() if d.is_dir()]

    dirs_with_ctime = [(d, os.stat(d).st_ctime) for d in dirs]
    dirs_with_ctime.sort(key=lambda item: item[1], reverse=True)

    return Path(str(dirs_with_ctime[0][0])).name

def launching(console: Console, executable_args: dict) -> str|None:
    minecraft_path = executable_args['gameDirectory']
    versions_dir = Path(minecraft_path, 'versions')

    installed_versions = [directory.name for directory in versions_dir.iterdir()]
    installed_versions.insert(0, 'сancel')

    if len(installed_versions) == 1:
        console.print("No version of Minecraft is installed :(")
        return

    menu = TerminalMenu(
        title='Select Minecraft to launch:',
        menu_entries=installed_versions
    )
    menu.show()

    if menu.chosen_menu_entry == 'сancel': return

    if executable_args['username'] == '':
        executable_args['username'] = Faker().user_name()

    if executable_args['uuid'] == '':
        executable_args['uuid'] = str(uuid.uuid4())

    launch_minecraft(version=menu.chosen_menu_entry, executable_args=executable_args)
    return menu.chosen_menu_entry
