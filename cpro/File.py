import os
from typing import List
import logging as log
import datetime

from FileMetadataBase import FileMetadata
import Context


class Author:
    def __init__(self, context: Context.Context) -> None:
        self.name: str = ''
        self.email: str = ''
        self.context: Context.Context = context

    def __hash__(self) -> int:
        ret = (self.name + self.email).__hash__()
        return ret

    def __str__(self) -> str:
        ret: str = self.name
        if self.context.settings.metadata.authors_include_email:
            ret = ret + ' <' + self.email.replace("@", "[at]") + '>'
        return ret

    def __repr__(self) -> str:
        return self.__str__()


class File:
    def __init__(self, filename: str, context: Context.Context) -> None:
        self.context: Context.Context = context

        try:
            self.absolute_path: str = os.path.abspath(filename)
            self.relative_path: str = self.absolute_path.replace(
                context.path, '')[1:]
            os.stat(self.absolute_path)

        except:
            raise

    def open(self) -> None:
        self.authors: List[Author] = []
        self.date: datetime.date = datetime.date.today()
        self.brief = ''
        try:
            blame_str = self.context.git(
                ['blame', self.absolute_path, '--porcelain'])
            self.authors = self._read_authors(blame_str)
            self.date = self._read_date(blame_str)

            self._metadata: FileMetadata = self.context.metadata_base.get(
                self.relative_path)
            self.brief = self._metadata.brief
            additional_authors = self._metadata.additional_authors
            for author in additional_authors:
                author_object = Author(self.context)
                author_object.name = author[0]
                author_object.email = author[1]
                self.authors.append(author_object)
        except:
            pass

        self.lines = File.read_lines(self.absolute_path)

    @staticmethod
    def read_lines(filename: str) -> List[str]:
        data: List[str] = []
        with open(filename, 'r', newline='') as f:
            data_str = f.read()

        data = data_str.splitlines()

        for line in data:
            line = line.replace('\r', '')
            line = line.replace('\n', '')

        return data

    def write_lines(self, lines: List[str]) -> None:
        self.lines = lines

    def write_to_disk(self) -> bool:
        ret: bool = False
        current_contents = File.read_lines(self.absolute_path)
        if not self.lines == current_contents:
            with open(self.absolute_path, 'w', newline='') as f:
                for line in self.lines:
                    f.write(line)
                    f.write(self.context.settings.code.newline)
                    ret = True
        else:
            ret = False
        return ret

    def _read_authors(self, blame_str: str) -> List[Author]:
        lines = blame_str.split('\n')
        all_authors = []
        line_number = 0
        for line in lines:
            if (line.startswith('author '))and (not 'author Not Committed Yet' in line):
                author = Author(self.context)
                author.name = lines[line_number].replace('author', '').strip()
                author.email = lines[line_number +
                                     1].replace('author-mail', '').replace('<', '').replace('>', '').strip()
                if not author.name in self.context.settings.metadata.authors_exclude:
                    all_authors.append(author)
            line_number = line_number + 1

        hashed_authors = {}
        for author in all_authors:
            hashed_authors[hash(author)] = author
        ret = list(hashed_authors.values())
        log.debug('Authors of file ' +
                  os.path.basename(self.absolute_path) + ': ' + repr(ret))
        return ret

    def _read_date(self, blame_str: str) -> datetime.date:
        lines = blame_str.split('\n')
        timestamps = []
        for line in lines:
            if ('author-time ' in line):
                timestamp = int(float(line.replace('author-time', '').strip()))
                timestamps.append(timestamp)
        min_timestamp = timestamps[0]
        for t in timestamps:
            min_timestamp = min(min_timestamp, t)
        ret = datetime.date.fromtimestamp(min_timestamp)
        return ret
