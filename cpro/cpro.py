import Context
from Operations.Operations import OperationResult as OperationResult
import Operations.Header
import Operations.Sections
import Operations.ClangFormat
import Operations.HeaderGuard
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
    print_version()
    FancyOutput.init()

    if len(sys.argv) == 1:
        try:
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
                    OperationResult.OK)

                result = OperationResult.SKIPPED
                if ctx.settings.operations.format_header:
                    operHeader = Operations.Header.HeaderComment(
                        ctx, file)
                    operHeader.run()
                    result = OperationResult.OK
                reporter.update_item(
                    file.relative_path, ProgressReporter.CproStage.HEADER,
                    result)

                result = OperationResult.SKIPPED
                if ctx.settings.operations.format_footer:
                    operFooter = Operations.Sections.FooterComment(ctx, file)
                    operFooter.run()
                    result = OperationResult.OK
                reporter.update_item(
                    file.relative_path, ProgressReporter.CproStage.FOOTER,
                    result)

                result = OperationResult.SKIPPED
                if ctx.settings.operations.header_guard:
                    operHeaderGuard = Operations.HeaderGuard.HeaderGuard(
                        ctx, file)
                    operHeaderGuard.run()
                    result = OperationResult.OK
                reporter.update_item(
                    file.relative_path, ProgressReporter.CproStage.FOOTER,
                    result)

                result = OperationResult.SKIPPED
                if ctx.settings.operations.sections:
                    operSect = Operations.Sections.SectionCommentWorker(
                        ctx, file)
                    operSect.run()
                    result = OperationResult.OK
                reporter.update_item(
                    file.relative_path, ProgressReporter.CproStage.INCLUDE,
                    result)

                file_changed = file.write_to_disk()

                result = OperationResult.SKIPPED
                if ctx.settings.operations.clang_format:
                    operClang = Operations.ClangFormat.ClangFormatOperation(
                        ctx, file)
                    operClang.run()
                    result = OperationResult.OK
                reporter.update_item(
                    file.relative_path, ProgressReporter.CproStage.CLANG,
                    result)

                file_changed = file_changed or file.write_to_disk()
                reporter.update_item(
                    file.relative_path, ProgressReporter.CproStage.FILE_WRITE,
                    OperationResult.OK)
                reporter.update_file_status(
                    file.relative_path, file_changed)

        except Errors.CproException as e:
            print(str(e))
    elif len(sys.argv) == 2 and sys.argv[1] == 'init':
        filename = './.cpro.json'
        if not os.path.isfile(filename):
            f = open(filename, 'w')
            f.write('{ }')
            f.close()
        context = Context.Context('.')


if __name__ == "__main__":
    logging.basicConfig(level=logging.CRITICAL)
    main()
