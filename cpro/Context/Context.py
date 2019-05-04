import os

import logging as log


class Context:
    def __init__(self, pathStr: str) -> None:
        try:
            self.path: str = os.path.abspath(pathStr)
            log.debug('Starting cpro in \'' + self.path + '\'')
        except:
            raise
