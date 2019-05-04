from typing import List, Tuple


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


def match_group(lines: List[str], predicate_group: Tuple) -> MatchResult:
    ret = MatchResult()
    line_number = 0
    for line in lines:
        ret.lines = []
        if predicate_group[0].test(line):
            result = True
            local_line_number = 0
            try:
                for pred in predicate_group:
                    result = (result or pred.test(line))
                    ret.lines.append(line_number+local_line_number)
                    local_line_number = local_line_number+1
                if result == True:
                    break
            except:
                pass
        line_number = line_number + 1
    return ret
