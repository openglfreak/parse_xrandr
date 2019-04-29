import enum
from typing import Any, Generic, Mapping, Optional, Sequence, Tuple, TypeVar, \
                   Union

__all__ = ('XRandRDimensions', 'XRandROffset', 'XRandRGeometry',
           'XRandRBorder', 'XRandRTransform', 'XRandRScreen',
           'XRandRScreenDimensionsList', 'XRandROutput',
           'XRandROutputProperties')

Rational = Union[int, float]
RationalT = TypeVar('RationalT', int, float)


class XRandRDimensions(Generic[RationalT]):
    __slots__ = ('width', 'height')
    width: Optional[RationalT]
    height: Optional[RationalT]

    def __init__(
            self,
            width: Optional[RationalT] = 0,
            heigth: Optional[RationalT] = 0
    ) -> None:
        self.width = width
        self.height = heigth


class XRandROffset(Generic[RationalT]):
    __slots__ = ('x', 'y')
    x: Optional[RationalT]
    y: Optional[RationalT]

    def __init__(
            self,
            x: Optional[RationalT] = 0,
            y: Optional[RationalT] = 0
    ) -> None:
        self.x = x
        self.y = y


class XRandRGeometry(Generic[RationalT]):
    __slots__ = ('dimensions', 'offset')
    dimensions: Optional[XRandRDimensions[RationalT]]
    offset: Optional[XRandROffset[RationalT]]

    def __init__(
            self,
            dimensions: Optional[XRandRDimensions[RationalT]] = None,
            offset: Optional[XRandROffset[RationalT]] = None
    ) -> None:
        self.dimensions = dimensions
        self.offset = offset


class XRandRBorder(Generic[RationalT]):
    __slots__ = ('left', 'top', 'right', 'bottom')
    left: Optional[RationalT]
    top: Optional[RationalT]
    right: Optional[RationalT]
    bottom: Optional[RationalT]

    def __init__(
            self,
            left: Optional[RationalT] = 0,
            top: Optional[RationalT] = 0,
            right: Optional[RationalT] = 0,
            bottom: Optional[RationalT] = 0
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
    minimum: Optional[XRandRDimensions[int]]
    current: Optional[XRandRDimensions[int]]
    maximum: Optional[XRandRDimensions[int]]

    def __init__(
            self,
            minimum: Optional[XRandRDimensions[int]] = None,
            current: Optional[XRandRDimensions[int]] = None,
            maximum: Optional[XRandRDimensions[int]] = None
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
    @enum.unique
    class Connection(enum.IntEnum):
        Connected = 0
        Disconnected = 1

    class Rotation(enum.IntEnum):
        Rotate_0 = 1
        Rotate_90 = 2
        Rotate_180 = 4
        Rotate_270 = 8

    class Reflection(enum.IntFlag):
        Reflect_X = 16
        Reflect_Y = 32

    class Mode:
        class Flags(enum.IntFlag):
            HSyncPositive = 1
            HSyncNegative = 2
            VSyncPositive = 4
            VSyncNegative = 8
            Interlace = 16
            DoubleScan = 32
            CSync = 64
            CSyncPositive = 128
            CSyncNegative = 256

        __slots__ = ('name', 'id', 'dotclock', 'flags', 'current', 'preferred',
                     'width', 'h_sync_start', 'h_sync_end', 'h_total',
                     'h_skew', '_h_clock', 'height', 'v_sync_start',
                     'v_sync_end', 'v_total', '_refresh')
        _h_clock: Optional[Rational]
        _refresh: Optional[Rational]

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

    __slots__ = ('name', 'connection', 'primary', 'geometry', 'mode',
                 'rotation', 'reflection', 'supported_rotations',
                 'supported_reflections', 'dimensions_mm', 'panning',
                 'tracking', 'border', 'properties', 'modes')
    name: str
    connection: Optional[Connection]
    primary: bool
    geometry: Optional[XRandRGeometry[int]]
    mode: Optional[int]
    rotation: Optional[Rotation]
    reflection: Optional[Reflection]
    supported_rotations: Optional[Rotation]
    supported_reflections: Optional[Reflection]
    dimensions_mm: Optional[XRandRDimensions[Any]]
    panning: Optional[XRandRGeometry[int]]
    tracking: Optional[XRandRGeometry[int]]
    border: Optional[XRandRBorder[int]]
    properties: Optional['XRandROutputProperties']
    modes: Optional[Sequence[Mode]]

    def __init__(
            self,
            name: str,
            connection: Optional[Connection] = None,
            primary: bool = False,
            geometry: Optional[XRandRGeometry[int]] = None,
            mode: Optional[int] = None,
            rotation: Optional[Rotation] = None,
            reflection: Optional[Reflection] = None,
            supported_rotations: Optional[Rotation] = None,
            supported_reflections: Optional[Reflection] = None,
            dimensions_mm: Optional[XRandRDimensions[Rational]] = None,
            panning: Optional[XRandRGeometry[int]] = None,
            tracking: Optional[XRandRGeometry[int]] = None,
            border: Optional[XRandRBorder[int]] = None,
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

    class SubpixelOrder(enum.IntEnum):
        HorizontalRGB = enum.auto()
        HorizontalBGR = enum.auto()
        VerticalRGB = enum.auto()
        VerticalBGR = enum.auto()
        NoSubpixels = enum.auto()

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
    panning: Optional[XRandRGeometry[int]]
    tracking: Optional[XRandRGeometry[int]]
    border: Optional[XRandRBorder[int]]
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
            panning: Optional[XRandRGeometry[int]] = None,
            tracking: Optional[XRandRGeometry[int]] = None,
            border: Optional[XRandRBorder[int]] = None,
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
