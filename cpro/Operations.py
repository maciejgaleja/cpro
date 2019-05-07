import File
import Context
import TextMatchers
import logging as log
from typing import List


class Operation:
    def __init__(self, context: Context.Context) -> None:
        self.context: Context.Context = context

    def run(self)->None:
        raise NotImplementedError


class FileOperation(Operation):
    def __init__(self, context: Context.Context, filename: str) -> None:
        super().__init__(context)
        self.file = File.File(filename, context)
        self.lines = self.file.read_lines()
        self.line_ending: str = ''
        if(self.lines[0][-2:] == '\r\n'):
            self.line_ending = '\r\n'
        elif(self.lines[0][-1:] == '\n'):
            self.line_ending = '\n'
        elif(self.lines[0][-1:] == '\r'):
            self.line_ending = '\r'

    def _delete_lines(self, lines_to_delete: List[int]) -> None:
        log.debug('Deleting lines: ' + repr(lines_to_delete))
        n_deleted = 0
        for i in lines_to_delete:
            del self.lines[i - n_deleted]
            n_deleted = n_deleted + 1


class CommentOperation(FileOperation):
    def __init__(self, context: Context.Context, filename: str) -> None:
        super().__init__(context, filename)
        self.use_block_comments = False
        self.comment_begin: str = '/* '
        self.comment_continue_begin: str = ' * '
        self.comment_continue_end: str = ' * '
        self.comment_end: str = ' */'
        self.solid_fill_character = '*'
        self.doxy_just_width: int = 15
        self.doxy_just_right: bool = False

    def _create_comment(self, text: str, continued: bool = False, solid: bool = False)->str:
        if continued:
            l_begin = self.comment_continue_begin
            l_end = self.comment_continue_end
        else:
            l_begin = self.comment_begin
            l_end = self.comment_end
        l_fill = ' '
        if solid:
            l_begin = l_begin.rstrip()
            l_end = l_end.lstrip()
            l_fill = self.solid_fill_character
            if len(text) > 0:
                text = ' ' + text + ' '
        ret = l_begin + text
        if(len(l_end) > 0):
            ret = ret.ljust(
                self.context.settings.code.line_width - len(l_end), l_fill)
            ret = ret + l_end
        ret = ret + self.line_ending
        return ret

    def _crate_doxy_comment(self, key: str, value: str, continued: bool = False)->str:
        if(self.doxy_just_right):
            text = (key+' ').rjust(self.doxy_just_width) + value
        else:
            text = key.ljust(self.doxy_just_width) + value
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
            self.lines.insert(line, self.line_ending)

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
            self.lines.insert(line + 1, self.line_ending)


class HeaderComment(CommentOperation):
    def __init__(self, context: Context.Context, filename: str) -> None:
        super().__init__(context, filename)

    def run(self)-> None:
        match_result = TextMatchers.match_comments(self.lines)

        if (len(match_result) > 0):
            possible_header = ''.join(
                self.lines[match_result[0].lines[0]:match_result[0].lines[-1]])
            if(self._verify_header(possible_header)):
                self._delete_lines(match_result[0].lines)

        self.lines.insert(
            0, self._create_comment('', solid=True))
        self.lines.insert(
            1, self._crate_doxy_comment('@filename', self.file.relative_path))
        self.lines.insert(
            2, self.create_authors_line())
        self.lines.insert(
            3, self._crate_doxy_comment('@date', self.file.date.isoformat()))
        self.lines.insert(
            4, self._crate_doxy_comment('@comment', ''))
        self.lines.insert(
            5, self._create_comment('', solid=True))

        self._ensure_empty_line_after(5)

        self.file.write_lines(self.lines)

    def create_authors_line(self)->str:
        ret = ''
        first_just = 15
        for author in self.file.authors:
            ret = ret + self._crate_doxy_comment('@author', repr(author))
        return ret

    def _verify_header(self, header: str)->bool:
        ret = True
        ret = ret and ('@filename' in header)
        ret = ret and ('@date' in header)
        ret = ret and ('@comment' in header)
        return ret


class PreIncludes(CommentOperation):
    def __init__(self, context: Context.Context, filename: str) -> None:
        super().__init__(context, filename)

    def run(self) -> None:
        predicate = (TextMatchers.PredicateBeginsWith('#include'),)
        includes = TextMatchers.match_group(self.lines, predicate)
        for mr in includes:
            log.debug('Found includes in: ' + repr(mr.lines))

        try:
            expected_include_comment_line = includes[0].lines[0] - 1
            log.debug('Expecting to find include comment in line ' +
                      str(expected_include_comment_line))

            expected_include_comment = self._create_comment(
                'Includes', solid=True)
            log.debug('Include comment would be like: ' +
                      expected_include_comment)

            comments = TextMatchers.match_comments(self.lines)
            deleted_line = False
            for mr in comments:
                if not deleted_line:
                    for i in mr.lines:
                        if i == expected_include_comment_line:
                            self._delete_lines([i])
                            deleted_line = True
                            break

            includes = TextMatchers.match_group(self.lines, predicate)
            comment_position = includes[0].lines[0]
            self.lines.insert(
                comment_position, expected_include_comment)

            self._ensure_empty_line_before(comment_position)

        except:
            log.warn('File ' + self.file.relative_path +
                     ' does not have include section')
            # TODO: what if there are no includes in this file?

        self.file.write_lines(self.lines)
