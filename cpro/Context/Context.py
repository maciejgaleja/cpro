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
            raise

    def git(self, command: List[str]) -> subprocess.CompletedProcess:
        command_to_call = [self.git_cmd, '-C', self.path]
        command_to_call.extend(command)
        log.debug('Calling \'' + ' '.join(command_to_call))
        return subprocess.run(command_to_call)
        # return
