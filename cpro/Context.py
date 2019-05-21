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
            Errors.NotInitialized(self.path)

    def __del__(self) -> None:
        self.settings.write_to_file()

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

    def _call_command(self, command: List[str], stdin: str = '') -> str:
        input_bytes: Any = None
        if not len(stdin) == 0:
            input_bytes = bytes(stdin, 'utf-8')

        log.debug('Calling \'' + ' '.join(command))
        ret = subprocess.run(
            command, capture_output=True, input=input_bytes)
        return_str: str = ret.stdout.decode('utf-8')
        if not (ret.returncode == 0):
            log.error(' '.join(command) +
                      ' command returned non-zero return status.\n' + str(ret))
            err_str: str = ret.stderr.decode('utf-8')
            raise Errors.CommandFailed(
                ' '.join(command), ret.returncode, return_str, err_str)
        return return_str
