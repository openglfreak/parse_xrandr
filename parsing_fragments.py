# noqa: E302
# xnoqa: W191,W293,E128,W503,E302,E501
import re
from typing import Iterable, Match, Optional, Pattern, Tuple

from .classes import XRandRBorder, XRandRDimensions, XRandRGeometry, \
                     XRandROffset, XRandROutput, XRandROutputProperties, \
                     XRandRScreen, XRandRScreenDimensionsList, XRandRTransform
from .mappings import text_to_flag, text_to_reflection, text_to_rotation, \
                      text_to_subpixel_order, text_to_supported_reflection
from .parser import MatchCallback, ParserAction, ParserState, parse


screen_regex = re.compile(r'Screen\s*(?P<screen_number>\d+):\s*')
def screen_func(
        state: ParserState,
        match: Match[str]
) -> Tuple[ParserAction, bool]:
    screen: XRandRScreen = XRandRScreen(int(match.group('screen_number')))
    state.data[screen.number] = screen

    state.position = match.end()

    state.string, state.position, screen.dimensions = parse(
        state.string,
        state.position,
        ((screen_dimensions_regex, screen_dimensions_func),),
        XRandRScreenDimensionsList()
    )[:-1]
    state.string, state.position, screen.outputs = parse(
        state.string,
        state.position,
        ((output_regex, output_func),),
        {}
    )[:-1]

    return ParserAction.Again, False


screen_dimensions_regex = re.compile(
    r'''
    (?P<type>minimum|current|maximum)
    \s+(?P<width>\d+)\s*x\s*(?P<height>\d+)
    \s*(?:,\s*)?
    ''',
    re.VERBOSE | re.MULTILINE
)
def screen_dimensions_func(
        state: ParserState,
        match: Match[str]
) -> ParserAction:
    dim: XRandRDimensions[int] = XRandRDimensions(
        int(match.group('width')),
        int(match.group('height'))
    )
    _type: Optional[str] = match.group('type')
    if _type == 'minimum':
        state.data.minimum = dim
    elif _type == 'current':
        state.data.current = dim
    else:
        assert _type == 'maximum'
        state.data.maximum = dim

    return ParserAction.Again


output_regex = re.compile(
    r'''
    (?P<name>\S+)
    \s+(?P<connection>connected|disconnected|unknown\ connection)
    (?:\s+(?P<primary>primary))?
    (?:
        \s+(?P<geometry>
            (?P<width>\d+)x(?P<height>\d+)
            \+(?P<x>\d+)\+(?P<y>\d+)
        )
        (?:\s+\((?P<mode>0x[0-9A-Fa-f]+)\))?
        (?:
            \s+(?P<rotation>normal|left|inverted|right|invalid\ rotation)
            (?:\s+(?P<reflection>none|X\ axis|Y\ axis|X\ and\ Y\ axis|
                invalid\ reflection))?
        )?
    )?\s*
    ''',
    re.VERBOSE | re.MULTILINE
)
def output_func(
        state: ParserState,
        match: Match[str]
) -> Tuple[ParserAction, bool]:
    output: XRandROutput = XRandROutput(match.group('name'))
    state.data[output.name] = output

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

    state.position = match.end()

    if (len(state.string) > state.position
            and state.string[state.position] == '('):
        state.position += 1

        state.string, state.position, output.supported_rotations = parse(
            state.string,
            state.position,
            ((
                output_supported_rotation_regex,
                output_supported_rotation_func
            ),),
            []
        )[:-1]
        state.string, state.position, output.supported_reflections = parse(
            state.string,
            state.position,
            ((
                output_supported_reflection_regex,
                output_supported_reflection_func
            ),),
            []
        )[:-1]

    state.string, state.position, output = parse(
        state.string,
        state.position,
        ((output_regex2, output_func2),),
        output
    )[:-1]

    state.string, state.position, output.properties = parse(
        state.string,
        state.position,
        output_property_parser_list,
        XRandROutputProperties(),
        ParserAction.Continue
    )[:-1]

    state.string, state.position, output.modes = parse(
        state.string,
        state.position,
        (
            (output_mode_nonverbose_regex, output_mode_nonverbose_func),
            (output_mode_verbose_regex, output_mode_verbose_func)
        ),
        [],
        ParserAction.Again
    )[:-1]

    return ParserAction.Again, False


output_supported_rotation_regex = re.compile(
    r'''
    (?P<supported_rotation>normal|left|inverted|right)
    \s*(?:\s|(?P<end>\)\s*))
    ''',
    re.VERBOSE | re.MULTILINE
)
def output_supported_rotation_func(
        state: ParserState,
        match: Match[str]
) -> ParserAction:
    state.data.append(text_to_rotation[match.group('supported_rotation')])
    return ParserAction.Stop if match.group('end') else ParserAction.Again


output_supported_reflection_regex = re.compile(
    r'''
    (?P<supported_reflection>x\ axis|y\ axis)
    \s*(?:\s|(?P<end>\)\s*))
    ''',
    re.VERBOSE | re.MULTILINE
)
def output_supported_reflection_func(
        state: ParserState,
        match: Match[str]
) -> ParserAction:
    state.data.append(
        text_to_supported_reflection[match.group('supported_reflection')]
    )
    return ParserAction.Stop if match.group('end') else ParserAction.Again


output_regex2 = re.compile(
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
    re.VERBOSE | re.MULTILINE
)
def output_func2(state: ParserState, match: Match[str]) -> ParserAction:
    output: XRandROutput = state.data
    output.dimensions_mm = XRandRDimensions[int](
        int(match.group('width_mm')),
        int(match.group('height_mm'))
    )
    if match.group('panning'):
        output.panning = XRandRGeometry[int](
            XRandRDimensions[int](
                int(match.group('pan_width')),
                int(match.group('pan_height'))
            ),
            XRandROffset[int](
                int(match.group('pan_left')),
                int(match.group('pan_top'))
            )
        )
    if match.group('tracking'):
        output.tracking = XRandRGeometry[int](
            XRandRDimensions[int](
                int(match.group('track_width')),
                int(match.group('track_height'))
            ),
            XRandROffset[int](
                int(match.group('track_left')),
                int(match.group('track_top'))
            )
        )
    if match.group('border'):
        output.border = XRandRBorder[int](
            int(match.group('border_left')),
            int(match.group('border_top')),
            int(match.group('border_right')),
            int(match.group('border_bottom'))
        )
    return ParserAction.Stop


output_property_identifier_regex = re.compile(
    r'''(?<=^\t)
    Identifier:\s*(?P<identifier>0x[0-9A-Fa-f]+)
    \s*
    ''',
    re.VERBOSE | re.MULTILINE
)
def output_property_identifier_func(
        state: ParserState,
        match: Match[str]
) -> None:
    state.data.identifier = int(match.group('identifier'), 16)


output_property_timestamp_regex = re.compile(
    r'''(?<=^\t)
    Timestamp:\s*(?P<timestamp>\d+)
    \s*
    ''',
    re.VERBOSE | re.MULTILINE
)
def output_property_timestamp_func(
        state: ParserState,
        match: Match[str]
) -> None:
    state.data.timestamp = int(match.group('timestamp'))


output_property_subpixel_order_regex = re.compile(
    r'''
    (?<=^\t)Subpixel:\s*
    (?P<subpixel_order>
        unknown
        |(?:horizontal|vertical)\ (?:rgb|bgr)
        |no\ subpixels
    )\s*
    ''',
    re.VERBOSE | re.MULTILINE
)
def output_property_subpixel_order_func(
        state: ParserState,
        match: Match[str]
) -> None:
    state.data.subpixel_order = (
        text_to_subpixel_order[match.group('subpixel_order')]
    )


output_property_gamma_regex = re.compile(
    r'''
    (?<=^\t)Gamma:\s*
    (?P<gamma_red>\d*\.\d*(?:e\d+)?)
    :(?P<gamma_green>\d*\.\d*(?:e\d+)?)
    :(?P<gamma_blue>\d*\.\d*(?:e\d+)?)
    \s*
    ''',
    re.VERBOSE | re.MULTILINE
)
def output_property_gamma_func(
        state: ParserState,
        match: Match[str]
) -> None:
    state.data.gamma = XRandROutputProperties.Gamma(
        float(match.group('gamma_red')),
        float(match.group('gamma_green')),
        float(match.group('gamma_blue'))
    )


output_property_brightness_regex = re.compile(
    r'''
    (?<=^\t)Brightness:\s*
    (?P<brightness>\d*\.\d*(?:e\d+)?)
    \s*
    ''',
    re.VERBOSE | re.MULTILINE
)
def output_property_brightness_func(
        state: ParserState,
        match: Match[str]
) -> None:
    state.data.brightness = float(match.group('brightness'))


output_property_clones_regex = re.compile(
    r'''(?<=^\t)
    Clones:[^\S\n]*(?P<clones>(?:\S+[^\S\n]*)*)
    \s*
    ''',
    re.VERBOSE | re.MULTILINE
)
def output_property_clones_func(
        state: ParserState,
        match: Match[str]
) -> None:
    state.data.clones = match.group('clones').split()


output_property_crtc_regex = re.compile(
    r'''(?<=^\t)
    CRTC:\s*(?P<crtc>\d+)
    \s*
    ''',
    re.VERBOSE | re.MULTILINE
)
def output_property_crtc_func(
        state: ParserState,
        match: Match[str]
) -> None:
    state.data.crtc = int(match.group('crtc'))


output_property_crtcs_regex = re.compile(
    r'''(?<=^\t)
    CRTCs:\s*(?P<crtcs>(?:\d+(?:$|\s+))+)
    \s*
    ''',
    re.VERBOSE | re.MULTILINE
)
def output_property_crtcs_func(
        state: ParserState,
        match: Match[str]
) -> None:
    state.data.crtcs = tuple(
        int(crtc) for crtc in match.group('crtcs').split()
    )


output_property_panning_regex = re.compile(
    r'''
    (?<=^\t)Panning:\s*
    (?P<pan_width>\d+)x(?P<pan_height>\d+)
    \+(?P<pan_left>\d+)\+(?P<pan_top>\d+)
    \s*
    ''',
    re.VERBOSE | re.MULTILINE
)
def output_property_panning_func(
        state: ParserState,
        match: Match[str]
) -> None:
    state.data.panning = XRandRGeometry(
        XRandRDimensions(
            int(match.group('pan_width')),
            int(match.group('pan_height'))
        ),
        XRandROffset(
            int(match.group('pan_left')),
            int(match.group('pan_top'))
        )
    )


output_property_tracking_regex = re.compile(
    r'''
    (?<=^\t)Tracking:\s*
    (?P<track_width>\d+)x(?P<track_height>\d+)
    \+(?P<track_left>\d+)\+(?P<track_top>\d+)
    \s*
    ''',
    re.VERBOSE | re.MULTILINE
)
def output_property_tracking_func(
        state: ParserState,
        match: Match[str]
) -> None:
    state.data.tracking = XRandRGeometry(
        XRandRDimensions(
            int(match.group('track_width')),
            int(match.group('track_height'))
        ),
        XRandROffset(
            int(match.group('track_left')),
            int(match.group('track_top'))
        )
    )


output_property_border_regex = re.compile(
    r'''
    (?<=^\t)Border:\s*
    (?P<border_left>\d+)\s+
    (?P<border_top>\d+)\s+
    (?P<border_right>\d+)\s+
    (?P<border_bottom>\d+)\s+
    range:.*
    \s*
    ''',
    re.VERBOSE | re.MULTILINE
)
def output_property_border_func(
        state: ParserState,
        match: Match[str]
) -> None:
    state.data.border = XRandRBorder(
        int(match.group('border_left')),
        int(match.group('border_top')),
        int(match.group('border_right')),
        int(match.group('border_bottom'))
    )


output_property_transform_regex = re.compile(
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
    re.VERBOSE | re.MULTILINE
)
def output_property_transform_func(
        state: ParserState,
        match: Match[str]
) -> None:
    state.data.transform = XRandRTransform(  # type: ignore
        *tuple(float(v) for v in match.group('matrix').split()),
        match.group('filter') or None
    )


output_property_edid_regex = re.compile(
    r'''
    (?<=^\t)EDID:\s*
    (?P<edid>
        (?:(?:[0-9A-Fa-f][0-9A-Fa-f]){16}\s*)*
        (?:[0-9A-Fa-f][0-9A-Fa-f])*
    )\s*
    ''',
    re.VERBOSE | re.MULTILINE
)
def output_property_edid_func(
        state: ParserState,
        match: Match[str]
) -> None:
    state.data.edid = bytes.fromhex(match.group('edid'))


output_property_guid_regex = re.compile(
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
    re.VERBOSE | re.MULTILINE
)
def output_property_guid_func(
        state: ParserState,
        match: Match[str]
) -> None:
    state.data.edid = bytes.fromhex(
        match.group('guid')[1:-1].replace('-', '')
    )


output_property_other_regex = re.compile(
    r'''
    (?<=^\t)(?P<name>[^:]+):[^\S\n]*(?P<value>.*)\s*
    (?:(?P<range>range:)|(?P<supported>supported:))?
    ''',
    re.VERBOSE | re.MULTILINE
)
def output_property_other_func(
        state: ParserState,
        match: Match[str]
) -> Optional[Tuple[None, bool]]:
    output_property = XRandROutputProperties.OtherProperty(
        match.group('name'),
        match.group('value')
    )
    if state.data.other is None:
        state.data.other = {}
    state.data.other[output_property.name] = output_property
    if output_property.value[-1] == ' ':
        output_property.value = output_property.value[:-1]

    regex = None
    if match.group('range'):
        regex = (
            output_property_other_range_regex,
            output_property_other_range_func
        )
    if match.group('supported'):
        assert regex is None
        regex = (
            output_property_other_supported_regex,
            output_property_other_supported_func
        )

    state.position = match.end()
    if regex is not None:
        state.string, state.position, output_property = parse(
            state.string,
            state.position,
            (regex,),
            output_property
        )[:-1]
        return None, False
    return None


output_property_other_range_regex = re.compile(
    r'''
    \ \((?P<start_val>[^,]+),
    \ (?P<end_val>[^)]+)\)
    \ (?:,|(?P<end>$\s*))
    ''',
    re.VERBOSE | re.MULTILINE
)
def output_property_other_range_func(
        state: ParserState,
        match: Match[str]
) -> ParserAction:
    if state.data.range is None:
        state.data.range = []
    state.data.range.append(
        (match.group('start_val'), match.group('end_val'))
    )
    return ParserAction.Stop if match.group('end') else ParserAction.Again


output_property_other_supported_regex = re.compile(
    r'''
    \ (?P<value>[^\n,]+)
    (?:,|(?P<end>$\s*))
    ''',
    re.VERBOSE | re.MULTILINE
)
def output_property_other_supported_func(
        state: ParserState,
        match: Match[str]
) -> ParserAction:
    if state.data.supported is None:
        state.data.supported = []
    state.data.supported.append(match.group('value'))
    return ParserAction.Stop if match.group('end') else ParserAction.Again


output_property_parser_list: Iterable[Tuple[Pattern[str], MatchCallback]] = (
    (output_property_identifier_regex, output_property_identifier_func),
    (output_property_timestamp_regex, output_property_timestamp_func),
    (output_property_subpixel_order_regex,
     output_property_subpixel_order_func),
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


output_mode_nonverbose_regex = re.compile(
    r'''(?<=^\ {3})
    (?P<name>(?P<width>\d+)x(?P<height>\d+))[^\S\n]+
    ''',
    re.VERBOSE | re.MULTILINE
)
output_mode_nonverbose_clock_regex = re.compile(
    r'''
    (?P<clock>\d*\.\d*)
    (?P<current>\*|\ )
    (?P<preferred>\+|\ )
    \s*
    ''',
    re.VERBOSE | re.MULTILINE
)
def output_mode_nonverbose_func(
        state: ParserState,
        match: Match[str]
) -> ParserAction:
    name = match.group('name')
    width = int(match.group('width'))
    height = int(match.group('height'))

    state.position = match.end()
    _match: Optional[Match[str]]
    while True:
        _match = output_mode_nonverbose_clock_regex.match(
            state.string,
            pos=state.position
        )
        if not _match:
            break

        mode = XRandROutput.Mode(
            name=name,
            current=(_match.group('current') == '*'),
            preferred=(_match.group('preferred') == '+'),
            width=width,
            height=height
        )

        state.data.append(mode)
        state.position = _match.end()

    return ParserAction.Again


output_mode_verbose_regex = re.compile(
    r'''
    (?<=^\ {2})(?P<name>\S+)\s+
    \((?P<id>0x[0-9A-Fa-f]+)\)\s+
    (?P<dotclock>\d*\.\d*)MHz
    \s*
    ''',
    re.VERBOSE | re.MULTILINE
)
def output_mode_verbose_func(
        state: ParserState,
        match: Match[str]
) -> Tuple[ParserAction, bool]:
    mode = XRandROutput.Mode(
        name=match.group('name'),
        id=int(match.group('id'), 16),
        dotclock=float(match.group('dotclock')) * 1000000
    )
    state.data.append(mode)

    state.position = match.end()

    state.string, state.position, mode.flags = parse(
        state.string,
        state.position,
        ((output_mode_verbose_flag_regex, output_mode_verbose_flag_func),),
        XRandROutput.Mode.Flags(0)
    )[:-1]
    state.string, state.position, mode = parse(
        state.string,
        state.position,
        ((output_mode_verbose_regex2, output_mode_verbose_func2),),
        mode
    )[:-1]

    return ParserAction.Again, False


output_mode_verbose_flag_regex = re.compile(
    r'(?P<flag>'
    + r'|'.join(re.escape(flag) for flag in text_to_flag)
    + r')\s*(?:\s|(?P<end>$\s*))',
    re.MULTILINE
)
def output_mode_verbose_flag_func(
        state: ParserState,
        match: Match[str]
) -> ParserAction:
    state.data |= text_to_flag[match.group('flag')]
    if match.group('end') is not None:
        return ParserAction.Stop
    return ParserAction.Again


output_mode_verbose_regex2 = re.compile(
    r'''
    (?P<current>\*current\s+)?
    (?P<preferred>\+preferred\s+)?

    (?<=^\ {8})h:\s*
    width\s+(?P<width>\d+)\s+
    start\s+(?P<h_sync_start>\d+)\s+
    end\s+(?P<h_sync_end>\d+)\s+
    total\s+(?P<h_total>\d+)\s+
    skew\s+(?P<h_skew>\d+)\s+
    clock\s+(?P<h_clock>\d*\.\d*)KHz\s+

    (?<=^\ {8})v:\s*
    height\s+(?P<height>\d+)\s+
    start\s+(?P<v_sync_start>\d+)\s+
    end\s+(?P<v_sync_end>\d+)\s+
    total\s+(?P<v_total>\d+)\s+
    clock\s+(?P<refresh>\d*\.\d*)Hz
    \s*
    ''',
    re.VERBOSE | re.MULTILINE
)
def output_mode_verbose_func2(
        state: ParserState,
        match: Match[str]
) -> ParserAction:
    mode: XRandROutput.Mode = state.data

    mode.current = bool(match.group('current'))
    mode.preferred = bool(match.group('preferred'))

    mode.width = int(match.group('width'))
    mode.h_sync_start = int(match.group('h_sync_start'))
    mode.h_sync_end = int(match.group('h_sync_end'))
    mode.h_total = int(match.group('h_total'))
    mode.h_skew = int(match.group('h_skew'))
    mode.h_clock = float(match.group('h_clock')) * 1000

    mode.height = int(match.group('height'))
    mode.v_sync_start = int(match.group('v_sync_start'))
    mode.v_sync_end = int(match.group('v_sync_end'))
    mode.v_total = int(match.group('v_total'))
    mode.refresh = float(match.group('refresh'))

    return ParserAction.Stop


__all__ = [v for v in globals() if v.endswith(('_func', '_regex'))]
