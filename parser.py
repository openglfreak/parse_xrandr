import dataclasses
import enum
from typing import Any, Callable, Iterable, Iterator, Match, Optional, \
                   Pattern, Tuple, Union

__all__ = ('ParserAction', 'ParserState', 'parse')


@enum.unique
class ParserAction(enum.Enum):
    Restart = enum.auto()
    Continue = enum.auto()
    Stop = enum.auto()
    Again = enum.auto()


@dataclasses.dataclass
class ParserState:
    string: str = ''
    position: int = 0
    data: Any = None
    default_action: ParserAction = ParserAction.Restart
    again_not_matched_action: ParserAction = ParserAction.Continue


MatchCallbackReturn = Union[Optional[ParserAction],
                            Tuple[Optional[ParserAction], bool]]
MatchCallback = Callable[[ParserState, Match[str]], MatchCallbackReturn]


def parse(
        string: str,
        position: int,
        regexes: Iterable[Tuple[Pattern[str], MatchCallback]],
        data: Any = None,
        default_action: ParserAction = ParserAction.Restart,
        again_not_matched_action: ParserAction = ParserAction.Continue
) -> Tuple[str, int, Any, int]:
    if again_not_matched_action == ParserAction.Again:
        raise ValueError('Parameter again_not_matched_action may not be '
                         'ParserAction.Again')

    state: ParserState = ParserState(string, position, data, default_action,
                                     again_not_matched_action)
    matches: int = _parse(state, regexes)
    return state.string, state.position, state.data, matches


def _parse(
        state: ParserState,
        regexes: Iterable[Tuple[Pattern[str], MatchCallback]]
) -> int:
    matches: int = 0

    action: ParserAction = ParserAction.Restart
    matched: bool
    regex_iter: Iterator[Tuple[Pattern[str], MatchCallback]]
    while action != ParserAction.Stop:
        if action == ParserAction.Restart:
            matched = False
            regex_iter = iter(regexes)
            action = ParserAction.Continue

        regex: Pattern[str]
        func: MatchCallback
        if action == ParserAction.Continue:
            try:
                regex, func = next(regex_iter)
            except StopIteration:
                if not matched:
                    break
                action = ParserAction.Restart
                continue
        else:
            assert action == ParserAction.Again, \
                'Internal parser state corrupt'

        match: Optional[Match[str]] = \
            regex.match(state.string, pos=state.position)
        if not match:
            if action == ParserAction.Again:
                action = state.again_not_matched_action
            continue
        matched = True
        matches += 1

        ret: MatchCallbackReturn = func(state, match)
        if ret is None:
            action = state.default_action
            state.position = match.end()
        elif isinstance(ret, ParserAction):
            action = ret
            state.position = match.end()
        elif isinstance(ret, tuple):
            if len(ret) > 2:
                raise ValueError(
                    'Too many values returned from match callback'
                )

            if ret[0] is None:
                action = state.default_action
            elif isinstance(ret[0], ParserAction):
                action = ret[0]
            else:
                raise ValueError('Returned action value is not a ParserAction')
            if len(ret) > 1 and ret[1]:
                state.position += match.end() - match.start()
        else:
            raise ValueError('Invalid value returned from match callback')

    return matches
