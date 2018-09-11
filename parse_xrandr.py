from re import compile, VERBOSE, MULTILINE, escape
from enum import IntEnum, IntFlag, Enum, unique, auto
from shutil import which
from subprocess import Popen, PIPE

__all__ = (
	'XRandRDimensions',
	'XRandROffset',
	'XRandRGeometry',
	'XRandRBorder',
	'XRandRTransform',
	'XRandRScreen',
	'XRandRScreenDimensionsList',
	'XRandROutput',
	'XRandROutputProperties',
	'parse_xrandr_screens',
	'parse_xrandr'
)

# Classes

class XRandRDimensions:
	__slots__ = ('width', 'height')
	def __init__(self, width=0, heigth=0):
		self.width = width
		self.height = heigth
class XRandROffset:
	__slots__ = ('x', 'y')
	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y

class XRandRGeometry:
	__slots__ = ('dimensions', 'offset')
	def __init__(self, dimensions=None, offset=None):
		self.dimensions = dimensions
		self.offset = offset

class XRandRBorder:
	__slots__ = ('left', 'top', 'right', 'bottom')
	def __init__(self, left=0, top=0, right=0, bottom=0):
		self.left = left
		self.top = top
		self.right = right
		self.bottom = bottom

class XRandRTransform:
	__slots__ = (
		'a', 'b', 'c',
		'd', 'e', 'f',
		'g', 'h', 'i',
		'filter'
	)
	def __init__(
		self,
		a=0, b=0, c=0,
		d=0, e=0, f=0,
		g=0, h=0, i=0,
		filter=None
	):
		self.a = a
		self.b = b
		self.c = c
		self.d = d
		self.e = e
		self.f = f
		self.g = g
		self.h = h
		self.i = i
		self.filter = filter

class XRandRScreen:
	__slots__ = ('number', 'dimensions', 'outputs')
	def __init__(self, number, dimensions=None, outputs=None):
		self.number = number
		self.dimensions = dimensions
		self.outputs = outputs
class XRandRScreenDimensionsList:
	__slots__ = ('minimum', 'current', 'maximum')
	def __init__(self, minimum=None, current=None, maximum=None):
		self.minimum = minimum
		self.current = current
		self.maximum = maximum

class XRandROutput:
	__slots__ = (
		'name',
		'connection',
		'primary',
		'geometry',
		'mode',
		'rotation',
		'reflection',
		'supported_rotations',
		'supported_reflections',
		'dimensions_mm',
		'panning',
		'tracking',
		'border',
		'properties',
		'modes'
	)
	@unique
	class Connection(IntEnum):
		Connected = 0
		Disconnected = 1
	class Rotation(IntEnum):
		Rotate_0 = 1
		Rotate_90 = 2
		Rotate_180 = 4
		Rotate_270 = 8
	class Reflection(IntFlag):
		Reflect_X = 16
		Reflect_Y = 32
	class Mode:
		__slots__ = (
			'name',
			'id',
			'dotclock',
			'flags',
			'current',
			'preferred',
			'width', 'h_sync_start', 'h_sync_end', 'h_total', 'h_skew', '_h_clock',
			'height', 'v_sync_start', 'v_sync_end', 'v_total', '_refresh'
		)
		class Flags(IntFlag):
			HSyncPositive = 1
			HSyncNegative = 2
			VSyncPositive = 4
			VSyncNegative = 8
			Interlace = 16
			DoubleScan = 32
			CSync = 64
			CSyncPositive = 128
			CSyncNegative = 256
		@property
		def h_clock(self):
			if self._h_clock is not None:
				return self._h_clock
			if self.dotclock is None or self.hTotal is None:
				return None
			if self.h_total == 0:
				return 0
			return self.dotclock / self.h_total
		@h_clock.setter
		def h_clock_setter(self, val):
			self._h_clock = val
		@property
		def refresh(self):
			if self._refresh is not None:
				return self._refresh
			if self.dotclock is None or self.h_total is None or self.v_total is None:
				return None
			if self.h_total == 0:
				return 0
			v_total = self.v_total
			if self.flags is not None:
				if self.flags & XRandROutput.Mode.Flags.DoubleScan:
					v_total *= 2
				if self.flags & XRandROutput.Mode.Flags.Interlace:
					v_total /= 2
			if v_total == 0:
				return 0
			return self.dotclock / (self.h_total * v_total)
		@refresh.setter
		def refresh_setter(self, val):
			self._refresh = val
		def __init__(
			self,
			name=None,
			id=None,
			dotclock=None,
			flags=None,
			current=False,
			preferred=False,
			width=None, h_sync_start=None, h_sync_end=None, h_total=None, h_skew=None, h_clock=None,
			height=None, v_sync_start=None, v_sync_end=None, v_total=None, refresh=None
		):
			self.name = name
			self.id = id
			self.dotclock = dotclock
			self.flags = flags
			self.current = current
			self.preferred = preferred
			self.width = width
			self.h_sync_start = h_sync_start
			self.h_sync_end = h_sync_end
			self.h_total = h_total
			self.h_skew = h_skew
			self._h_clock = h_clock
			self.height = height
			self.v_sync_start = v_sync_start
			self.v_sync_end = v_sync_end
			self.v_total = v_total
			self._refresh = refresh
	def __init__(
		self,
		name,
		connection=None,
		primary=None,
		geometry=None,
		mode=None,
		rotation=None,
		reflection=None,
		supported_rotations=None,
		supported_reflections=None,
		dimensions_mm = None,
		panning=None,
		tracking=None,
		border=None,
		properties=None,
		modes=None
	):
		self.name = name
		self.connection = connection
		self.primary = primary
		self.geometry = geometry
		self.mode = mode
		self.rotation = rotation
		self.reflection = reflection
		self.supported_rotations = supported_rotations
		self.supported_reflections = supported_reflections
		self.dimensions_mm = dimensions_mm
		self.panning = panning
		self.tracking = tracking
		self.border = border
		self.properties = properties
		self.modes = modes

class XRandROutputProperties:
	__slots__ = (
		'identifier',
		'timestamp',
		'subpixel_order',
		'gamma',
		'brightness',
		'clones',
		'crtc',
		'crtcs',
		'panning',
		'tracking',
		'border',
		'transform',
		'edid',
		'guid',
		'other'
	)
	class SubpixelOrder(IntEnum):
		HorizontalRGB = auto()
		HorizontalBGR = auto()
		VerticalRGB = auto()
		VerticalBGR = auto()
		NoSubpixels = auto()
	class Gamma():
		__slots__ = ('red', 'green', 'blue')
		def __init__(self, red=0, green=0, blue=0):
			self.red = red
			self.green = green
			self.blue = blue
	class OtherProperty():
		__slots__ = ('name', 'value', 'range', 'supported')
		def __init__(self, name, value=None, range=None, supported=None):
			self.name = name
			self.value = value
			self.range = range
			self.supported = supported
	def __init__(
		self,
		identifier=None,
		timestamp=None,
		subpixel_order=None,
		gamma=None,
		brightness=None,
		clones=None,
		crtc=None,
		crtcs=None,
		panning=None,
		tracking=None,
		border=None,
		transform=None,
		edid=None,
		guid=None,
		other=None
	):
		self.identifier = identifier
		self.timestamp = timestamp
		self.subpixel_order = subpixel_order
		self.gamma = gamma
		self.brightness = brightness
		self.clones = clones
		self.crtc = crtc
		self.crtcs = crtcs
		self.panning = panning
		self.tracking = tracking
		self.border = border
		self.transform = transform
		self.edid = edid
		self.guid = guid
		self.other = other

# Mappings

def reverse_mapping(mapping):
	return { v: k for k, v in mapping.items() }

text_to_rotation = {
	'normal': XRandROutput.Rotation.Rotate_0,
	'left': XRandROutput.Rotation.Rotate_90,
	'inverted': XRandROutput.Rotation.Rotate_180,
	'right': XRandROutput.Rotation.Rotate_270,
	'invalid rotation': None
}
rotation_to_text = reverse_mapping(text_to_rotation)

text_to_reflection = {
	'none': XRandROutput.Reflection(0),
	'X axis': XRandROutput.Reflection.Reflect_X,
	'Y axis': XRandROutput.Reflection.Reflect_Y,
	'X and Y axis': XRandROutput.Reflection.Reflect_X | XRandROutput.Reflection.Reflect_Y,
	'invalid reflection': None
}
reflection_to_text = reverse_mapping(text_to_reflection)

text_to_supported_reflection = {
	'x axis': XRandROutput.Reflection.Reflect_X,
	'y axis': XRandROutput.Reflection.Reflect_Y
}
supported_reflection_to_text = reverse_mapping(text_to_supported_reflection)

text_to_subpixel_order = {
	'horizontal rgb': XRandROutputProperties.SubpixelOrder.HorizontalRGB,
	'horizontal bgr': XRandROutputProperties.SubpixelOrder.HorizontalBGR,
	'vertical rgb': XRandROutputProperties.SubpixelOrder.VerticalRGB,
	'vertical bgr': XRandROutputProperties.SubpixelOrder.VerticalBGR,
	'no subpixels': XRandROutputProperties.SubpixelOrder.NoSubpixels,
	'unknown': None
}
subpixel_order_to_text = reverse_mapping(text_to_subpixel_order)

text_to_flag = {
	'+HSync': XRandROutput.Mode.Flags.HSyncPositive,
	'-HSync': XRandROutput.Mode.Flags.HSyncNegative,
	'+VSync': XRandROutput.Mode.Flags.VSyncPositive,
	'-VSync': XRandROutput.Mode.Flags.VSyncNegative,
	'Interlace': XRandROutput.Mode.Flags.Interlace,
	'DoubleScan': XRandROutput.Mode.Flags.DoubleScan,
	'CSync': XRandROutput.Mode.Flags.CSync,
	'+CSync': XRandROutput.Mode.Flags.CSyncPositive,
	'-CSync': XRandROutput.Mode.Flags.CSyncNegative
}
flag_to_text = reverse_mapping(text_to_flag)

# Parsing regexes and functions

screen_regex = compile(r'Screen\s*(?P<screen_number>\d+):\s*')
def screen_func(s, pos, screens, match):
	screen = XRandRScreen(int(match.group('screen_number')))
	
	pos = match.end()
	s, pos, screen.dimensions, matches = parse(
		s,
		pos,
		XRandRScreenDimensionsList(),
		((screen_dimensions_regex, screen_dimensions_func),)
	)
	s, pos, screen.outputs, matches = parse(
		s,
		pos,
		{},
		((output_regex, output_func),)
	)
	
	screens[screen.number] = screen
	return s, pos, screens, ParserAction.Again

screen_dimensions_regex = compile(
	r'''
	(?P<type>minimum|current|maximum)
	\s+(?P<width>\d+)\s*x\s*(?P<height>\d+)
	\s*(?:,\s*)?
	''',
	VERBOSE | MULTILINE
)
def screen_dimensions_func(s, pos, dimensions_list, match):
	dim = XRandRDimensions(
		int(match.group('width')),
		int(match.group('height'))
	)
	type = match.group('type')
	if type == 'minimum':
		dimensions_list.minimum = dim
	elif type == 'current':
		dimensions_list.current = dim
	else:
		assert type == 'maximum'
		dimensions_list.maximum = dim
	
	return s, match.end(), dimensions_list, ParserAction.Again

output_regex = compile(
	r'''
	(?P<name>\S+)
	\s+(?P<connection>connected|disconnected|unknown connection)
	(?:\s+(?P<primary>primary))?
	(?:
		\s+(?P<geometry>
			(?P<width>\d+)x(?P<height>\d+)
			\+(?P<x>\d+)\+(?P<y>\d+)
		)
		(?:\s+\((?P<mode>0x[0-9A-Fa-f]+)\))?
		(?:
			\s+(?P<rotation>normal|left|inverted|right|invalid rotation)
			(?:\s+(?P<reflection>none|X axis|Y axis|X and Y axis|invalid reflection))?
		)?
	)?\s*
	''',
	VERBOSE | MULTILINE
)
def output_func(s, pos, outputs, match):
	output = XRandROutput(match.group('name'))
	
	if match.group('connection') == 'connected':
		output.connection = XRandROutput.Connection.Connected
	elif match.group('connection') == 'disconnected':
		output.connection = XRandROutput.Connection.Disconnected
	else:
		assert match.group('connection') == 'unknown connection'
		output.connection = None
	
	output.primary = bool(match.group('primary'))
	
	if match.group('geometry'):
		output.geometry = XRandRGeometry(
			XRandRDimensions(
				int(match.group('width')),
				int(match.group('height'))
			),
			XRandROffset(
				int(match.group('x')),
				int(match.group('y'))
			)
		)
	
	if match.group('mode'):
		output.mode = int(match.group('mode'), 16)
	
	if match.group('rotation'):
		output.rotation = text_to_rotation[match.group('rotation')]
	else:
		output.rotation = XRandROutput.Rotation.Rotate_0
	if match.group('reflection'):
		output.reflection = text_to_reflection[match.group('reflection')]
	else:
		output.reflection = XRandROutput.Reflection(0)
	
	pos = match.end()
	if len(s) > pos and s[pos] == '(':
		pos += 1
		
		s, pos, output.supported_rotations, matches = parse(
			s,
			pos,
			[],
			((output_supported_rotation_regex, output_supported_rotation_func),)
		)
		
		s, pos, output.supported_reflections, matches = parse(
			s,
			pos,
			[],
			((output_supported_reflection_regex, output_supported_reflection_func),)
		)
	
	s, pos, output, matches = parse(
		s,
		pos,
		output,
		((output_regex2, output_func2),)
	)
	
	s, pos, output.properties, matches = parse(
		s,
		pos,
		XRandROutputProperties(),
		output_property_parser_list
	)
	
	s, pos, output.modes, matches = parse(
		s,
		pos,
		[],
		(
			(output_mode_nonverbose_regex, output_mode_nonverbose_func),
			(output_mode_verbose_regex, output_mode_verbose_func)
		)
	)
	
	outputs[output.name] = output
	return s, pos, outputs, ParserAction.Again

output_supported_rotation_regex = compile(r'(?P<supported_rotation>normal|left|inverted|right)\s*(?:\s|(?P<end>\)\s*))')
def output_supported_rotation_func(s, pos, supported_rotations, match):
	supported_rotations.append(
		text_to_rotation[match.group('supported_rotation')]
	)
	_action = ParserAction.Again
	if match.group('end'):
		_action = ParserAction.Stop
	return s, match.end(), supported_rotations, _action

output_supported_reflection_regex = compile(r'(?P<supported_reflection>x axis|y axis)\s*(?:\s|(?P<end>\)\s*))')
def output_supported_reflection_func(s, pos, supported_reflections, match):
	supported_reflections.append(
		text_to_supported_reflection[match.group('supported_reflection')]
	)
	_action = ParserAction.Again
	if match.group('end'):
		_action = ParserAction.Stop
	return s, match.end(), supported_reflections, _action

output_regex2 = compile(
	r'''
	(?P<width_mm>\d+)mm\s*x\s*(?P<height_mm>\d+)mm
	(?P<panning>
		\s+panning\s+
		(?P<pan_width>\d+)x(?P<pan_height>\d+)
		\+(?P<pan_left>\d+)\+(?P<pan_top>\d+)
	)?
	(?P<tracking>
		\s+tracking\s+
		(?P<track_width>\d+)x(?P<track_height>\d+)
		\+(?P<track_left>\d+)\+(?P<track_top>\d+)
	)?
	(?P<border>
		\s+border\s+
		(?P<border_left>\d+)/(?P<border_top>\d+)
		/(?P<border_right>\d+)/(?P<border_bottom>\d+)
	)?\s*
	''',
	VERBOSE | MULTILINE
)
def output_func2(s, pos, output, match):
	output.dimensions_mm = XRandRDimensions(
		int(match.group('width_mm')),
		int(match.group('height_mm'))
	)
	if match.group('panning'):
		output.panning = XRandRGeometry(
			XRandRDimensions(
				int(match.group('pan_width')),
				int(match.group('pan_height'))
			),
			XRandROffset(
				int(match.group('pan_left')),
				int(match.group('pan_top'))
			)
		)
	if match.group('tracking'):
		output.tracking = XRandRGeometry(
			XRandRDimensions(
				int(match.group('track_width')),
				int(match.group('track_height'))
			),
			XRandROffset(
				int(match.group('track_left')),
				int(match.group('track_top'))
			)
		)
	if match.group('border'):
		output.border = XRandRBorder(
			int(match.group('border_left')),
			int(match.group('border_top')),
			int(match.group('border_right')),
			int(match.group('border_bottom'))
		)
	return s, match.end(), output, ParserAction.Stop

output_property_identifier_regex = compile(r'(?<=^\t)Identifier:\s*(?P<identifier>0x[0-9A-Fa-f]+)\s*', MULTILINE)
def output_property_identifier_func(s, pos, output_properties, match):
	output_properties.identifier = int(match.group('identifier'), 16)
	return s, match.end(), output_properties, ParserAction.Continue

output_property_timestamp_regex = compile(r'(?<=^\t)Timestamp:\s*(?P<timestamp>\d+)\s*', MULTILINE)
def output_property_timestamp_func(s, pos, output_properties, match):
	output_properties.timestamp = int(match.group('timestamp'))
	return s, match.end(), output_properties, ParserAction.Continue

output_property_subpixel_order_regex = compile(
	r'''
	(?<=^\t)Subpixel:\s*
	(?P<subpixel_order>
		unknown
		|(?:horizontal|vertical)\ (?:rgb|bgr)
		|no\ subpixels
	)\s*
	''',
	VERBOSE | MULTILINE
)
def output_property_subpixel_order_func(s, pos, output_properties, match):
	output_properties.subpixel_order = text_to_subpixel_order[match.group('subpixel_order')]
	return s, match.end(), output_properties, ParserAction.Continue

output_property_gamma_regex = compile(
	r'''
	(?<=^\t)Gamma:\s*
	(?P<gamma_red>\d+(?:\.\d+)(?:e+\d+))
	:(?P<gamma_green>\d+(?:\.\d+)(?:e+\d+))
	:(?P<gamma_blue>\d+(?:\.\d+)(?:e+\d+))
	\s*
	''',
	VERBOSE | MULTILINE
)
def output_property_gamma_func(s, pos, output_properties, match):
	output_properties.gamma = XRandROutputProperties.Gamma(
		float(match.group('gamma_red')),
		float(match.group('gamma_green')),
		float(match.group('gamma_blue'))
	)
	return s, match.end(), output_properties, ParserAction.Continue

output_property_brightness_regex = compile(
	r'''
	(?<=^\t)Brightness:\s*
	(?P<brightness>\d+(?:\.\d+)(?:e+\d+))
	\s*
	''',
	VERBOSE | MULTILINE
)
def output_property_brightness_func(s, pos, output_properties, match):
	output_properties.brightness = float(match.group('brightness'))
	return s, match.end(), output_properties, ParserAction.Continue

output_property_clones_regex = compile(r'(?<=^\t)Clones:[^\S\n]*(?P<clones>(?:\S+[^\S\n]*)*)\s*', MULTILINE)
def output_property_clones_func(s, pos, output_properties, match):
	output_properties.clones = match.group('clones').split()
	return s, match.end(), output_properties, ParserAction.Continue

output_property_crtc_regex = compile(r'(?<=^\t)CRTC:\s*(?P<crtc>\d+)\s*', MULTILINE)
def output_property_crtc_func(s, pos, output_properties, match):
	output_properties.crtc = int(match.group('crtc'))
	return s, match.end(), output_properties, ParserAction.Continue

output_property_crtcs_regex = compile(r'(?<=^\t)CRTCs:\s*(?P<crtcs>(?:\d+(?:$|\s+))+)\s*', MULTILINE)
def output_property_crtcs_func(s, pos, output_properties, match):
	output_properties.crtcs = tuple(int(crtc) for crtc in match.group('crtcs').split())
	return s, match.end(), output_properties, ParserAction.Continue

output_property_panning_regex = compile(
	r'''
	(?<=^\t)Panning:\s*
	(?P<pan_width>\d+)x(?P<pan_height>\d+)
	\+(?P<pan_left>\d+)\+(?P<pan_top>\d+)
	\s*
	''',
	VERBOSE | MULTILINE
)
def output_property_panning_func(s, pos, output_properties, match):
	output_properties.panning = XRandRGeometry(
		XRandRDimensions(
			int(match.group('pan_width')),
			int(match.group('pan_height'))
		),
		XRandROffset(
			int(match.group('pan_left')),
			int(match.group('pan_top'))
		)
	)
	return s, match.end(), output_properties, ParserAction.Continue

output_property_tracking_regex = compile(
	r'''
	(?<=^\t)Tracking:\s*
	(?P<track_width>\d+)x(?P<track_height>\d+)
	\+(?P<track_left>\d+)\+(?P<track_top>\d+)
	\s*
	''',
	VERBOSE | MULTILINE
)
def output_property_tracking_func(s, pos, output_properties, match):
	output_properties.tracking = XRandRGeometry(
		XRandRDimensions(
			int(match.group('track_width')),
			int(match.group('track_height'))
		),
		XRandROffset(
			int(match.group('track_left')),
			int(match.group('track_top'))
		)
	)
	return s, match.end(), output_properties, ParserAction.Continue

output_property_border_regex = compile(
	r'''
	(?<=^\t)Border:\s*
	(?P<border_left>\d+)/(?P<border_top>\d+)
	/(?P<border_right>\d+)/(?P<border_bottom>\d+)
	\s*
	''',
	VERBOSE | MULTILINE
)
def output_property_border_func(s, pos, output_properties, match):
	output_properties.border = XRandRBorder(
		int(match.group('border_left')),
		int(match.group('border_top')),
		int(match.group('border_right')),
		int(match.group('border_bottom'))
	)
	return s, match.end(), output_properties, ParserAction.Continue

output_property_transform_regex = compile(
	r'''
	(?<=^\t)Transform:\s*
	(?P<matrix>
		(?:\d*(?:\.\d*)\s+){8}
		\d*(?:\.\d*)
	)\s*
	(?:
		filter:[^\S\n]*
		(?P<filter>.*)
		\s*
	)?
	''',
	VERBOSE | MULTILINE
)
def output_property_transform_func(s, pos, output_properties, match):
	output_properties.transform = XRandRTransform(
		*tuple(float(v) for v in match.group('matrix').split()),
		match.group('filter') or None
	)
	return s, match.end(), output_properties, ParserAction.Continue

output_property_edid_regex = compile(
	r'''
	(?<=^\t)EDID:\s*
	(?P<edid>
		(?:(?:[0-9A-Fa-f][0-9A-Fa-f]){16}\s*)*
		(?:[0-9A-Fa-f][0-9A-Fa-f])*
	)\s*
	''',
	VERBOSE | MULTILINE
)
def output_property_edid_func(s, pos, output_properties, match):
	output_properties.edid = bytes.fromhex(match.group('edid'))
	return s, match.end(), output_properties, ParserAction.Continue

output_property_guid_regex = compile(
	r'''
	(?<=^\t)GUID:\s*
	(?P<guid>
		\{
		(?:[0-9A-Fa-f][0-9A-Fa-f]){4}
		-
		(?:[0-9A-Fa-f][0-9A-Fa-f]){2}
		-
		(?:[0-9A-Fa-f][0-9A-Fa-f]){2}
		-
		(?:[0-9A-Fa-f][0-9A-Fa-f]){2}
		-
		(?:[0-9A-Fa-f][0-9A-Fa-f]){6}
		\}
	)\s*
	''',
	VERBOSE | MULTILINE
)
def output_property_guid_func(s, pos, output_properties, match):
	output_properties.edid = bytes.fromhex(match.group('guid')[1:-1].replace('-', ''))
	return s, match.end(), output_properties, ParserAction.Continue

output_property_other_regex = compile(
	r'''
	(?<=^\t)(?P<name>[^:]+):[^\S\n]*(?P<value>.*)\s*
	(?:(?P<range>range:)|(?P<supported>supported:))?
	''',
	VERBOSE | MULTILINE
)
def output_property_other_func(s, pos, output_properties, match):
	if output_properties.other is None:
		output_properties.other = {}
	output_property = XRandROutputProperties.OtherProperty(match.group('name'), match.group('value'))
	if output_property.value[-1] == ' ':
		output_property.value = output_property.value[:-1]
	
	regex = None
	if match.group('range'):
		regex = (output_property_other_range_regex, output_property_other_range_func)
	if match.group('supported'):
		assert regex is None
		regex = (output_property_other_supported_regex, output_property_other_supported_func)
	
	pos = match.end()
	if regex is not None:
		s, pos, obj, matches = parse(
			s,
			pos,
			output_property,
			(regex,)
		)
	
	output_properties.other[output_property.name] = output_property
	return s, pos

output_property_other_range_regex = compile(r' \((?P<start_val>[^,]+), (?P<end_val>[^)]+)\)(?:,|(?P<end>$\s*))', MULTILINE)
def output_property_other_range_func(s, pos, output_property, match):
	if output_property.range is None:
		output_property.range = []
	output_property.range.append((match.group('start_val'), match.group('end_val')))
	return s, match.end(), output_property, ParserAction.Stop if match.group('end') else ParserAction.Again

output_property_other_supported_regex = compile(r' (?P<value>[^\n,]+)(?:,|(?P<end>$\s*))', MULTILINE)
def output_property_other_supported_func(s, pos, output_property, match):
	if output_property.supported is None:
		output_property.supported = []
	output_property.supported.append(match.group('value'))
	return s, match.end(), output_property, ParserAction.Stop if match.group('end') else ParserAction.Again

output_property_parser_list = (
	(output_property_identifier_regex, output_property_identifier_func),
	(output_property_timestamp_regex, output_property_timestamp_func),
	(output_property_subpixel_order_regex, output_property_subpixel_order_func),
	(output_property_gamma_regex, output_property_gamma_func),
	(output_property_brightness_regex, output_property_brightness_func),
	(output_property_clones_regex, output_property_clones_func),
	(output_property_crtc_regex, output_property_crtc_func),
	(output_property_crtcs_regex, output_property_crtcs_func),
	(output_property_panning_regex, output_property_panning_func),
	(output_property_tracking_regex, output_property_tracking_func),
	(output_property_border_regex, output_property_border_func),
	(output_property_transform_regex, output_property_transform_func),
	(output_property_edid_regex, output_property_edid_func),
	(output_property_guid_regex, output_property_guid_func),
	(output_property_other_regex, output_property_other_func)
)

output_mode_nonverbose_regex = compile(
	r'''
	(?<=^\ {3})(?P<name>(?P<width>\d+)x(?P<height>\d+))[^\S\n]+
	''',
	VERBOSE | MULTILINE
)
output_mode_nonverbose_clock_regex = compile(
	r'''
	(?P<clock>\d*\.\d*)
	(?P<current>\*|\ )
	(?P<preferred>\+|\ )
	\s*
	''',
	VERBOSE | MULTILINE
)
def output_mode_nonverbose_func(s, pos, modes, match):
	name = match.group('name')
	width = int(match.group('width'))
	height = int(match.group('height'))
	
	pos = match.end()
	while True:
		match = output_mode_nonverbose_clock_regex.match(s, pos=pos)
		if not match:
			break
		
		mode = XRandROutput.Mode(
			name=name,
			current=(match.group('current') == '*'),
			preferred=(match.group('preferred') == '+'),
			width=width,
			height=height
		)
		
		modes.append(mode)
		pos = match.end()
	
	return s, pos, modes, ParserAction.Again

output_mode_verbose_regex = compile(
	r'''
	(?<=^\ {2})(?P<name>\S+)\s+
	\((?P<id>0x[0-9A-Fa-f]+)\)\s+
	(?P<dotclock>\d*\.\d*)MHz
	(?P<flags>(?:\s+''' + r')?(?:\s+'.join(escape(flag) for flag in text_to_flag.keys()) + r''')?)
	(?P<current>\s+\*current)?
	(?P<preferred>\s+\+preferred)?
	[^\S\n]*
	
	\n\ {8}h:\s*
	width\s+(?P<width>\d+)\s+
	start\s+(?P<h_sync_start>\d+)\s+
	end\s+(?P<h_sync_end>\d+)\s+
	total\s+(?P<h_total>\d+)\s+
	skew\s+(?P<h_skew>\d+)\s+
	clock\s+(?P<h_clock>\d*\.\d*)KHz
	[^\S\n]*
	
	\n\ {8}v:\s*
	height\s+(?P<height>\d+)\s+
	start\s+(?P<v_sync_start>\d+)\s+
	end\s+(?P<v_sync_end>\d+)\s+
	total\s+(?P<v_total>\d+)\s+
	clock\s+(?P<refresh>\d*\.\d*)Hz
	\s*
	''',
	VERBOSE | MULTILINE
)
def output_mode_verbose_func(s, pos, modes, match):
	mode = XRandROutput.Mode(
		name=match.group('name'),
		id=int(match.group('id'), 16),
		dotclock=float(match.group('dotclock')) * 1000000,
		current=bool(match.group('current')),
		preferred=bool(match.group('preferred')),
		
		width=int(match.group('width')),
		h_sync_start=int(match.group('h_sync_start')),
		h_sync_end=int(match.group('h_sync_end')),
		h_total=int(match.group('h_total')),
		h_skew=int(match.group('h_skew')),
		h_clock=float(match.group('h_clock')) * 1000,
		
		height=int(match.group('height')),
		v_sync_start=int(match.group('v_sync_start')),
		v_sync_end=int(match.group('v_sync_end')),
		v_total=int(match.group('v_total')),
		refresh=float(match.group('refresh'))
	)
	
	mode.flags = XRandROutput.Mode.Flags(0)
	for flag in match.group('flags').split():
		mode.flags |= text_to_flag[flag]
	
	modes.append(mode)
	return s, match.end(), modes, ParserAction.Again

# Parser

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

# Parsing helpers

def parse_xrandr_screens(xrandr_output, start=0):
	xrandr_output, start, screens, matches = parse(
		xrandr_output,
		start,
		{},
		((screen_regex, screen_func),)
	)
	success = start == len(xrandr_output)
	return screens, success

def parse_xrandr():
	xrandr_path = which('xrandr')
	if not xrandr_path:
		raise FileNotFoundError('xrandr not found')
	
	with Popen(('xrandr', '--verbose'), executable=xrandr_path, stdout=PIPE, universal_newlines=True) as popen:
		xrandr_output = popen.stdout.read()
	
	return parse_xrandr_screens(xrandr_output)
