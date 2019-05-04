import os
from typing import List
import subprocess


import logging as log


class Context:
    def __init__(self, pathStr: str) -> None:
        self.git_cmd: str = 'git'
        try:
            self.path: str = os.path.abspath(pathStr)
            log.debug('Starting cpro in \'' + self.path + '\'')
        except:
            raise  # TODO

    def git(self, command: List[str]) -> str:
        command_to_call = [self.git_cmd, '--no-pager', '-C', self.path]
        command_to_call.extend(command)
        log.debug('Calling \'' + ' '.join(command_to_call))
        ret = subprocess.run(command_to_call, capture_output=True)
        if not (ret.returncode == 0):
            log.error('Git command returned non-zero return status.\n' + str(ret))
            raise Exception()
        return str(ret.stdout)
