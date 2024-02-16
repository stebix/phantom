from typing import Iterable

from phantom.compartment.compartment import (MagnetizationParams,
                                             GeometricParams,
                                             LabelParams,
                                             Morphology,
                                             CompartmentSpec)

from phantom.stencil import create_circular_positions

def int_ID_homogenous(dicts: Iterable[dict]) -> bool:
    """
    Checks if the integer IDs are homogenously `None`.
    """
    unique = {d.get('int_ID') for d in dicts}
    return len(unique) == 1 and unique.pop() is None


def int_ID_are_unique(dicts: Iterable[dict]) -> bool:
    """
    Checks that the values of the 'int_ID' key across all dictionaries are unique.
    """
    unique = set()
    every = []
    for d in dicts:
        ID = d.get('int_ID')
        unique.add(ID)
        every.append(ID)
    
    return len(unique) == len(every)



def from_dicts(canvas_shape: tuple[int, int],
               radius: int,
               morphology: str | Morphology,
               parameters: Iterable[dict]
               ) -> list[CompartmentSpec]:

    morphology = Morphology(morphology) if isinstance(morphology, str) else morphology

    if int_ID_homogenous(parameters):
        # auto-assign integer ID
        for i, parameter in enumerate(parameters):
            parameter.update({'int_ID' : i})

    else:
        # integer IDs are preset by user and thus have to be checked for uniqueness
        if not int_ID_are_unique(parameters):
            raise ValueError('integer ID must be either unqiue or all None '
                             'for automatic ID assigment')
    
    parameters = sorted(parameters, key=lambda p: p['int_ID'])
    lblsparams = [
        LabelParams(int_ID=p['int_ID'], name=p.get('name', None))
        for p in parameters
    ]
    magparams = [
        MagnetizationParams(PD=p['PD'], T1=p['T1'], T2=p['T2'])
        for p in parameters
    ]
    positions = create_circular_positions(len(parameters),
                                          canvas_shape=canvas_shape,
                                          radius=radius)
    geoparams = [
        GeometricParams(center=position, morphology=morphology)
        for position in positions
    ]
    compartments = []
    for magparam, lblparam, geoparam in zip(magparams, lblsparams, geoparams):
        compartment = CompartmentSpec(magnetization_params=magparam,
                                      labels=lblparam, geometry=geoparam)
        compartments.append(compartment)
    return compartments
