# noqa: W191,W293,W503,E128
from enum import unique, IntEnum, IntFlag, auto
from typing import Optional, Mapping, Sequence, Union, Any, Tuple

__all__ = (
	'XRandRDimensions',
	'XRandROffset',
	'XRandRGeometry',
	'XRandRBorder',
	'XRandRTransform',
	'XRandRScreen',
	'XRandRScreenDimensionsList',
	'XRandROutput',
	'XRandROutputProperties'
)

Rational = Union[int, float]

# TODO: idea: make the XRandR types (like XRandRGeometry,
#     XRandRDimension, etc) generic (typing.Generic).


class XRandRDimensions:
	__slots__ = ('width', 'height')
	width: Optional[int]
	height: Optional[int]
	
	def __init__(
		self,
		width: Optional[int] = 0,
		heigth: Optional[int] = 0
	) -> None:
		self.width = width
		self.height = heigth


class XRandROffset:
	__slots__ = ('x', 'y')
	x: Optional[int]
	y: Optional[int]
	
	def __init__(
		self,
		x: Optional[int] = 0,
		y: Optional[int] = 0
	) -> None:
		self.x = x
		self.y = y


class XRandRGeometry:
	__slots__ = ('dimensions', 'offset')
	dimensions: Optional[XRandRDimensions]
	offset: Optional[XRandROffset]
	
	def __init__(
		self,
		dimensions: Optional[XRandRDimensions] = None,
		offset: Optional[XRandROffset] = None
	) -> None:
		self.dimensions = dimensions
		self.offset = offset


class XRandRBorder:
	__slots__ = ('left', 'top', 'right', 'bottom')
	left: Optional[int]
	top: Optional[int]
	right: Optional[int]
	bottom: Optional[int]
	
	def __init__(
		self,
		left: Optional[int] = 0,
		top: Optional[int] = 0,
		right: Optional[int] = 0,
		bottom: Optional[int] = 0
	) -> None:
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
	a: Optional[Rational]
	b: Optional[Rational]
	c: Optional[Rational]
	d: Optional[Rational]
	e: Optional[Rational]
	f: Optional[Rational]
	g: Optional[Rational]
	h: Optional[Rational]
	i: Optional[Rational]
	filter: Optional[str]
	
	def __init__(
		self,
		a: Optional[Rational] = 0,
		b: Optional[Rational] = 0,
		c: Optional[Rational] = 0,
		d: Optional[Rational] = 0,
		e: Optional[Rational] = 0,
		f: Optional[Rational] = 0,
		g: Optional[Rational] = 0,
		h: Optional[Rational] = 0,
		i: Optional[Rational] = 0,
		filter: Optional[str] = None
	) -> None:
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


class XRandRScreenDimensionsList:
	__slots__ = ('minimum', 'current', 'maximum')
	minimum: Optional[XRandRDimensions]
	current: Optional[XRandRDimensions]
	maximum: Optional[XRandRDimensions]
	
	def __init__(
		self,
		minimum: Optional[XRandRDimensions] = None,
		current: Optional[XRandRDimensions] = None,
		maximum: Optional[XRandRDimensions] = None
	) -> None:
		self.minimum = minimum
		self.current = current
		self.maximum = maximum


class XRandRScreen:
	__slots__ = ('number', 'dimensions', 'outputs')
	number: int
	dimensions: Optional[XRandRScreenDimensionsList]
	outputs: Optional[Mapping[str, 'XRandROutput']]
	
	def __init__(
		self,
		number: int,
		dimensions: Optional[XRandRScreenDimensionsList] = None,
		outputs: Optional[Mapping[str, 'XRandROutput']] = None
	) -> None:
		self.number = number
		self.dimensions = dimensions
		self.outputs = outputs


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
			
			'width',
			'h_sync_start',
			'h_sync_end',
			'h_total',
			'h_skew',
			'_h_clock',
			
			'height',
			'v_sync_start',
			'v_sync_end',
			'v_total',
			'_refresh'
		)
		_h_clock: Optional[Rational]
		_refresh: Optional[Rational]
		
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
		def h_clock(self) -> Optional[Rational]:
			if self._h_clock is not None:
				return self._h_clock
			if self.dotclock is None or self.h_total is None:
				return None
			if self.h_total == 0:
				return 0
			return self.dotclock / self.h_total
		
		@h_clock.setter
		def h_clock(self, val: Rational) -> None:
			self._h_clock = val
		
		@property
		def refresh(self) -> Optional[Rational]:
			if self._refresh is not None:
				return self._refresh
			if (self.dotclock is None
				or self.h_total is None
				or self.v_total is None):
				return None
			if self.h_total == 0:
				return 0
			v_total: Union[int, float] = self.v_total
			if self.flags is not None:
				if self.flags & XRandROutput.Mode.Flags.DoubleScan:
					v_total *= 2
				if self.flags & XRandROutput.Mode.Flags.Interlace:
					v_total /= 2
			if v_total == 0:
				return 0
			return self.dotclock / (self.h_total * v_total)
		
		@refresh.setter
		def refresh(self, val: Rational) -> None:
			self._refresh = val
		
		name: Optional[str]
		id: Optional[int]
		dotclock: Optional[Rational]
		flags: Optional[Flags]
		current: bool
		preferred: bool
		
		width: Optional[int]
		h_sync_start: Optional[int]
		h_sync_end: Optional[int]
		h_total: Optional[int]
		h_skew: Optional[int]
		
		height: Optional[int]
		v_sync_start: Optional[int]
		v_sync_end: Optional[int]
		v_total: Optional[int]
		
		def __init__(
			self,
			name: Optional[str] = None,
			id: Optional[int] = None,
			dotclock: Optional[Rational] = None,
			flags: Optional[Flags] = None,
			current: bool = False,
			preferred: bool = False,
			
			width: Optional[int] = None,
			h_sync_start: Optional[int] = None,
			h_sync_end: Optional[int] = None,
			h_total: Optional[int] = None,
			h_skew: Optional[int] = None,
			h_clock: Optional[Rational] = None,
			
			height: Optional[int] = None,
			v_sync_start: Optional[int] = None,
			v_sync_end: Optional[int] = None,
			v_total: Optional[int] = None,
			refresh: Optional[Rational] = None
		) -> None:
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
	
	name: str
	connection: Optional[Connection]
	primary: bool
	geometry: Optional[XRandRGeometry]
	mode: Optional[int]
	rotation: Optional[Rotation]
	reflection: Optional[Reflection]
	supported_rotations: Optional[Rotation]
	supported_reflections: Optional[Reflection]
	dimensions_mm: Optional[XRandRDimensions]
	panning: Optional[XRandRGeometry]
	tracking: Optional[XRandRGeometry]
	border: Optional[XRandRBorder]
	properties: Optional['XRandROutputProperties']
	modes: Optional[Sequence[Mode]]
	
	def __init__(
		self,
		name: str,
		connection: Optional[Connection] = None,
		primary: bool = False,
		geometry: Optional[XRandRGeometry] = None,
		mode: Optional[int] = None,
		rotation: Optional[Rotation] = None,
		reflection: Optional[Reflection] = None,
		supported_rotations: Optional[Rotation] = None,
		supported_reflections: Optional[Reflection] = None,
		dimensions_mm: Optional[XRandRDimensions] = None,
		panning: Optional[XRandRGeometry] = None,
		tracking: Optional[XRandRGeometry] = None,
		border: Optional[XRandRBorder] = None,
		properties: Optional['XRandROutputProperties'] = None,
		modes: Optional[Sequence[Mode]] = None
	) -> None:
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
		red: Rational
		green: Rational
		blue: Rational
		
		def __init__(
			self,
			red: Rational = 0,
			green: Rational = 0,
			blue: Rational = 0
		) -> None:
			self.red = red
			self.green = green
			self.blue = blue
	
	class OtherProperty():
		__slots__ = ('name', 'value', 'range', 'supported')
		name: str
		value: Any
		range: Optional[Sequence[Tuple[Any, Any]]]
		supported: Optional[Sequence[Any]]
		
		def __init__(
			self,
			name: str,
			value: Any = None,
			range: Optional[Sequence[Tuple[Any, Any]]] = None,
			supported: Optional[Sequence[Any]] = None
		) -> None:
			self.name = name
			self.value = value
			self.range = range
			self.supported = supported
	
	identifier: Optional[int]
	timestamp: Optional[int]
	subpixel_order: Optional[SubpixelOrder]
	gamma: Optional[Gamma]
	brightness: Optional[Rational]
	clones: Optional[Sequence[str]]
	crtc: Optional[int]
	crtcs: Optional[Sequence[int]]
	panning: Optional[XRandRGeometry]
	tracking: Optional[XRandRGeometry]
	border: Optional[XRandRBorder]
	transform: Optional[XRandRTransform]
	edid: Optional[bytes]
	guid: Optional[bytes]
	other: Optional[Mapping[str, OtherProperty]]
	
	def __init__(
		self,
		identifier: Optional[int] = None,
		timestamp: Optional[int] = None,
		subpixel_order: Optional[SubpixelOrder] = None,
		gamma: Optional[Gamma] = None,
		brightness: Optional[Rational] = None,
		clones: Optional[Sequence[str]] = None,
		crtc: Optional[int] = None,
		crtcs: Optional[Sequence[int]] = None,
		panning: Optional[XRandRGeometry] = None,
		tracking: Optional[XRandRGeometry] = None,
		border: Optional[XRandRBorder] = None,
		transform: Optional[XRandRTransform] = None,
		edid: Optional[bytes] = None,
		guid: Optional[bytes] = None,
		other: Optional[Mapping[str, OtherProperty]] = None
	) -> None:
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
