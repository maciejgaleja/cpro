import Context
import Operations.Operations
import Operations.Header
import Operations.Sections
import Operations.ClangFormat
import File
import logging
import Settings
import os
from typing import List
import sys
import version
import ProgressReporter
import FileFinder
import Errors
import FancyOutput
import OutputManager


def print_version() -> None:
    print('v' + version.version)


def main() -> None:
    FancyOutput.init()
    try:
        print_version()
        root_path = '.'

        ctx = Context.Context(root_path)
        outputManager = OutputManager.OutputManager()
        reporter = ProgressReporter.ProgressReporter(outputManager)

        fileFinder: FileFinder.FileFinder = FileFinder.FileFinder(ctx)
        filenames: List[str] = fileFinder.get_file_list()

        files: List[File.File] = []
        for filename in filenames:
            file = File.File(filename, ctx)
            files.append(file)
            reporter.update(
                ProgressReporter.ReportItem(file.relative_path))

        for file in files:
            file.open()
            reporter.update_item(
                file.relative_path, ProgressReporter.CproStage.OPEN,
                Operations.Operations.OperationResult.OK)

            oper = Operations.Header.HeaderComment(ctx, file)
            oper.run()
            reporter.update_item(
                file.relative_path, ProgressReporter.CproStage.HEADER,
                Operations.Operations.OperationResult.OK)

            if ctx.settings.operations.pre_includes:
                operInc = Operations.Sections.PreIncludes(ctx, file)
                operInc.run()
                reporter.update_item(
                    file.relative_path, ProgressReporter.CproStage.INCLUDE,
                    Operations.Operations.OperationResult.OK)
            else:
                reporter.update_item(
                    file.relative_path, ProgressReporter.CproStage.INCLUDE,
                    Operations.Operations.OperationResult.SKIPPED)

            oper2 = Operations.Sections.FooterComment(ctx, file)
            oper2.run()
            reporter.update_item(
                file.relative_path, ProgressReporter.CproStage.FOOTER,
                Operations.Operations.OperationResult.OK)

            oper3 = Operations.ClangFormat.ClangFormatOperation(ctx, file)
            oper3.run()
            reporter.update_item(
                file.relative_path, ProgressReporter.CproStage.CLANG,
                Operations.Operations.OperationResult.OK)

            file_changed = file.write_to_disk()
            reporter.update_item(
                file.relative_path, ProgressReporter.CproStage.FILE_WRITE,
                Operations.Operations.OperationResult.OK)
            reporter.update_file_status(
                file.relative_path, file_changed)

    except Errors.CproException as e:
        print(' '. join(e.args))


if __name__ == "__main__":
    logging.basicConfig(level=logging.CRITICAL)
    main()
