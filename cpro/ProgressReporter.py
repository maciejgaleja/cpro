from typing import Dict, List
from enum import Enum
import sys

from FancyOutput import colors, signs

from Operations.Operations import OperationResult as OperationResult
import OutputManager


class CproStage(Enum):
    OPEN = 0
    HEADER = 1
    INCLUDE = 2
    GUARD = 2
    FOOTER = 100
    CLANG = 200
    FILE_WRITE = 300


class ReportItem:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.stages: Dict[CproStage, OperationResult] = {CproStage.OPEN: OperationResult.PENDING,
                                                         CproStage.HEADER: OperationResult.PENDING,
                                                         CproStage.INCLUDE: OperationResult.PENDING,
                                                         CproStage.GUARD: OperationResult.PENDING,
                                                         CproStage.FOOTER: OperationResult.PENDING,
                                                         CproStage.CLANG: OperationResult.PENDING,
                                                         CproStage.FILE_WRITE: OperationResult.PENDING}
        self.file_modified: bool = False

    def __str__(self) -> str:
        ret: str = self.name.ljust(60)
        for stage in self.stages.keys():
            if stage == CproStage.FILE_WRITE:
                if self.file_modified:
                    ret = ret + colors.green(signs.check_heavy)
                else:
                    ret = ret + colors.white(signs.check_heavy)
            else:
                if self.stages[stage] == OperationResult.PENDING:
                    ret = ret + colors.white('-'.ljust(4))
                elif self.stages[stage] == OperationResult.SKIPPED:
                    ret = ret + \
                        colors.green(signs.arrow_triangle_right.ljust(4))
                elif self.stages[stage] == OperationResult.OK:
                    ret = ret + \
                        colors.green(signs.check_heavy.ljust(4))
                else:
                    ret = ret + colors.red('x'.ljust(4))
        return ret


class ProgressReporter():
    def __init__(self, output_manager: OutputManager.OutputManager) -> None:
        self.items: Dict[str, ReportItem] = {}
        self.output = output_manager

    def update(self, item: ReportItem) -> None:
        self.items[item.name] = item

    def update_item(self, name: str, stage: CproStage, value: OperationResult) -> None:
        self.items[name].stages[stage] = value

    def update_file_status(self, name: str, modified: bool) -> None:
        self.items[name].file_modified = modified
        self.output.write(str(self.items[name]))

    def to_string(self) -> str:
        ret: str = ''
        for item in self.items.values():
            ret = ret + str(item) + '\n'
        return ret
