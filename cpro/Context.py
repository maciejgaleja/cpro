import os
from typing import List, Any
import subprocess
import Settings
import OutputManager
import logging as log
import ProgressReporter


class Context:
    def __init__(self, pathStr: str) -> None:
        # TODO: use settings
        self.git_cmd: str = 'git'
        try:
            self.path: str = os.path.abspath(pathStr)
            log.debug('Starting cpro in \'' + self.path + '\'')
        except:
            raise  # TODO

        try:
            self.settings: Settings.SettingsFile = Settings.SettingsFile(
                os.path.join(self.path, '.cpro.json'))
        except:
            raise  # TODO

        self.output: OutputManager.OutputManager = OutputManager.OutputManager()
        self.reporter: ProgressReporter.ProgressReporter = ProgressReporter.ProgressReporter(
            self.output)

    def __del__(self) -> None:
        self.settings.write_to_file()

    def git(self, command: List[str]) -> str:
        command_to_call = [self.git_cmd, '--no-pager', '-C', self.path]
        command_to_call.extend(command)
        log.debug('Calling \'' + ' '.join(command_to_call))
        ret = subprocess.run(command_to_call, capture_output=True)
        if not (ret.returncode == 0):
            log.error('Git command returned non-zero return status.\n' + str(ret))
            raise Exception()
        return str(ret.stdout)

    def clang_format(self, command: List[str], stdin: str = '') -> str:
        input_bytes: Any = None
        if not len(stdin) == 0:
            input_bytes = bytes(stdin, 'utf-8')

        # TODO: make it generic, this code is duplicated
        command_to_call: List[str] = [
            self.settings.main.clang_format_executable]
        command_to_call.extend(command)
        log.debug('Calling \'' + ' '.join(command_to_call))
        ret = subprocess.run(
            command_to_call, capture_output=True, input=input_bytes)
        if not (ret.returncode == 0):
            log.error(' '.join(command_to_call) +
                      ' command returned non-zero return status.\n' + str(ret))
            raise Exception()
        return_str: str = ret.stdout.decode('utf-8')
        return return_str
