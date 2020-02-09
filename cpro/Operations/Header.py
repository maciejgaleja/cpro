from . import Operations
import TextMatchers
import File
import Context
from typing import List
import os


class HeaderComment(Operations.CommentOperation):
    def __init__(self, context: Context.Context, file_object: File.File) -> None:
        super().__init__(context, file_object)

    def run(self) -> None:
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

    def _create_header_block(self) -> List[str]:
        header_block = []
        continued_comment: bool = self.context.settings.header.is_block_comment

        for line in self.context.settings.header.template:
            if line == '${AUTHOR}':
                n_authors: int = 0
                for author in self.file.authors:
                    header_block.append(
                        self._crate_doxy_comment('@author', repr(author), continued=continued_comment))
                    n_authors = n_authors + 1
                if n_authors == 0:
                    header_block.append(
                        self._crate_doxy_comment('@author', '', continued=continued_comment))
            elif line == '${FILE}':
                header_block.append(self._create_FILE_part(continued_comment))
            elif line == '${DATE}':
                header_block.append(self._crate_doxy_comment(
                    '@date', self.file.date.isoformat(), continued=continued_comment))
            elif line == '${BRIEF}':
                header_block.append(self._crate_doxy_comment(
                    '@brief', self.file.brief, continued=continued_comment))
            else:
                header_block.append(line)
        return header_block

    def _create_FILE_part(self, continued: bool = False) -> str:
        ret = ''
        file_path = self.file.relative_path
        if self.context.settings.header.filename_only:
            file_path = os.path.basename(file_path)
        else:
            for path_spec in self.context.settings.header.file_base_path:
                potential_part_to_remove = os.path.join(*path_spec)
                if(file_path.startswith(potential_part_to_remove)) and len(potential_part_to_remove) > 0:
                    file_path = file_path[len(potential_part_to_remove)+1:]
                    break
        ret = self._crate_doxy_comment(
            '@file', file_path, continued=continued)
        return ret

    def _verify_header(self, header: str) -> bool:
        ret = True
        # TODO
        return ret
