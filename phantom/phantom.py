import numpy as np
import matplotlib.pyplot as plt
import matplotlib.axes as axes

from typing import Iterable, Literal

import attrs
import skimage.morphology as morph

from phantom.compartment.compartment import (Morphology, MagnetizationParams,
                                             LabelParams, CompartmentSpec,
                                             EnvironmentSpec,
                                             compartment_info)

import phantom.compartment.create as compartment_create
from phantom.stencil import create_stencil, create_simple_phantom_mask, add_host_environment_disk

# create some defaults for basal background and host compartment 
DEFAULT_BACKGROUND_MAG = MagnetizationParams(PD=0.0, T1=1, T2=1)
DEFAULT_BACKGROUND_LBL = LabelParams(int_ID=-2, name='background')
DEFAULT_BACKGROUND = EnvironmentSpec(DEFAULT_BACKGROUND_MAG, DEFAULT_BACKGROUND_LBL)

DEFAULT_WATER_MAG = MagnetizationParams(PD=1.0, T1=4000, T2=2000)
DEFAULT_WATER_LBL = LabelParams(int_ID=-1, name='host-water')
DEFAULT_WATER = EnvironmentSpec(DEFAULT_WATER_MAG, DEFAULT_WATER_LBL)



def add_integer_label_at_center(ax: axes.Axes,
                                compartments: Iterable[CompartmentSpec], **text_kwargs) -> None:
    """
    Place the integer ID at the center position of the compartments.
    Additional kwargs are directly passed to the `ax.text` function.
    """
    defaults = {'fontweight' : 'bold', 'ha' : 'center', 'va' : 'center'}
    kwargs = defaults | text_kwargs
    for compspec in compartments:
        I, J = compspec.geometry.center
        # changed order: ax.text uses math-graph odering
        ax.text(J, I, s=str(compspec.labels.int_ID), **kwargs)



def add_textbox(ax: axes.Axes, s: str) -> None:
    """
    Add a textbox on the top-right edge of the axes.
    Modifies in-place.

    Parameter
    =========

    ax : matplotlib.axes.Axes
        Axes to which the textbox is added.

    s : str
        Data included in the textbox.
    """
    fontsize = 8
    x = 1.03
    y = 0.98
    properties = {'boxstyle' : 'round', 'facecolor' : 'grey', 'alpha' : 0.15}
    ax.text(x, y, s, transform=ax.transAxes, fontsize=fontsize,
            bbox=properties, verticalalignment='top')




@attrs.define
class BasicPhantom:
    array: np.ndarray
    compartments: list[CompartmentSpec]
    hostmedium: EnvironmentSpec = attrs.field(default=DEFAULT_WATER)
    background: EnvironmentSpec = attrs.field(default=DEFAULT_BACKGROUND)


    def compartments_entirety(self) -> list[CompartmentSpec, EnvironmentSpec]:
        """
        Get the entirety of compartments, i.e. foreground, hostmedium and background.
        """
        return [self.background, self.hostmedium, *self.compartments]

        
    def plot_array(self, ax: axes.Axes | None = None,
                   show_int_labels: bool = False,
                   show_legend: bool = False,
                   legend_kwargs: dict | None = None
                   ) -> axes.Axes:
        """
        Plot the underlying array data.
        
        Parameters
        ==========
        
        ax : matplotlib.Axes.Axes
            The axes into wich the 2D array is plottes. Will be created if not
            given.
            
        show_int_labels : bool, optional
            Flag to overlay compartment integer overlay onto the
            array plot.
            
        show_legend : bool, optional
             Toggle legend.
             
        legend_kwargs : dict
            Legend settings.
        """
        legend_kwargs = legend_kwargs or {}
        if not ax:
            fig, ax = plt.subplots()
        img = ax.imshow(self.array)

        if show_int_labels:
            add_integer_label_at_center(ax, compartments=self.compartments)

        if show_legend:
            add_textbox(ax, s=compartment_info(self.compartments, include_name=False))

        return ax


    @classmethod
    def from_dicts(cls,
                   canvas_shape: tuple[int, int],
                   stencil_radius: int,
                   morphology: str | Morphology,
                   position_radius: int,
                   specifications: Iterable[dict]
                   ) -> 'BasicPhantom':
        """
        Create the basic phantom from the canvas shape, the morphology and its radius
        and a variable number of magnetization and label specifications.

        Parameters
        ==========

        canvas_shape : tuple[int, int]
            Shape of the 2D background canvas.

        stencil_radius : int
            Radius of the stencil morphology.

        morphology : str or Morphology
            Form/shape/morphology of the stencil. Can be one of
            {'disk', 'star', 'diamond', 'square'}

        position_radius : int
            Radius of the positioning of the stencils on
            a circle inside the canvas shape.

        specifications : Iterable of dict
            Free-form magnetization and label specifications for
            the compartments.
        """
        stencil = create_stencil(morphology=morphology, radius=stencil_radius)
        compartments = compartment_create.from_dicts(canvas_shape=canvas_shape,
                                                     radius=position_radius,
                                                     morphology=morphology,
                                                     parameters=specifications)
        positions = [c.geometry.center for c in compartments]
        mask = create_simple_phantom_mask(stencil=stencil, canvas_shape=canvas_shape,
                                          positions=positions, odd_preference='post')
        # mask = add_host_environment_disk(mask)
        return cls(mask, compartments)
        

    def map(self, parameter: Literal['PD', 'T1', 'T2']) -> np.ndarray:
        """
        Return the requested parameter map.
        """
        parameter_map = np.full(shape=self.array.shape,
                                fill_value=np.nan,
                                dtype=np.float32)
                                
        for compartment in self.compartments_entirety():
            pvalue = getattr(compartment.magnetization_params, parameter)
            mask = self.array == compartment.labels.int_ID
            parameter_map[mask] = pvalue

        if np.any(np.isnan(parameter_map)):
            raise RuntimeError('warp core breach: detected NaN in parameter map')
        
        return parameter_map
