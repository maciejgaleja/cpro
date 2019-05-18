import Context
import Operations
import File
import logging
import Settings
import os
from typing import List
import sys
import version
import ProgressReporter
import FileFinder


def print_version() -> None:
    print('v' + version.version)


def main() -> None:
    print_version()
    root_path = '.'

    ctx = Context.Context(root_path)

    fileFinder: FileFinder.FileFinder = FileFinder.FileFinder(ctx)
    filenames: List[str] = fileFinder.get_file_list()

    files: List[File.File] = []
    for filename in filenames:
        file = File.File(filename, ctx)
        files.append(file)
        ctx.reporter.update(ProgressReporter.ReportItem(file.relative_path))

    for file in files:
        file.open()
        ctx.reporter.update_item(
            file.relative_path, ProgressReporter.CproStage.OPEN, 1)

        oper = Operations.HeaderComment(ctx, file)
        oper.run()
        ctx.reporter.update_item(
            file.relative_path, ProgressReporter.CproStage.HEADER, 1)

        operInc = Operations.PreIncludes(ctx, file)
        operInc.run()
        ctx.reporter.update_item(
            file.relative_path, ProgressReporter.CproStage.INCLUDE, 1)

        oper2 = Operations.FooterComment(ctx, file)
        oper2.run()
        ctx.reporter.update_item(
            file.relative_path, ProgressReporter.CproStage.FOOTER, 1)

        oper3 = Operations.ClangFormatOperation(ctx, file)
        oper3.run()
        ctx.reporter.update_item(
            file.relative_path, ProgressReporter.CproStage.CLANG, 1)

        file_changed = file.write_to_disk()
        file_status = 0
        if file_changed:
            file_status = 1
        else:
            file_status = -1
        ctx.reporter.update_item(
            file.relative_path, ProgressReporter.CproStage.FILE_MODIFIED, file_status)


if __name__ == "__main__":
    logging.basicConfig(level=logging.CRITICAL)
    main()
