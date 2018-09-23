from re import compile, VERBOSE, MULTILINE, escape

from .classes import *
from .mappings import *
from .parser import *

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
	return s, match.end()

output_property_timestamp_regex = compile(r'(?<=^\t)Timestamp:\s*(?P<timestamp>\d+)\s*', MULTILINE)
def output_property_timestamp_func(s, pos, output_properties, match):
	output_properties.timestamp = int(match.group('timestamp'))
	return s, match.end()

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
	return s, match.end()

output_property_gamma_regex = compile(
	r'''
	(?<=^\t)Gamma:\s*
	(?P<gamma_red>\d*\.\d*(?:e\d+)?)
	:(?P<gamma_green>\d*\.\d*(?:e\d+)?)
	:(?P<gamma_blue>\d*\.\d*(?:e\d+)?)
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
	return s, match.end()

output_property_brightness_regex = compile(
	r'''
	(?<=^\t)Brightness:\s*
	(?P<brightness>\d*\.\d*(?:e\d+)?)
	\s*
	''',
	VERBOSE | MULTILINE
)
def output_property_brightness_func(s, pos, output_properties, match):
	output_properties.brightness = float(match.group('brightness'))
	return s, match.end()

output_property_clones_regex = compile(r'(?<=^\t)Clones:[^\S\n]*(?P<clones>(?:\S+[^\S\n]*)*)\s*', MULTILINE)
def output_property_clones_func(s, pos, output_properties, match):
	output_properties.clones = match.group('clones').split()
	return s, match.end()

output_property_crtc_regex = compile(r'(?<=^\t)CRTC:\s*(?P<crtc>\d+)\s*', MULTILINE)
def output_property_crtc_func(s, pos, output_properties, match):
	output_properties.crtc = int(match.group('crtc'))
	return s, match.end()

output_property_crtcs_regex = compile(r'(?<=^\t)CRTCs:\s*(?P<crtcs>(?:\d+(?:$|\s+))+)\s*', MULTILINE)
def output_property_crtcs_func(s, pos, output_properties, match):
	output_properties.crtcs = tuple(int(crtc) for crtc in match.group('crtcs').split())
	return s, match.end()

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
	return s, match.end()

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
	return s, match.end()

output_property_border_regex = compile(
	r'''
	(?<=^\t)Border:\s*
	(?P<border_left>\d+)\s+
	(?P<border_top>\d+)\s+
	(?P<border_right>\d+)\s+
	(?P<border_bottom>\d+)\s+
	range:.*
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
	return s, match.end()

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
	return s, match.end()

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
	return s, match.end()

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
	return s, match.end()

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

__all__ = [v for v in globals() if v.endswith(('_func', '_regex'))]
