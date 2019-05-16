import Context
from typing import List
import logging
import os


class FileFinder():
    def __init__(self, context: Context.Context) -> None:
        self.context = context

    def _get_extensions(self) -> List[str]:
        full_extensions = []
        extensions = self.context.settings.scope.extensions_source + \
            self.context.settings.scope.extensions_header
        for extension in extensions:
            extension = extension.replace('.', '')
            extension = '.' + extension
            full_extensions.append(extension.upper())
            full_extensions.append(extension.lower())
        return full_extensions

    def _filter_by_extension(self, input: List[str], extensions: List[str]) -> List[str]:
        output = []
        for file in input:
            if file.endswith(tuple(extensions)):
                output.append(os.path.realpath(file))
        return output

    def get_file_list(self) -> List[str]:
        full_extensions = self._get_extensions()

        all_candidates = []

        for start_dir in self.context.settings.scope.source_directories:
            full_dir = os.path.realpath(start_dir)
            for root, dirs, files in os.walk(full_dir):
                for name in files:
                    all_candidates.append(os.path.join(root, name))
                for name in dirs:
                    all_candidates.append(os.path.join(root, name))

        files = self._filter_by_extension(all_candidates, full_extensions)
        return files
