import os
import enum
from typing import Dict, Iterable, List, Optional, Union

from .classes import Any, XRandRBorder, XRandRDimensions, XRandRGeometry, \
                     XRandROffset, XRandROutput, XRandROutputProperties, \
                     XRandRScreen
from .mappings import reflection_to_text, rotation_to_text

__all__ = ('XRandRConfigurationOptions', 'configure_screens',
           'configure_outputs')


class XRandRConfigurationOptions(enum.Flag):
    ConfigureNone = 0

    ConfigureScreenDimensions = enum.auto()
    ConfigureScreenPrimaryOutput = enum.auto()
    ConfigureScreens = \
        ConfigureScreenDimensions |\
        ConfigureScreenPrimaryOutput

    ConfigureOutputPosition = enum.auto()
    ConfigureOutputMode = enum.auto()
    ConfigureOutputRotation = enum.auto()
    ConfigureOutputReflection = enum.auto()
    ConfigureOutputPanning = enum.auto()
    ConfigureOutputTracking = enum.auto()
    ConfigureOutputBorder = enum.auto()
    ConfigureOutputsBasic = \
        ConfigureOutputPosition |\
        ConfigureOutputMode |\
        ConfigureOutputRotation |\
        ConfigureOutputReflection |\
        ConfigureOutputPanning |\
        ConfigureOutputTracking |\
        ConfigureOutputBorder

    ConfigureOutputProperties = enum.auto()
    ConfigureUnknownOutputProperties = enum.auto()
    ConfigureOutputsAll = \
        ConfigureOutputsBasic |\
        ConfigureOutputProperties |\
        ConfigureUnknownOutputProperties

    ConfigureAll = ~ConfigureNone


def configure_screens(
        screens: Union[Iterable[XRandRScreen], Dict[str, XRandRScreen]],
        config_options: XRandRConfigurationOptions =
        ~XRandRConfigurationOptions.ConfigureUnknownOutputProperties
) -> None:
    if not config_options & XRandRConfigurationOptions.ConfigureAll:
        return

    _screens: Iterable[XRandRScreen]
    if isinstance(screens, dict):
        _screens = screens.values()
    else:
        _screens = screens

    args: Optional[Iterable[Union[str, bytes]]] = _configure_screens_args(
        _screens,
        config_options
    )
    if args:
        os.spawnlp(os.P_WAIT, 'xrandr', 'xrandr', *args)

    if not (config_options
            & XRandRConfigurationOptions.ConfigureUnknownOutputProperties):
        return

    for screen in _screens:
        if screen.outputs:
            for output in screen.outputs.values():
                if output.properties and output.properties.other:
                    _configure_output_unknown_properties(
                        screen.number,
                        output.name,
                        output.properties.other.values(),
                        config_options
                    )


def configure_outputs(
        screen_nr: int,
        outputs: Union[Iterable[XRandROutput], Dict[str, XRandROutput]],
        config_options: XRandRConfigurationOptions =
        ~XRandRConfigurationOptions.ConfigureUnknownOutputProperties
) -> None:
    if not config_options & XRandRConfigurationOptions.ConfigureOutputsAll:
        return

    _outputs: Iterable[XRandROutput]
    if isinstance(outputs, dict):
        _outputs = outputs.values()
    else:
        _outputs = outputs

    args: Optional[Iterable[Union[str, bytes]]] = _configure_outputs_args(
        _outputs,
        config_options
    )
    if args:
        os.spawnlp(
            os.P_WAIT,
            'xrandr',
            'xrandr', '--screen', str(screen_nr), *args
        )

    if not (config_options
            & XRandRConfigurationOptions.ConfigureUnknownOutputProperties):
        return

    for output in _outputs:
        if output.properties and output.properties.other:
            _configure_output_unknown_properties(
                screen_nr,
                output.name,
                output.properties.other.values(),
                config_options
            )


def _configure_screens_args(
        screens: Iterable[XRandRScreen],
        config_options: XRandRConfigurationOptions
) -> Optional[List[str]]:
    if not config_options & XRandRConfigurationOptions.ConfigureScreens:
        return None

    args: List[str] = []

    for screen in screens:
        _args: List[str] = []

        if ((config_options
             & XRandRConfigurationOptions.ConfigureScreenDimensions)
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
        if ((config_options
             & XRandRConfigurationOptions.ConfigureScreenPrimaryOutput)
                and screen.outputs):
            has_primary: bool = False
            for output in screen.outputs.values():
                if output and output.primary:
                    has_primary = True
            if not has_primary:
                _args.append('--noprimary')

        if screen.outputs:
            _args.extend(
                _configure_outputs_args(
                    screen.outputs.values(),
                    config_options
                ) or ()
            )
        if _args:
            args.extend(('--screen', str(screen.number)))
            args.extend(_args)

    return args


def _configure_outputs_args(
        outputs: Iterable[XRandROutput],
        config_options: XRandRConfigurationOptions
) -> Optional[List[str]]:
    if not (config_options
            & XRandRConfigurationOptions.ConfigureOutputsAll
            & ~XRandRConfigurationOptions.ConfigureUnknownOutputProperties):
        return None

    args: List[str] = []

    for output in outputs:
        _args: List[str] = []

        if ((config_options
             & XRandRConfigurationOptions.ConfigureScreenPrimaryOutput)
                and output.primary):
            _args.append('--primary')

        if (config_options & XRandRConfigurationOptions.ConfigureOutputMode
                and output.modes):
            mode: Optional[str] = None
            rate: Optional[float] = None

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
            elif output.mode is False:
                _args.append('--off')

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

        if ((config_options
             & XRandRConfigurationOptions.ConfigureOutputRotation)
                and output.rotation is not None):
            _args.extend((
                '--rotate',
                rotation_to_text[output.rotation]
            ))
        if ((config_options
             & XRandRConfigurationOptions.ConfigureOutputReflection)
                and output.reflection is not None):
            _args.extend((
                '--reflect',
                reflection_to_text[output.reflection]
            ))

        if config_options & XRandRConfigurationOptions.ConfigureOutputPanning:
            _panning: Optional[XRandRGeometry[int]]
            if output.properties:
                _panning = _merge_geometry_objects(
                    output.panning,
                    output.properties.panning
                )
            else:
                _panning = output.panning
            if (_panning
                    and _panning.dimensions
                    and _panning.dimensions.width is not None
                    and _panning.dimensions.height is not None):
                _panning_arg: str = '{!s}x{!s}'.format(
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
                if (config_options
                        & XRandRConfigurationOptions.ConfigureOutputTracking):
                    _tracking: Optional[XRandRGeometry[int]]
                    if output.properties:
                        _tracking = _merge_geometry_objects(
                            output.tracking,
                            output.properties.tracking
                        )
                    else:
                        _tracking = output.tracking
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
                        if (config_options
                                & XRandRConfigurationOptions
                                .ConfigureOutputBorder):
                            _border: Optional[XRandRBorder[int]]
                            if output.properties:
                                _border = _merge_border_objects(
                                    output.border,
                                    output.properties.border
                                )
                            else:
                                _border = output.border
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

        if ((config_options
             & XRandRConfigurationOptions.ConfigureOutputProperties)
                and output.properties):
            _args.extend(
                _configure_output_properties_args(
                    output.properties,
                    config_options
                ) or ()
            )
        if _args:
            args.extend(('--output', output.name))
            args.extend(_args)

    return args


def _merge_geometry_objects(
        a: Optional[XRandRGeometry[int]],
        b: Optional[XRandRGeometry[int]]
) -> Optional[XRandRGeometry[int]]:
    if a is None:
        return b
    if b is None:
        return a

    ret: XRandRGeometry[int] = XRandRGeometry[int]()

    if a.dimensions or b.dimensions:
        ret.dimensions = XRandRDimensions(None, None)
        if a.dimensions and a.dimensions.width is not None:
            ret.dimensions.width = a.dimensions.width
        elif b.dimensions:
            ret.dimensions.width = b.dimensions.width
        if a.dimensions and a.dimensions.height is not None:
            ret.dimensions.height = a.dimensions.height
        elif b.dimensions:
            ret.dimensions.height = b.dimensions.height
    if a.offset or b.offset:
        ret.offset = XRandROffset(None, None)
        if a.offset and a.offset.x is not None:
            ret.offset.x = a.offset.x
        elif b.offset:
            ret.offset.x = b.offset.x
        if a.offset and a.offset.y is not None:
            ret.offset.y = a.offset.y
        elif b.offset:
            ret.offset.y = b.offset.y

    return ret


def _merge_border_objects(
        a: Optional[XRandRBorder[int]],
        b: Optional[XRandRBorder[int]]
) -> Optional[XRandRBorder[int]]:
    if a is None:
        return b
    if b is None:
        return a

    return XRandRBorder[int](
        a.left if a.left is not None else b.left,
        a.top if a.top is not None else b.top,
        a.right if a.right is not None else b.right,
        a.bottom if a.bottom is not None else b.bottom
    )


def _configure_output_properties_args(
        properties: XRandROutputProperties,
        config_options: XRandRConfigurationOptions
) -> Optional[List[str]]:
    if not (config_options
            & ~XRandRConfigurationOptions.ConfigureOutputProperties):
        return None

    args: List[str] = []

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


def _configure_output_unknown_properties(
        screen_nr: int,
        output_name: str,
        properties: Iterable[XRandROutputProperties.OtherProperty],
        config_options: XRandRConfigurationOptions
) -> None:
    if not (config_options
            & XRandRConfigurationOptions.ConfigureUnknownOutputProperties):
        return

    for _property in properties:
        if _property.name:
            os.spawnlp(
                os.P_WAIT,
                'xrandr',
                'xrandr',
                '--screen',
                str(screen_nr),
                '--output',
                str(output_name),
                '--set',
                str(_property.name),
                _propval_to_str(_property.value)
                if _property.value is not None
                else ''
            )


def _propval_to_str(v: Any) -> str:
    if isinstance(v, (list, tuple, bytes)):
        return ','.join(str(x) for x in v)
    return str(v)
