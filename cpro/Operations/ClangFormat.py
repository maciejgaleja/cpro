from . import Operations
import File
import Context


class ClangFormatOperation(Operations.FileOperation):
    def __init__(self, context: Context.Context, file_object: File.File) -> None:
        super().__init__(context, file_object)

    def run(self) -> None:
        input_str = self.context.settings.code.newline.join(self.lines)
        formatted_string = self.context.clang_format(
            ['-style=file'], stdin=input_str)
        formatted_lines = formatted_string.splitlines()
        self.file.write_lines(formatted_lines)
