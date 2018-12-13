# noqa: W191,W293
from shutil import which
from subprocess import Popen, PIPE
from typing import Tuple, Dict

from .parser import parse
from .classes import XRandRScreen
from .parsing_fragments import screen_regex, screen_func

__all__ = (
	'parse_xrandr',
	'parse_screens'
)


def parse_xrandr() -> Tuple[Dict[str, XRandRScreen], bool]:
	xrandr_path = which('xrandr')
	if not xrandr_path:
		raise FileNotFoundError('xrandr not found')
	
	with Popen(
		('xrandr', '--verbose'),
		executable=xrandr_path,
		stdout=PIPE,
		universal_newlines=True
	) as popen:
		xrandr_output: str = popen.stdout.read()
	
	return parse_screens(xrandr_output)


def parse_screens(
	xrandr_output: str,
	start: int = 0
) -> Tuple[Dict[str, XRandRScreen], bool]:
	xrandr_output, start, screens, matches = parse(
		xrandr_output,
		start,
		((screen_regex, screen_func),),
		{}
	)
	success = start == len(xrandr_output)
	return screens, success
