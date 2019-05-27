import os
from typing import List, Any
import subprocess
import logging as log

import Errors
import Settings


class Context:
    def __init__(self, pathStr: str) -> None:
        try:
            self.path: str = os.path.abspath(pathStr)
            log.debug('Starting cpro in \'' + self.path + '\'')
        except:
            Errors.NotInitialized(self.path)

        try:
            self.settings: Settings.SettingsFile = Settings.SettingsFile(
                os.path.join(self.path, '.cpro.json'))
        except:
            raise Errors.NotInitialized(self.path)

    def __del__(self) -> None:
        try:
            self.settings.write_to_file()
        except:
            pass

    def git(self, command: List[str]) -> str:
        command_to_call = [self.settings.main.git_executable,
                           '--no-pager', '-C', self.path]
        command_to_call.extend(command)
        return self._call_command(command_to_call)

    def clang_format(self, command: List[str], stdin: str = '') -> str:
        command_to_call: List[str] = [
            self.settings.main.clang_format_executable]
        command_to_call.extend(command)
        return self._call_command(command_to_call, stdin)

    def get_filename_in_temp_dir(self, filename: str) -> str:
        ret: str = self.path
        abspath = os.path.abspath(filename)
        common_path = os.path.commonpath(
            [os.path.abspath(self.path), abspath])
        path_difference = abspath[len(common_path)+len(os.sep):]
        ret = os.path.join(common_path, '.cpro', 'temp', path_difference)
        dirname = os.path.dirname(ret)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(ret, 'w') as file:
            file.truncate()
        return ret

    def _call_command(self, command: List[str], stdin: str = '') -> str:
        input_bytes: Any = None
        if not len(stdin) == 0:
            input_bytes = bytes(stdin, 'utf-8')

        try:
            log.debug('Calling \'' + ' '.join(command))
            ret = subprocess.run(
                command, capture_output=True, input=input_bytes)
            return_str: str = ret.stdout.decode('utf-8')
            err_str: str = ret.stderr.decode('utf-8')
            if not (ret.returncode == 0):
                raise Exception()
        except:
            raise Errors.CommandFailed(
                ' '.join(command), ret.returncode, return_str, err_str)
        return return_str
