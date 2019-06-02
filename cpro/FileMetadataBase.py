import os
from typing import Dict, Any, List, Tuple
import json


class FileMetadata:
    def __init__(self) -> None:
        self.additional_authors: List[Tuple[str, str]] = []
        self.brief: str = ''


class FileMetadataBase:
    def __init__(self, filename: str) -> None:
        self._filename = filename
        if not os.path.isfile(filename):
            f = open(filename, 'a')
            f.write('{ }')
            f.close()

        self._json_obj: Dict[str, Any] = {}
        with open(filename, 'r') as file:
            self._json_obj = json.load(file)

        print(repr(self._json_obj))

    def get(self, filename: str) -> FileMetadata:
        absolute_path: str = os.path.normpath(filename).replace('\\', '/')
        try:
            ret: FileMetadata = self._json_obj[absolute_path]
        except:
            ret = FileMetadata()
            self._json_obj[absolute_path] = ret.__dict__
        return ret

    def write_to_file(self) -> None:
        json_dict = {}
        for path in self._json_obj:
            json_dict[path] = self._json_obj[path]
        json_str: str = json.dumps(json_dict, indent=4, sort_keys=True)
        with open(self._filename, 'w') as file:
            file.write(json_str)
