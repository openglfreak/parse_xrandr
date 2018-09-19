from enum import unique, Enum, auto

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

def parse(s, pos, obj, regexes, default_action=ParserAction.Restart, again_nomatch_action=ParserAction.Continue):
	assert again_nomatch_action != ParserAction.Again
	
	matches = 0
	
	action = ParserAction.Restart
	while True:
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
		
		match = regex.match(s, pos=pos)
		if not match:
			if action == ParserAction.Again:
				action = again_nomatch_action
			continue
		matched = True
		matches += 1
		
		action = default_action
		
		ret = func(s, pos, obj, match)
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
