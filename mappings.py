from typing import Dict, Mapping, Optional, TypeVar

from .classes import XRandROutput, XRandROutputProperties

__all__ = ('text_to_rotation', 'rotation_to_text', 'text_to_reflection',
           'reflection_to_text', 'text_to_supported_reflection',
           'text_to_subpixel_order', 'text_to_flag')

KeyT = TypeVar('KeyT')
ValueT = TypeVar('ValueT')


def reverse_mapping(
        mapping: Mapping[KeyT, ValueT]
) -> Dict[ValueT, KeyT]:
    return {v: k for k, v in mapping.items()}


text_to_rotation: Dict[str, Optional[XRandROutput.Rotation]] = {
    'normal': XRandROutput.Rotation.Rotate_0,
    'left': XRandROutput.Rotation.Rotate_90,
    'inverted': XRandROutput.Rotation.Rotate_180,
    'right': XRandROutput.Rotation.Rotate_270,
    'invalid rotation': None
}
rotation_to_text: Dict[Optional[XRandROutput.Rotation], str] = \
    reverse_mapping(text_to_rotation)

text_to_reflection: Dict[str, Optional[XRandROutput.Reflection]] = {
    'none': XRandROutput.Reflection(0),
    'X axis': XRandROutput.Reflection.Reflect_X,
    'Y axis': XRandROutput.Reflection.Reflect_Y,
    'X and Y axis':
        XRandROutput.Reflection.Reflect_X | XRandROutput.Reflection.Reflect_Y,
    'invalid reflection': None
}
reflection_to_text: Dict[XRandROutput.Reflection, str] = {
    XRandROutput.Reflection(0): 'normal',
    XRandROutput.Reflection.Reflect_X: 'x',
    XRandROutput.Reflection.Reflect_Y: 'y',
    XRandROutput.Reflection.Reflect_X | XRandROutput.Reflection.Reflect_Y: 'xy'
}

text_to_supported_reflection: Dict[str, XRandROutput.Reflection] = {
    'x axis': XRandROutput.Reflection.Reflect_X,
    'y axis': XRandROutput.Reflection.Reflect_Y
}

text_to_subpixel_order: \
    Dict[str, Optional[XRandROutputProperties.SubpixelOrder]]
text_to_subpixel_order = {
    'horizontal rgb': XRandROutputProperties.SubpixelOrder.HorizontalRGB,
    'horizontal bgr': XRandROutputProperties.SubpixelOrder.HorizontalBGR,
    'vertical rgb': XRandROutputProperties.SubpixelOrder.VerticalRGB,
    'vertical bgr': XRandROutputProperties.SubpixelOrder.VerticalBGR,
    'no subpixels': XRandROutputProperties.SubpixelOrder.NoSubpixels,
    'unknown': None
}

text_to_flag: Dict[str, XRandROutput.Mode.Flags] = {
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
