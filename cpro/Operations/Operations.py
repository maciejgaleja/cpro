import File
import Context
import TextMatchers
import logging as log
from typing import List
import os


class Operation:
    def __init__(self, context: Context.Context) -> None:
        self.context: Context.Context = context

    def run(self)->None:
        raise NotImplementedError


class FileOperation(Operation):
    def __init__(self, context: Context.Context, file_object: File.File) -> None:
        super().__init__(context)
        self.file = file_object
        self.lines = self.file.lines

    def _delete_lines(self, lines_to_delete: List[int]) -> None:
        log.debug('Deleting lines: ' + repr(lines_to_delete))
        n_deleted = 0
        for i in lines_to_delete:
            del self.lines[i - n_deleted]
            n_deleted = n_deleted + 1

    def _insert_before(self, base_line: int, lines: List[str])->None:
        i: int = base_line
        for line in lines:
            self.lines.insert(i, line)
            i = i + 1


class CommentOperation(FileOperation):
    def __init__(self, context: Context.Context, file_object: File.File) -> None:
        super().__init__(context, file_object)

    def _create_comment(self, text: str, continued: bool = False, solid: bool = False)->str:
        if continued:
            l_begin = self.context.settings.comment.continued_begin
            l_end = self.context.settings.comment.continued_end
        else:
            l_begin = self.context.settings.comment.basic_begin
            l_end = self.context.settings.comment.basic_end
        l_fill = ' '
        if solid:
            l_begin = l_begin.rstrip()
            l_end = l_end.lstrip()
            l_fill = self.context.settings.comment.solid_fill_character
            if len(text) > 0:
                text = ' ' + text + ' '
        ret: str = l_begin + text
        if (len(l_end) > 0) or solid:
            ret = ret.ljust(
                self.context.settings.code.line_width - len(l_end), l_fill)
            ret = ret + l_end
        return ret

    def _crate_doxy_comment(self, key: str, value: str, continued: bool = False)->str:
        if(self.context.settings.comment.doxy_is_just_right):
            text = (
                key+' ').rjust(self.context.settings.comment.doxy_just_width) + value
        else:
            text = key.ljust(
                self.context.settings.comment.doxy_just_width) + value
        return self._create_comment(text, continued)

    def _ensure_empty_line_before(self, line: int) -> None:
        empty_lines = TextMatchers.match_empty_lines(self.lines)
        empty_line_present = False
        for mr in empty_lines:
            if not empty_line_present:
                for i in mr.lines:
                    if i == line - 1:
                        empty_line_present = True
                        break
        if not empty_line_present:
            self.lines.insert(line, '')

    def _ensure_empty_line_after(self, line: int) -> None:
        empty_lines = TextMatchers.match_empty_lines(self.lines)
        empty_line_present = False
        for mr in empty_lines:
            if not empty_line_present:
                for i in mr.lines:
                    if i == line + 1:
                        empty_line_present = True
                        break
        if not empty_line_present:
            self.lines.insert(line + 1, '')


class FooterComment(CommentOperation):
    def __init__(self, context: Context.Context, file_object: File.File) -> None:
        super().__init__(context, file_object)

    def run(self)-> None:
        comments = TextMatchers.join_results(
            TextMatchers.match_comments(self.lines))
        if len(self.lines) - 1 in comments.lines:
            self._delete_lines([-1])
        else:
            pass

        if not len(self.lines[-1]) == 0:
            self.lines.append('')

        for line in self.context.settings.footer.content:
            self.lines.append(line)

        self.file.write_lines(self.lines)


class ClangFormatOperation(FileOperation):
    def __init__(self, context: Context.Context, file_object: File.File) -> None:
        super().__init__(context, file_object)

    def run(self) -> None:
        input_str = self.context.settings.code.newline.join(self.lines)
        formatted_string = self.context.clang_format(
            ['-style=file'], stdin=input_str)
        formatted_lines = formatted_string.splitlines()
        self.file.write_lines(formatted_lines)
