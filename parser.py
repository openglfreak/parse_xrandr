# noqa: W191,W293
from enum import unique, Enum, auto
from typing import (
	Any, Iterable, Tuple, Pattern, Iterator, Callable, Match, Union, Optional
)

__all__ = (
	'ParserAction',
	'ParserState',
	'parse'
)


@unique
class ParserAction(Enum):
	Restart = auto()
	Continue = auto()
	Stop = auto()
	Again = auto()


class ParserState:
	__slots__ = (
		'string',
		'position',
		'data',
		'default_action',
		'again_not_matched_action'
	)
	string: str
	position: int
	
	data: Any
	
	default_action: ParserAction
	again_not_matched_action: ParserAction
	
	def __init__(
		self,
		string: str = '',
		position: int = 0,
		data: Any = None,
		default_action: ParserAction = ParserAction.Restart,
		again_not_matched_action: ParserAction = ParserAction.Continue
	) -> None:
		self.string = string
		self.position = position
		self.data = data
		self.default_action = default_action
		self.again_not_matched_action = again_not_matched_action


MatchCallbackReturnType = Union[None, ParserAction, Tuple[ParserAction, bool]]
MatchCallbackType = Callable[[ParserState, Match], MatchCallbackReturnType]


def parse(
	string: str,
	position: int,
	regexes: Iterable[Tuple[Pattern, MatchCallbackType]],
	data: Any = None,
	default_action: ParserAction = ParserAction.Restart,
	again_not_matched_action: ParserAction = ParserAction.Continue
) -> Tuple[str, int, Any, int]:
	state: ParserState = ParserState(
		string,
		position,
		data,
		default_action,
		again_not_matched_action
	)
	matches: int = _parse(state, regexes)
	return state.string, state.position, state.data, matches

def _parse(
	state: ParserState,
	regexes: Iterable[Tuple[Pattern, MatchCallbackType]]
) -> int:
	assert state.again_not_matched_action != ParserAction.Again
	
	matches: int = 0
	
	action: ParserAction = ParserAction.Restart
	while True:
		matched: bool
		regex: Pattern
		func: MatchCallbackType
		regex_iter: Iterator[Tuple[Pattern, MatchCallbackType]]
		
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
		
		match: Optional[Match] = regex.match(state.string, pos=state.position)
		if not match:
			if action == ParserAction.Again:
				action = state.again_not_matched_action
			continue
		matched = True
		matches += 1
		
		ret: MatchCallbackReturnType = func(state, match)
		if ret is not None:
			if isinstance(ret, ParserAction):
				action = ret
				state.position = match.end()
			else:
				if ret[0] is not None:
					action = ret[0]
				else:
					action = state.default_action
				if ret[1]:
					state.position += match.end() - match.start()
		else:
			action = state.default_action
			state.position = match.end()
	
	return matches
