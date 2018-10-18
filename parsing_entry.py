from shutil import which
from subprocess import Popen, PIPE

from .parser import *
from .parsing_fragments import *

__all__ = (
	'parse_xrandr',
	'parse_screens'
)

def parse_xrandr():
	xrandr_path = which('xrandr')
	if not xrandr_path:
		raise FileNotFoundError('xrandr not found')
	
	with Popen(('xrandr', '--verbose'), executable=xrandr_path, stdout=PIPE, universal_newlines=True) as popen:
		xrandr_output = popen.stdout.read()
	
	return parse_screens(xrandr_output)

def parse_screens(xrandr_output, start=0):
	xrandr_output, start, screens, matches = parse(
		xrandr_output,
		start,
		{},
		((screen_regex, screen_func),)
	)
	success = start == len(xrandr_output)
	return screens, success
