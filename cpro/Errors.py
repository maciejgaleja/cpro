class NotInitialized(Exception):
    def __init__(self, message: str) -> None:
        full_message = 'Not a cpro project (' + message + ')'
        super().__init__(full_message)
