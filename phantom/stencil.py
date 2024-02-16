"""
Basic stencil and composition functionality to create the core phantom masks/

@jsteb 2024
"""
import numpy as np

from typing import Iterable, Literal, Callable
from numbers import Number

import skimage.morphology as morph

from phantom.position import Position
from phantom.compartment.compartment import Morphology


def get_morphology_create_fn(morphology: str | Morphology) -> Callable[[int], np.ndarray]:
    morphology = Morphology(morphology) if isinstance(morphology, str) else morphology
    create_fn = {
        Morphology.DISK : morph.disk,
        Morphology.SQUARE : morph.square,
        Morphology.DIAMOND : morph.diamond,
        Morphology.STAR : morph.star,
    }
    return create_fn[morphology]



def create_stencil(morphology: str | Morphology,
                   radius: int) -> np.ndarray:
    morphology = Morphology(morphology) if isinstance(morphology, str) else morphology
    return get_morphology_create_fn(morphology)(radius=radius)



def create_simple_phantom_mask(
    stencil: np.ndarray,
    canvas_shape: tuple[int, int],
    positions: Iterable[Position],
    add_host_environment_disk: bool = True,
    odd_preference: Literal['pre', 'post'] = 'post',
    dtype: np.dtype = np.int32
) -> np.ndarray:
    """
    Create a simple phantom mask by placing the stencils at the indicated positions inside
    a host canvas shape.

    Parameters
    ==========

    stencil : np.ndarray
        Minimal stencil shape that will be center-placed
        at the given positions int the canvas shape.

    canvas_shape : tuple[int, int]
        Shape of the 2D background canvas.

    positions : Iterable of Position 
        The (I, J) position coordinate pairs for the stencils.

    add_host_environment_disk : bool , optional
        Enables placement of canvas-filling host environment.

    odd_preference : {'post', 'pre'}
        Prefered placement of adjustment pixels.

    dtype : np.dtype, optional
        Force the resulting phantom mask to the indicated
        NumPy datatype. Defaults to `np.int32`
    """
    background_offset = -2
    canvas = np.full(canvas_shape, fill_value=background_offset)
    layers = [canvas]
    for i, position in enumerate(positions, start=0):
        
        layer = embed_at(inlay=stencil, centerpos=position,
                         canvas_shape=canvas_shape, odd_preference=odd_preference)
        # give every layer its specific integer label and offset the background
        layer[layer > 0] = i + 2
        layers.append(layer)

    layers = np.stack(layers, axis=0)
    mask = np.sum(layers, axis=0)

    if add_host_environment_disk:
        radius = canvas_shape[0] // 2
        hostenv = create_stencil(morphology='disk', radius=radius)[:-1, :-1]
        mask[(mask < 0) & (hostenv > 0)] = -1

    return mask.astype(dtype)


def add_host_environment_disk(mask: np.ndarray) -> np.ndarray:
    """
    Going from basal FG <-> BG mask, this function creates a new mask where the 'deep'
    background sits at int_ID -2, the newly added host environment disk spanning the 
    entire square sits at int_ID -1.
    Thus the foreground compartments conveniently have their respective int_ID labels. 
    """
    radius = mask.shape[0] // 2
    # discard one row and one column to match original shape
    hostenv = create_stencil(morphology='disk', radius=radius)[:-1, :-1]
    canvas = (-2) * np.ones_like(mask)
    return canvas + hostenv + mask


def parameterized_circle(t: Number | np.ndarray, R: float) -> tuple[np.ndarray]:
    x = R * np.cos(t)
    y = R * np.sin(t)
    return (x, y)


def create_circular_positions(N: int, /, canvas_shape: Iterable[int], radius: int) -> list[Position]:
    """
    Create position coordinates for `N` compartments on a circle with specified radius.
    Host canvas size can be specified via `canvas_shape`.

    Parameters
    ==========

    N : int
        Number of compartments.

    canvas_shape : Iterable of int
        (I, J) size specification of the host canvas.

    radius : int
        Radius of the circle the compartments are placed on.
    """
    canvas_shape = np.array(canvas_shape)
    center = canvas_shape // 2
    increment = (2 * np.pi) / N
    angles = increment * np.arange(0, N)
    centroid_X, centroid_Y = parameterized_circle(angles, R=radius)
    X = centroid_X + center[0]
    Y = centroid_Y + center[1]
    positions = [
        Position(np.rint(x).astype(int), np.rint(y).astype(int))
        for x, y in zip(X, Y)
    ]
    return positions


def embed_at(inlay: np.ndarray, centerpos: Position, canvas_shape: tuple[int],
             odd_preference: Literal['pre', 'post'] = 'post'):
    """
    Place the `inlay` array such that the plane is embedded into to
    the desired shape at the indicate center position.
    """
    inlay_shape = np.array(inlay.shape)
    canvas_shape = np.array(canvas_shape)
    centerpos = np.array(centerpos)
    
    is_odd = inlay_shape[0] % 2 != 0
    if odd_preference not in {'pre', 'post'}:
        raise ValueError(f'invalid odd_preference \'{odd_preference}\'')
        
    pre_off = 1 if is_odd and (odd_preference == 'pre') else 0
    post_off = 1 if is_odd and (odd_preference == 'post') else 0
        
    if np.any((centerpos - (inlay_shape // 2 + 1)) < 0):
        raise ValueError(
            f'cannot embed inlay with shape {inlay_shape} into canvas with '
            f'shape {canvas_shape} at position {centerpos} - borders outside of region'
        )
    
    axis_0_pre = centerpos[0] - (inlay_shape[0] // 2 + pre_off)
    axis_0_post = canvas_shape[0] - (centerpos[0] + inlay_shape[0] // 2 + post_off)
    
    axis_1_pre = centerpos[1] - (inlay_shape[1] // 2 + pre_off)
    axis_1_post = canvas_shape[1] - (centerpos[1] + inlay_shape[1] // 2 + post_off)
    
    axis_0_spec = (axis_0_pre, axis_0_post)
    axis_1_spec = (axis_1_pre, axis_1_post)
    
    padspec = (axis_0_spec, axis_1_spec)
    embedded = np.pad(inlay, pad_width=padspec,
                      mode='constant', constant_values=0)
    
    return embedded