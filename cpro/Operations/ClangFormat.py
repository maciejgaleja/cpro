from . import Operations
import File
import Context
from typing import List


class ClangFormatOperation(Operations.FileOperation):
    def __init__(self, context: Context.Context, file_object: File.File) -> None:
        super().__init__(context, file_object)

    def run(self) -> None:
        input_str = self.context.settings.code.newline.join(self.lines)
        temp_filename = self.context.get_filename_in_temp_dir('temp.txt')
        with open(temp_filename, 'w') as file:
            file.write(input_str)
        self.context.clang_format(
            ['-style=file', '-i', temp_filename])
        formatted_lines: List[str] = File.File.read_lines(temp_filename)
        self.file.write_lines(formatted_lines)
