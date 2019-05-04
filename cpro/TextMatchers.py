from typing import List, Tuple
import copy


class MatchResult:
    def __init__(self) -> None:
        self.lines: List[int] = []

    def is_valid(self) -> bool:
        return len(self.lines) > 0


class Predicate:
    def __init__(self) -> None:
        raise NotImplementedError

    def test(self, string: str) -> bool:
        raise NotImplementedError


class PredicateBeginsWith(Predicate):
    def __init__(self, pattern: str, use_regex: bool = False) -> None:
        self.pattern: str = pattern
        # TODO: impelement regex

    def test(self, string: str) -> bool:
        return string.startswith(self.pattern)


def match_group(lines: List[str], predicate_group: Tuple) -> List[MatchResult]:
    total_result = MatchResult()
    line_number = 0
    for line in lines:
        if predicate_group[0].test(line):
            result = True
            local_line_number = 0
            try:
                for pred in predicate_group:
                    result = (result or pred.test(line))
                    total_result.lines.append(line_number+local_line_number)
                    local_line_number = local_line_number+1
            except:
                pass
        line_number = line_number + 1
    return __detect_sections(total_result)


def match_comments(lines: List[str]) -> List[MatchResult]:
    ret = []
    in_block = False
    line_n = 0
    for line in lines:
        stripped = line.strip()
        is_comment = False
        if in_block:
            is_comment = True
            if(stripped.endswith('*/')):
                in_block = False
        else:
            if(stripped.startswith('//')):
                is_comment = True
            elif(stripped.startswith('/*') and stripped.endswith('*/')):
                is_comment = True
            elif(stripped.startswith('/*')):
                is_comment = True
                in_block = True

        if(is_comment):
            ret.append(line_n)
        line_n = line_n + 1

    mr = MatchResult()
    mr.lines = ret
    return __detect_sections(mr)


def __detect_sections(total_result: MatchResult) -> List[MatchResult]:
    ret = []
    if(total_result.is_valid()):
        prev_num = total_result.lines[0]
        mr = MatchResult()
        mr.lines.append(prev_num)
        for num in total_result.lines[1:]:
            if not ((num - prev_num) == 1):
                ret.append(copy.deepcopy(mr))
                mr = MatchResult()
            mr.lines.append(num)
            prev_num = num
    if(len(mr.lines) > 0):
        ret.append(copy.deepcopy(mr))
    return ret
