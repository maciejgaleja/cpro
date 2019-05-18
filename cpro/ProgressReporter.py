from typing import Dict, List
import OutputManager
from enum import Enum
from FancyOutput import colors, signs


class CproStage(Enum):
    OPEN = 0
    HEADER = 1
    INCLUDE = 2
    FOOTER = 100
    CLANG = 200
    FILE_MODIFIED = 300


class ReportItem:
    def __init__(self, name: str)->None:
        self.name: str = name
        self.stages: Dict[CproStage, int] = {CproStage.OPEN: 0,
                                             CproStage.HEADER: 0,
                                             CproStage.INCLUDE: 0,
                                             CproStage.FOOTER: 0,
                                             CproStage.CLANG: 0,
                                             CproStage.FILE_MODIFIED: 0}
        self.file_modified: bool = False

    def __str__(self)->str:
        ret: str = self.name.ljust(70)
        for stage in self.stages.keys():
            if stage == CproStage.FILE_MODIFIED:
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
    def __init__(self, output_manager: OutputManager.OutputManager)->None:
        self.items: Dict[str, ReportItem] = {}
        self.output = output_manager

    def update(self, item: ReportItem)->None:
        self.items[item.name] = item
        self.output.write(self.to_string())

    def update_item(self, name: str, stage: CproStage, value: int)->None:
        self.items[name].stages[stage] = value
        self.output.write(self.to_string())

    def to_string(self)->str:
        ret: str = ''
        for item in self.items.values():
            ret = ret + str(item) + '\n'
        return ret
