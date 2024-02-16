"""
Encode information about compartments (of a basic phantom) into
composite data objects.

@jsteb 2024
"""
import enum
import attrs

from typing import Iterable

from phantom.position import Position


class Morphology(enum.Enum):
    """
    Compartment morphologies."""
    SQUARE = 'square'
    DISK = 'disk'
    DIAMOND = 'diamond'
    STAR = 'star'



@attrs.define
class MagnetizationParams:
    """
    Magnetization-specific parameters.

    Maybe extend to further parameters.
    """
    PD: float = attrs.field()
    T1: float = attrs.field()
    T2: float = attrs.field()

    @PD.validator
    def _PD_validator(self, attribute, value):
        if value > 1 or value < 0:
            raise ValueError(f'PD value must be between 0.0 and 1.0 (got {value})')
        
    @T1.validator
    def _T1_validator(self, attribute, value):
        if value < 0:
            raise ValueError(f'T1 relaxation time must be positive (got {value})')

    @T2.validator
    def _T2_validator(self, attribute, value):
        if value < 0:
            raise ValueError(f'T2 relaxation time must be positive (got {value})')



        
@attrs.define
class LabelParams:
    int_ID: int
    name: str | None = attrs.field(default=None)
        
        
@attrs.define
class GeometricParams:
    center: Position
    morphology: Morphology
    

@attrs.define
class CompartmentSpec:
    magnetization_params: MagnetizationParams
    labels: LabelParams
    geometry: GeometricParams


@attrs.define
class EnvironmentSpec:
    """
    encodes information about delocalized 'environment' compartments without any
    geometry information.
    """
    magnetization_params: MagnetizationParams
    labels: LabelParams



def compartment_info(compartments: Iterable[CompartmentSpec],
                     include_name: bool = False,
                     indent: int = 4) -> str:
    """
    Create a nice information string about the compartments.
    
    Parameters
    ==========
    
    compartments : Iterable[CompartmentSpec]
    
    include_name : bool, optional
        Include the compartment string name in the information
        display. defaults to `False`.
        
    indent : int, optional
        Number of spaces the information string about magnetization
        parameters is indented under the integer ID and name row.
        Defaults to 4.
    """
    s = ''
    indent = ''.join((' ' for _ in range(indent)))
    for compartment in compartments:
        ID = compartment.labels.int_ID
        name = compartment.labels.name if include_name else ''
        PD = compartment.magnetization_params.PD
        T1 = compartment.magnetization_params.T1
        T2 = compartment.magnetization_params.T2
        s += f'ID {ID} {name}\n{indent}PD = {PD:.2f} T1 = {T1:.1f} ms T2 = {T2:.1f} ms\n'
    return s
