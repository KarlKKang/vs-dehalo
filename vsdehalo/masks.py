import vapoursynth as vs
from vsmask.edge import TriticalTCanny
from vsrgtools.util import PlanesT, iterate, norm_expr_planes
from vsutil import disallow_variable_format, disallow_variable_resolution

__all__ = [
    'TritSigmaTCanny',
    # morpho functions
    'dilation', 'erosion', 'closing', 'opening', 'gradient', 'top_hat', 'black_hat'
]

core = vs.core


class TritSigmaTCanny(TriticalTCanny):
    sigma: float = 0

    def __init__(self, sigma: float = 0) -> None:
        super().__init__()
        self.sigma = sigma

    def _compute_edge_mask(self, clip: vs.VideoNode) -> vs.VideoNode:
        return clip.tcanny.TCanny(self.sigma, mode=1, op=0)


@disallow_variable_format
@disallow_variable_resolution
def dilation(src: vs.VideoNode, radius: int = 1, planes: PlanesT = None) -> vs.VideoNode:
    if radius < 1:
        raise RuntimeError('mask.dilation: radius has to be greater than 0!')

    return iterate(src, core.std.Maximum, radius, planes)


@disallow_variable_format
@disallow_variable_resolution
def erosion(src: vs.VideoNode, radius: int = 1, planes: PlanesT = None) -> vs.VideoNode:
    if radius < 1:
        raise RuntimeError('mask.erosion: radius has to be greater than 0!')

    return iterate(src, core.std.Minimum, radius, planes)


@disallow_variable_format
@disallow_variable_resolution
def closing(src: vs.VideoNode, radius: int = 1, planes: PlanesT = None) -> vs.VideoNode:
    if radius < 1:
        raise RuntimeError('mask.closing: radius has to be greater than 0!')

    dilated = dilation(src, radius, planes)
    eroded = erosion(dilated, radius, planes)

    return eroded


@disallow_variable_format
@disallow_variable_resolution
def opening(src: vs.VideoNode, radius: int = 1, planes: PlanesT = None) -> vs.VideoNode:
    if radius < 1:
        raise RuntimeError('mask.opening: radius has to be greater than 0!')

    eroded = erosion(src, radius, planes)
    dilated = dilation(eroded, radius, planes)

    return dilated


@disallow_variable_format
@disallow_variable_resolution
def gradient(src: vs.VideoNode, radius: int = 1, planes: PlanesT = None) -> vs.VideoNode:
    if radius < 1:
        raise RuntimeError('mask.gradient: radius has to be greater than 0!')

    eroded = erosion(src, radius, planes)
    dilated = dilation(src, radius, planes)

    return core.std.Expr([dilated, eroded], norm_expr_planes(src, 'x y -', planes))


@disallow_variable_format
@disallow_variable_resolution
def top_hat(src: vs.VideoNode, radius: int = 1, planes: PlanesT = None) -> vs.VideoNode:
    if radius < 1:
        raise RuntimeError('mask.top_hat: radius has to be greater than 0!')

    opened = opening(src, radius, planes)

    return core.std.Expr([src, opened], norm_expr_planes(src, 'x y -', planes))


@disallow_variable_format
@disallow_variable_resolution
def black_hat(src: vs.VideoNode, radius: int = 1, planes: PlanesT = None) -> vs.VideoNode:
    if radius < 1:
        raise RuntimeError('mask.black_hat: radius has to be greater than 0!')

    closed = closing(src, radius, planes)

    return core.std.Expr([closed, src], norm_expr_planes(src, 'x y -', planes))