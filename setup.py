import os
from enum import Flag, auto

from .classes import *
from .mappings import *

__all__ = (
	'XRandRSetupOptions',
	'setup_screens',
	'setup_outputs'
)

class XRandRSetupOptions(Flag):
	SetupNone = 0
	
	SetupScreenDimensions = auto()
	SetupScreenPrimaryOutput = auto()
	SetupScreens = \
		SetupScreenDimensions |\
		SetupScreenPrimaryOutput
	
	SetupOutputPosition = auto()
	SetupOutputMode = auto()
	SetupOutputRotation = auto()
	SetupOutputReflection = auto()
	SetupOutputPanning = auto()
	SetupOutputTracking = auto()
	SetupOutputBorder = auto()
	SetupOutputsBasic = \
		SetupOutputPosition |\
		SetupOutputMode |\
		SetupOutputRotation |\
		SetupOutputReflection |\
		SetupOutputPanning |\
		SetupOutputTracking |\
		SetupOutputBorder
	
	SetupOutputProperties = auto()
	SetupUnknownOutputProperties = auto()
	SetupOutputsAll = \
		SetupOutputsBasic |\
		SetupOutputProperties |\
		SetupUnknownOutputProperties
	
	SetupAll = ~SetupNone

def setup_screens(screens, setup_options=XRandRSetupOptions.SetupAll):
	if not setup_options & XRandRSetupOptions.SetupAll:
		return
	
	args = _setup_screens_args(screens, setup_options)
	if args:
		os.spawnlp(os.P_WAIT, 'xrandr', 'xrandr', *args)
	
	if setup_options & XRandRSetupOptions.SetupUnknownOutputProperties:
		for screen in screens.values():
			if screen.outputs:
				for output in screen.outputs.values():
					_setup_output_unknown_properties(screen.number, output.name, output.properties.other, setup_options)

def setup_outputs(screen_nr, outputs, setup_options=XRandRSetupOptions.SetupAll):
	if not setup_options & XRandRSetupOptions.SetupOutputAll:
		return
	
	args = _setup_outputs_args(outputs, setup_options)
	if args:
		os.spawnlp(os.P_WAIT, 'xrandr', 'xrandr', '--screen', str(screen_nr), *args)
	
	if setup_options & XRandRSetupOptions.SetupUnknownOutputProperties:
		for output in outputs.values():
			_setup_output_unknown_properties(screen_nr, output.name, output.properties.other, setup_options)

def _setup_screens_args(screens, setup_options):
	if not setup_options & XRandRSetupOptions.SetupScreens:
		return
	
	args = []
	
	for screen in screens.values():
		_args = []
		
		if (setup_options & XRandRSetupOptions.SetupScreenDimensions
			and screen.dimensions
			and screen.dimensions.current
			and screen.dimensions.current.width is not None
			and screen.dimensions.current.height is not None):
			_args.extend((
				'--fb',
				'{!s}x{!s}'.format(
					screen.dimensions.current.width,
					screen.dimensions.current.height
				)
			))
		if (setup_options & XRandRSetupOptions.SetupScreenPrimaryOutput
			and screen.outputs):
			has_primary = False
			for output in screen.outputs.values():
				if output and output.primary:
					has_primary = True
			if not has_primary:
				_args.append('--noprimary')
		
		_args.extend(_setup_outputs_args(screen.outputs, setup_options) or ())
		if _args:
			args.extend(('--screen', str(screen.number)))
			args.extend(_args)
	
	return args

def _setup_outputs_args(outputs, setup_options):
	if not setup_options & (XRandRSetupOptions.SetupOutputsAll & ~XRandRSetupOptions.SetupUnknownOutputProperties):
		return
	
	args = []
	
	for output in outputs.values():
		if not output:
			continue
		
		_args = []
		
		if setup_options & XRandRSetupOptions.SetupScreenPrimaryOutput and output.primary:
			_args.append('--primary')
		
		if setup_options & XRandRSetupOptions.SetupOutputMode:
			mode = None
			rate = None
			
			for _mode in output.modes:
				if _mode.current:
					if _mode.width and _mode.height:
						rate = _mode.refresh
						mode = '{!s}x{!s}'.format(
							_mode.width,
							_mode.height
						)
					elif _mode.id:
						mode = format(_mode.id, '#x')
					else:
						continue
					break
			
			if not mode:
				if output.mode:
					mode = format(output.mode, '#x')
				elif (output.geometry
					and output.geometry.dimensions
					and output.geometry.dimensions.width is not None
					and output.geometry.dimensions.height is not None):
					mode = '{!s}x{!s}'.format(
						output.geometry.dimensions.width,
						output.geometry.dimensions.height
					)
			
			if rate:
				_args.extend(('--rate', str(rate)))
			if mode:
				_args.extend(('--mode', mode))
			#else:
			#	_args.append('--off')
			
			if (output.geometry
				and output.geometry.offset
				and output.geometry.offset.x is not None
				and output.geometry.offset.y is not None):
				_args.extend((
					'--pos',
					'{!s}x{!s}'.format(
						output.geometry.offset.x,
						output.geometry.offset.y
					)
				))
		
		if (setup_options & XRandRSetupOptions.SetupOutputRotation
			and output.rotation is not None):
			_args.extend((
				'--rotate',
				rotation_to_text[output.rotation]
			))
		if (setup_options & XRandRSetupOptions.SetupOutputReflection
			and output.reflection is not None):
			_args.extend((
				'--reflect',
				reflection_to_text[output.reflection]
			))
		
		if setup_options & XRandRSetupOptions.SetupOutputPanning:
			_panning = _merge_geometry_objects(
				output.panning,
				output.properties.panning
			)
			if (_panning
				and _panning.dimensions
				and _panning.dimensions.width is not None
				and _panning.dimensions.height is not None):
				_panning_arg = '{!s}x{!s}'.format(
					_panning.dimensions.width,
					_panning.dimensions.height
				)
				if (_panning.offset
					and _panning.offset.x is not None
					and _panning.offset.y is not None):
					_panning_arg += '+{!s}+{!s}'.format(
						_panning.offset.x,
						_panning.offset.y
					)
				if setup_options & XRandRSetupOptions.SetupOutputTracking:
					_tracking = _merge_geometry_objects(
						output.tracking,
						output.properties.tracking
					)
					if (_tracking
						and _tracking.dimensions
						and _tracking.dimensions.width is not None
						and _tracking.dimensions.height is not None
						and _tracking.offset
						and _tracking.offset.x is not None
						and _tracking.offset.y is not None):
						_panning_arg += '/{!s}x{!s}+{!s}+{!s}'.format(
							_tracking.dimensions.width,
							_tracking.dimensions.height,
							_tracking.offset.x,
							_tracking.offset.y
						)
						if setup_options & XRandRSetupOptions.SetupOutputBorder:
							_border = _merge_border_objects(
								output.border,
								output.properties.border
							)
							if (_border
								and _border.left is not None
								and _border.top is not None
								and _border.right is not None
								and _border.bottom is not None):
								_panning_arg += '/{!s}/{!s}/{!s}/{!s}'.format(
									_border.left,
									_border.top,
									_border.right,
									_border.bottom
								)
				_args.extend(('--panning', _panning_arg))
		
		if setup_options & XRandRSetupOptions.SetupOutputProperties:
			_args.extend(_setup_output_properties_args(output.properties, setup_options) or ())
		if _args:
			args.extend(('--output', output.name))
			args.extend(_args)
	
	return args

def _merge_geometry_objects(a, b):
	if a is None:
		return b
	elif b is None:
		return a
	
	ret = XRandRGeometry()
	
	if a.dimensions or b.dimensions:
		ret.dimensions = XRandRDimensions(
			a.dimensions.width if a.dimensions.width is not None else b.dimensions.width,
			a.dimensions.height if a.dimensions.height is not None else b.dimensions.height
		)
	if a.offset or b.offset:
		ret.offset = XRandROffset(
			a.offset.x if a.offset.x is not None else b.offset.x,
			a.offset.y if a.offset.y is not None else b.offset.y
		)
	
	return ret

def _merge_border_objects(a, b):
	if a is None:
		return b
	elif b is None:
		return a
	
	return XRandRBorder(
		a.left if a.left is not None else b.left,
		a.top if a.top is not None else b.top,
		a.right if a.right is not None else b.right,
		a.bottom if a.bottom is not None else b.bottom
	)

def _setup_output_properties_args(properties, setup_options):
	if not setup_options & ~XRandRSetupOptions.SetupOutputProperties:
		return
	
	args = []
	
	if (properties.gamma
		and properties.gamma.red is not None
		and properties.gamma.green is not None
		and properties.gamma.blue is not None):
		args.extend((
			'--gamma',
			'{!s}:{!s}:{!s}'.format(
				properties.gamma.red,
				properties.gamma.green,
				properties.gamma.blue
			)
		))
	
	if properties.brightness is not None:
		args.extend(('--brightness', str(properties.brightness)))
	
	# TODO: How do I implement properties.clones?
	
	if properties.crtc is not None:
		args.extend(('--crtc', str(properties.crtc)))
	
	if (properties.transform
		and properties.transform.a is not None
		and properties.transform.b is not None
		and properties.transform.c is not None
		and properties.transform.d is not None
		and properties.transform.e is not None
		and properties.transform.f is not None
		and properties.transform.g is not None
		and properties.transform.h is not None
		and properties.transform.i is not None):
		args.extend((
			'--transform',
			'{!s},{!s},{!s},{!s},{!s},{!s},{!s},{!s},{!s}'.format(
				properties.transform.a,
				properties.transform.b,
				properties.transform.c,
				properties.transform.d,
				properties.transform.e,
				properties.transform.f,
				properties.transform.g,
				properties.transform.h,
				properties.transform.i
			)
		))
		if (properties.transform.filter
			and properties.transform.filter != 'bilinear'):
			args.extend(('--filter', str(properties.transform.filter)))
	
	if properties.guid:
		args.extend(('--set', 'GUID', _propval_to_str(properties.guid)))
	
	return args

def _setup_output_unknown_properties(screen_nr, output_name, properties, setup_options):
	if not setup_options & XRandRSetupOptions.SetupUnknownOutputProperties:
		return
	
	for property in properties.values():
		if property.name:
			os.spawnlp(
				os.P_WAIT,
				'xrandr',
				'xrandr',
				'--screen',
				str(screen_nr),
				'--output',
				str(output_name),
				'--set',
				str(property.name),
				_propval_to_str(property.value) if property.value is not None else ''
			)

def _propval_to_str(v):
	if isinstance(v, list) or isinstance(v, tuple) or isinstance(v, bytes):
		return ','.join(str(x) for x in v)
	return str(v)
