from typing import Any, Dict
import json


class SettingsBase:
    def __init__(self) -> None:
        self.map: Dict[str, Any] = {}

    def __getitem__(self, key: str) -> Any:
        return self.map[key]


class HardcodedSettings(SettingsBase):
    def __init__(self) -> None:
        super().__init__()
        self.map['main.git_executable'] = 'git'


class SettingsFile(HardcodedSettings):
    def __init__(self, filename: str) -> None:
        super().__init__()
        self._filename: str = filename

    def write_to_file(self)->None:
        with open(self._filename, 'w') as file:
            json.dump(self.map, file)
