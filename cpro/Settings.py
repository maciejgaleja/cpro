from typing import Any, Dict
import json
from types import SimpleNamespace
import logging as log


class SettingsBase:
    def __init__(self) -> None:
        pass

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def as_dict(self) -> Dict[str, Any]:
        map: Dict[str, Any] = {}
        for key in self.__dict__:
            if not key.startswith('_'):
                map[key] = (self.__dict__[key]).__dict__
        return map


class HardcodedSettings(SettingsBase):
    def __init__(self) -> None:
        super().__init__()
        self.main = SimpleNamespace()
        self.main.git_executable = 'git'
        self.main.clang_format_executable = 'clang-format'

        self.operations = SimpleNamespace()
        self.operations.format_header = False
        self.operations.format_footer = False
        self.operations.clang_format = False
        self.operations.pre_includes = False

        self.scope = SimpleNamespace()
        self.scope.source_directories = ["."]
        self.scope.extensions_source = ["c", "cpp", "cxx", "cc"]
        self.scope.extensions_header = ["h", "hpp", "hxx"]

        self.metadata = SimpleNamespace()
        self.metadata.authors_exclude = ['']

        self.code = SimpleNamespace()
        self.code.line_width = 80
        self.code.newline = '\n'

        self.comment = SimpleNamespace()
        self.comment.basic_begin = '/* '
        self.comment.basic_end = ' */'
        self.comment.block_begin = '/**'
        self.comment.block_end = ' */'
        self.comment.continued_begin = ' * '
        self.comment.continued_end = ' * '
        self.comment.solid_fill_character = '*'
        self.comment.doxy_is_just_right = False
        self.comment.doxy_just_width = 15

        self.header = SimpleNamespace()
        self.header.is_block_comment = True
        self.header.file_base_path = [[""]]
        self.header.template = [
            '/**', '${FILE}', '${AUTHOR}', '${DATE}', '${BRIEF}', '**/']

        self.footer = SimpleNamespace()
        self.footer.content = [
            '/******************************************************************************/']


class SettingsFile(HardcodedSettings):
    def __init__(self, filename: str) -> None:
        super().__init__()
        self._filename: str = filename
        json_obj: Dict[str, Any] = {}
        try:
            with open(self._filename, 'r') as file:
                json_obj = json.load(file)
        except:
            json_obj = {}
        for key in json_obj:
            try:
                nmspc: SimpleNamespace = getattr(self, key)
            except:
                log.warn(
                    'Unrecognized section found in settings file: ' + key)
                nmspc = SimpleNamespace()
                setattr(self, key, nmspc)
            for namespace_key in json_obj[key]:
                try:
                    param: Any = getattr(getattr(self, key), namespace_key)
                except:
                    log.warning(
                        'Unrecognized field found in settings file: ' + key + '.'+namespace_key)
                setattr(getattr(self, key), namespace_key,
                        json_obj[key][namespace_key])

    def write_to_file(self) -> None:
        json_str: str = json.dumps(self.as_dict(), indent=4, sort_keys=True)
        with open(self._filename, 'w') as file:
            file.write(json_str)
