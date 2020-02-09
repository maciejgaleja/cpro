from . import Operations
import File
import Context
from typing import List


class ClangFormatOperation(Operations.FileOperation):
    def __init__(self, context: Context.Context, file_object: File.File) -> None:
        super().__init__(context, file_object)

    def run(self) -> None:
        formatted_str = self.context.clang_format(
            ['-style=file', self.file.absolute_path])
        formatted_lines: List[str] = formatted_str.splitlines()
        self.file.write_lines(formatted_lines)
