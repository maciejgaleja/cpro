from . import Operations
import TextMatchers as tm
import File
import Context
import logging as log
from typing import List


class SectionComment(Operations.CommentOperation):
    def __init__(self, context: Context.Context, file_object: File.File, tokens_to_match: List[str], comment_text: str) -> None:
        super().__init__(context, file_object)
        self.tokens: List[str] = tokens_to_match
        self.comment_text: str = comment_text

    def run(self) -> None:
        settings = self.context.settings.sections

        potential_lines = self._find_potential_lines()

        if len(potential_lines) > 0:
            expected_comment_line_index = potential_lines[0] - 1
            expected_comment_str = self._create_comment(
                self.comment_text, solid=settings.solid_comment_line)

            if not (self.lines[expected_comment_line_index]
                    == expected_comment_str):
                print('inserting ' + str(expected_comment_line_index+1) +
                      ': ' + self.comment_text)
                self._insert_before(
                    expected_comment_line_index+1, [expected_comment_str])

        self.file.write_lines(self.lines)

    def _find_potential_lines(self) -> List[int]:
        potential_lines: List[int] = []
        for token in self.tokens:
            predicate = (tm.PredicateBeginsWith(token),)
            results = tm.match_group(self.lines, predicate)
            for result in results:
                potential_lines.extend(result.lines)
        potential_lines.sort()
        return potential_lines


class SectionCommentWorker(Operations.FileOperation):
    def __init__(self, context: Context.Context, file_object: File.File) -> None:
        super().__init__(context, file_object)

    def run(self) -> None:
        sections_map = self.context.settings.sections.templates
        for comment_text in sections_map:
            tokens = sections_map[comment_text]
            section_object = SectionComment(
                self.context, self.file, tokens, comment_text)
            section_object.run()
        #  ['#include '], 'Includes'


class FooterComment(Operations.CommentOperation):
    def __init__(self, context: Context.Context, file_object: File.File) -> None:
        super().__init__(context, file_object)

    def run(self) -> None:
        comments = tm.join_results(
            tm.match_comments(self.lines))
        if len(self.lines) - 1 in comments.lines:
            self._delete_lines([-1])
        else:
            pass

        if not len(self.lines[-1]) == 0:
            self.lines.append('')

        for line in self.context.settings.footer.content:
            self.lines.append(line)

        self.file.write_lines(self.lines)
