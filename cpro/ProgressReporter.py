from typing import Dict, List
from enum import Enum
import ansiescapes  # type: ignore
import sys

from FancyOutput import colors, signs

from Operations.Operations import OperationResult as OperationResult
import OutputManager


class CproStage(Enum):
    OPEN = 0
    HEADER = 1
    INCLUDE = 2
    FOOTER = 100
    CLANG = 200
    FILE_WRITE = 300


class ReportItem:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.stages: Dict[CproStage, OperationResult] = {CproStage.OPEN: OperationResult.PENDING,
                                                         CproStage.HEADER: OperationResult.PENDING,
                                                         CproStage.INCLUDE: OperationResult.PENDING,
                                                         CproStage.FOOTER: OperationResult.PENDING,
                                                         CproStage.CLANG: OperationResult.PENDING,
                                                         CproStage.FILE_WRITE: OperationResult.PENDING}
        self.file_modified: bool = False

    def __str__(self) -> str:
        ret: str = self.name.ljust(70)
        for stage in self.stages.keys():
            if stage == CproStage.FILE_WRITE:
                if self.stages[stage] == 1:
                    ret = ret + colors.green(signs.check_heavy)
                elif self.stages[stage] == 0:
                    ret = ret + colors.white('-')
                else:
                    ret = ret + colors.white(signs.check_heavy)
            else:
                if self.stages[stage] == 0:
                    ret = ret + colors.white('-'.ljust(4))
                else:
                    ret = ret + colors.green(signs.check_heavy.ljust(4))
        return ret


class ProgressReporter():
    def __init__(self, output_manager: OutputManager.OutputManager) -> None:
        self.items: Dict[str, ReportItem] = {}
        self.output = output_manager
        self._lines_written = 0

    def update(self, item: ReportItem) -> None:
        self.items[item.name] = item
        self._write_to_console(self.to_string())

    def update_item(self, name: str, stage: CproStage, value: OperationResult) -> None:
        self.items[name].stages[stage] = value
        self._write_to_console(self.to_string())

    def update_file_status(self, name: str, modified: bool) -> None:
        self.items[name].file_modified = modified

    def to_string(self) -> str:
        ret: str = ''
        for item in self.items.values():
            ret = ret + str(item) + '\n'
        return ret

    def _write_to_console(self, text: str) -> None:
        sys.stdout.write(ansiescapes.eraseLines(self._lines_written + 2))
        self.output.write(self.to_string())
        self._lines_written = len(text.splitlines(keepends=True))
