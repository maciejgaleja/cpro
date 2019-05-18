from . import Operations
import TextMatchers
import File
import Context
import logging as log


class PreIncludes(Operations.CommentOperation):
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


class FooterComment(Operations.CommentOperation):
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
