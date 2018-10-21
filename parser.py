# noqa: W191,W293
from enum import unique, Enum, auto
from typing import Any, Iterable, Tuple, Pattern, Callable, Match, Union, \
	Optional

__all__ = (
	'ParserAction',
	'parse'
)


@unique
class ParserAction(Enum):
	Restart = auto()
	Continue = auto()
	Stop = auto()
	Again = auto()


MatchCallbackReturn = Union[
	Tuple[str],
	Tuple[str, int],
	Tuple[str, int, Any],
	Tuple[str, int, Any, ParserAction]
]
MatchCallbackType = Callable[[str, int, Any, Match], MatchCallbackReturn]


def parse(
	s: str,
	pos: int,
	obj: Any,
	regexes: Iterable[Tuple[Pattern, MatchCallbackType]],
	default_action: ParserAction = ParserAction.Restart,
	again_nomatch_action: ParserAction = ParserAction.Continue
) -> Tuple[str, int, Any, int]:
	assert again_nomatch_action != ParserAction.Again
	
	matches: int = 0
	
	action: ParserAction = ParserAction.Restart
	while True:
		matched: bool
		regex: Pattern
		func: MatchCallbackType
		
		if action == ParserAction.Stop:
			break
		if action == ParserAction.Restart:
			matched = False
			regex_iter = iter(regexes)
			action = ParserAction.Continue
		if action == ParserAction.Continue:
			try:
				regex, func = next(regex_iter)
			except StopIteration:
				if not matched:
					break
				action = ParserAction.Restart
				continue
		else:
			assert action == ParserAction.Again
		
		match: Optional[Match] = regex.match(s, pos=pos)
		if not match:
			if action == ParserAction.Again:
				action = again_nomatch_action
			continue
		matched = True
		matches += 1
		
		action = default_action
		
		ret: MatchCallbackReturn = func(s, pos, obj, match)
		if ret is None:
			continue
		
		if len(ret) < 1:
			continue
		s = ret[0]
		if len(ret) < 2:
			continue
		pos = ret[1]
		if len(ret) < 3:
			continue
		obj = ret[2]
		if len(ret) < 4:
			continue
		action = ret[3]
	
	return s, pos, obj, matches
