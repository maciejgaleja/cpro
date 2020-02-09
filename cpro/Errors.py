class CproException(Exception):
    def __init__(self, message: str, doc: str = '') -> None:
        self.doc: str = doc
        super().__init__(message)


class NotInitialized(CproException):
    def __init__(self, message: str) -> None:
        full_message = 'Not a cpro project (' + message + \
            ')\nTo initialize project, use\n\n    cpro init\n'
        super().__init__(full_message)


class CommandFailed(CproException):
    def __init__(self, command: str, return_code: int, stdout: str, stderr: str) -> None:
        full_message = 'Command failed (return code ' + \
            str(return_code) + '):\n' \
            + command + '\n stdout/stderr: ' + stdout + stderr
        super().__init__(full_message)
