import os
from typing import List
import logging as log
import datetime

import Context


class Author:
    def __init__(self) -> None:
        self.name: str = ''
        self.email: str = ''

    def __hash__(self) -> int:
        ret = (self.name + self.email).__hash__()
        return ret

    def __str__(self) -> str:
        return self.name + ' <' + self.email + '>'

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
        try:
            blame_str = self.context.git(
                ['blame', self.absolute_path, '--porcelain'])
            self.authors: List[Author] = self._read_authors(blame_str)
            self.date: datetime.date = self._read_date(blame_str)
        except:
            raise

        self.lines = self._read_lines()

    def _read_lines(self) -> List[str]:
        data: List[str] = []
        with open(self.absolute_path, 'r', newline='') as f:
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
        current_contents = self._read_lines()
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
                author = Author()
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
