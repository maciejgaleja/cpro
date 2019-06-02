from . import Operations
import TextMatchers
import File
import Context
from typing import List, Tuple
import pathlib
import os.path


class HeaderGuard(Operations.CommentOperation):
    def __init__(self, context: Context.Context, file_object: File.File) -> None:
        super().__init__(context, file_object)

    def run(self) -> None:
        if self._is_file_a_header():
            lines_ifndef, guard_ifndef = self._find_tokens('#ifndef')
            lines_define, guard_define = self._find_tokens('#define')
            lines_endif, guard_endif = self._find_tokens('#endif')

            token_found_in_file = self._find_token_in_file(
                guard_ifndef, guard_define)
            if not token_found_in_file == '':
                self._remove_old_guard(
                    token_found_in_file, lines_ifndef, lines_define, lines_endif)

            token_to_insert = self._create_token()
            print(token_to_insert)

            all_comments = TextMatchers.match_comments(self.lines)
            comments_top: List[int] = []
            comments_bottom: List[int] = []
            try:
                comments_top = all_comments[0].lines
                if len(all_comments) > 1:
                    comments_bottom = all_comments[-1].lines
            except KeyError:
                pass

            lines_already_inserted = 0
            block_top = self._create_top_block()
            block_bottom = self._create_bottom_block()
            self._insert_before(
                comments_top[-1]+1, block_top)
            lines_already_inserted += len(block_top)
            self._insert_before(
                comments_bottom[0]+lines_already_inserted, block_bottom)

    def _is_file_a_header(self) -> bool:
        extension = pathlib.Path(
            self.file.absolute_path).suffix.replace('.', '')
        return extension in self.context.settings.scope.extensions_header

    def _find_tokens(self, predicate_str: str) -> Tuple[List[int], List[str]]:
        ret: List[str] = []
        predicate = (TextMatchers.PredicateBeginsWith(predicate_str),)
        matches = TextMatchers.join_results(
            TextMatchers.match_group(self.lines, predicate)).lines
        for mr in matches:
            ret.append(
                self.lines[mr].replace(predicate_str, '').strip())
        return (matches, ret)

    def _find_token_in_file(self, guard_ifndef: List[str], guard_define: List[str]) -> str:
        token_found_in_file: str = ''
        for token in guard_ifndef:
            if token in guard_define:
                token_found_in_file = token
                break
        return token_found_in_file

    def _remove_old_guard(self, token_found_in_file: str, lines_ifndef: List[int], lines_define: List[int], lines_endif: List[int]) -> None:
        lines_to_delete: List[int] = []
        for line in lines_ifndef:
            if token_found_in_file in self.lines[line]:
                lines_to_delete.append(line)
        for line in lines_define:
            if token_found_in_file in self.lines[line]:
                lines_to_delete.append(line)
        for line in lines_endif:
            if token_found_in_file in self.lines[line]:
                lines_to_delete.append(line)
        lines_already_deleted = 0
        for line in lines_to_delete:
            del self.lines[line-lines_already_deleted]
            lines_already_deleted += 1

    def _create_top_block(self) -> List[str]:
        ret: List[str] = []
        settings = self.context.settings.header_guard
        token = self._create_token()
        ret.append('')
        ret.append('#ifndef ' + token)
        ret.append('#define ' + token)
        return ret

    def _create_bottom_block(self) -> List[str]:
        ret: List[str] = []
        settings = self.context.settings.header_guard
        token = self._create_token()
        ret.append('')
        ret.append('#endif ' + settings.endif_comment_begin +
                   token + settings.endif_comment_end)
        return ret

    def _create_token(self) -> str:
        ret: str = ''
        settings = self.context.settings.header_guard

        path = self.file.relative_path
        for path_spec in settings.file_base_path:
            potential_part_to_remove = os.path.join(*path_spec)
            if(path.startswith(potential_part_to_remove)) and len(potential_part_to_remove) > 0:
                path = path[len(potential_part_to_remove)+1:]
                break

        path = path.replace('/', settings.path_separator)
        path = path.replace('\\', settings.path_separator)
        path = path.replace('.', settings.extension_separator)
        path = path.upper()
        ret = settings.prefix + path + settings.suffix
        print(ret)
        return ret
