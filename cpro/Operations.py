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


class HeaderComment(CommentOperation):
    def __init__(self, context: Context.Context, file_object: File.File) -> None:
        super().__init__(context, file_object)

    def run(self)-> None:
        match_result = TextMatchers.match_comments(self.lines)

        if (len(match_result) > 0):
            possible_header = ''.join(
                self.lines[match_result[0].lines[0]:match_result[0].lines[-1]])
            if(self._verify_header(possible_header)):
                self._delete_lines(match_result[0].lines)

        header_block = self._create_header_block()
        self._insert_before(0, header_block)
        self._ensure_empty_line_after(len(header_block) - 1)

        self.file.write_lines(self.lines)

    def _create_header_block(self)->List[str]:
        header_block = []
        continued_comment: bool = self.context.settings.header.is_block_comment

        for line in self.context.settings.header.template:
            if line == '${AUTHOR}':
                for author in self.file.authors:
                    header_block.append(
                        self._crate_doxy_comment('@author', repr(author), continued=continued_comment))
            elif line == '${FILE}':
                header_block.append(self._create_FILE_part(continued_comment))
            elif line == '${DATE}':
                header_block.append(self._crate_doxy_comment(
                    '@date', self.file.date.isoformat(), continued=continued_comment))
            elif line == '${BRIEF}':
                header_block.append(self._crate_doxy_comment(
                    '@brief', '', continued=continued_comment))
            else:
                header_block.append(line)
        return header_block

    def _create_FILE_part(self, continued: bool = False)->str:
        ret = ''
        file_path = self.file.relative_path
        for path_spec in self.context.settings.header.file_base_path:
            potential_part_to_remove = os.path.join(*path_spec)
            if(file_path.startswith(potential_part_to_remove)) and len(potential_part_to_remove) > 0:
                file_path = file_path[len(potential_part_to_remove)+1:]
                break
        ret = self._crate_doxy_comment(
            '@file', file_path, continued=continued)
        return ret

    def _verify_header(self, header: str)->bool:
        ret = True
        ret = ret and ('@file' in header)
        ret = ret and ('@date' in header)
        ret = ret and ('@brief' in header)
        return ret


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


class PreIncludes(CommentOperation):
    def __init__(self, context: Context.Context, file_object: File.File) -> None:
        super().__init__(context, file_object)

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


class ClangFormatOperation(FileOperation):
    def __init__(self, context: Context.Context, file_object: File.File) -> None:
        super().__init__(context, file_object)

    def run(self) -> None:
        input_str = self.context.settings.code.newline.join(self.lines)
        formatted_string = self.context.clang_format(
            ['-style=file'], stdin=input_str)
        formatted_lines = formatted_string.splitlines()
        self.file.write_lines(formatted_lines)
