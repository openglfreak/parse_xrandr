from enum import unique, IntEnum, IntFlag, auto

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
