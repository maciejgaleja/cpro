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


def format_extensions(extensions: List[str]) -> List[str]:
    full_extensions = []
    for extension in extensions:
        full_extensions.append(extension.upper())
        full_extensions.append(extension.lower())
    return full_extensions


def filter_by_extension(input: List[str], extensions: List[str]) -> List[str]:
    output = []
    for file in input:
        if file.endswith(tuple(extensions)):
            output.append(os.path.realpath(file))
    return output


def get_file_list(start_dir: str, extensions: List[str], recursive: bool = False) -> List[str]:
    full_dir = os.path.realpath(start_dir)
    full_extensions = format_extensions(extensions)
    logging.debug("Getting file list:")
    logging.debug("\troot directory: {0}".format(full_dir))
    logging.debug("\tsearching extensions: {0}".format(
        " ".join(full_extensions)))
    logging.debug("\trecursive: {0}".format(recursive))

    all_candidates = []

    if recursive:
        for root, dirs, files in os.walk(full_dir):
            for name in files:
                all_candidates.append(os.path.join(root, name))
            for name in dirs:
                all_candidates.append(os.path.join(root, name))
    else:
        candinates = os.listdir(full_dir)
        for candidate in candinates:
            all_candidates.append(os.path.join(full_dir, candidate))

    files = filter_by_extension(all_candidates, full_extensions)
    logging.debug("\tFound files:\n\t\t{0}".format("\n\t\t".join(files)))
    return files


def print_version() -> None:
    print('v' + version.version)


def main() -> None:
    print_version()
    root_path = '.'

    ctx = Context.Context(root_path)

    if len(sys.argv) == 1:
        filenames = get_file_list(root_path, ['.cpp', '.hpp', '.h'], True)
    elif len(sys.argv) == 2:
        filenames = [sys.argv[1]]
    else:
        logging.error("Use 0 or 1 argument")
        return

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

        file.write_to_disk()


if __name__ == "__main__":
    logging.basicConfig(level=logging.CRITICAL)
    main()
