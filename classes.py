from dataclasses import dataclass, field, asdict
from typing import List

class TrackedDict(dict):
    def __init__(self, owner, name,  *args, **kwargs):
        self.owner = owner
        self.name = name
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.owner._config_dump(changed_key=key, dict_name=self.name)

    def __delitem__(self, key):
        super().__delitem__(key)
        self.owner._config_dump(changed_key=key, dict_name=self.name)

    def clear(self):
        super().clear()
        self.owner._config_dump(changed_key='all_cleared', dict_name=self.name)

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.owner._config_dump(changed_key='multiple_changed', dict_name=self.name)

@dataclass
class Settings:
    last_launch: str = ""
    launch_after_install: bool = True
    show_in_vanilla: List[str] = field(default_factory=['release', 'snapshot', 'old_beta', 'old_alpha'])
