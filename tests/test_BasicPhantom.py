import copy
import numpy as np

import pytest

from phantom.phantom import BasicPhantom
from phantom.compartment.compartment import compartment_info

def test_create_from_dicts():
    canvas_shape = (256, 256)
    stencil_radius = 12
    position_radius = 40
    morphology = 'disk'
    specification = [
        {'PD' : 1.0, 'T1' : 100, 'T2' : 50},
        {'PD' : 0.7, 'T1' : 1000, 'T2' : 250},
        {'PD' : 0.9, 'T1' : 700, 'T2' : 300}
    ]
    phantom = BasicPhantom.from_dicts(canvas_shape=canvas_shape,
                                      stencil_radius=stencil_radius,
                                      morphology=morphology,
                                      position_radius=position_radius,
                                      specifications=specification)
    
    assert phantom.array.shape == canvas_shape
    array_uniques = set(np.unique(phantom.array))
    compartments = [
        *copy.deepcopy(phantom.compartments),
        phantom.background, phantom.hostmedium
    ]
    comp_uniques = set(c.labels.int_ID for c in compartments)
    assert array_uniques == comp_uniques


def test_retrieval_of_PD_map():
    canvas_shape = (256, 256)
    stencil_radius = 12
    position_radius = 40
    morphology = 'disk'
    specification = [
        {'PD' : 1.0, 'T1' : 100, 'T2' : 50},
        {'PD' : 0.7, 'T1' : 1000, 'T2' : 250},
        {'PD' : 0.9, 'T1' : 700, 'T2' : 300}
    ]
    phantom = BasicPhantom.from_dicts(canvas_shape=canvas_shape,
                                      stencil_radius=stencil_radius,
                                      morphology=morphology,
                                      position_radius=position_radius,
                                      specifications=specification)
    PD_map = phantom.map('PD')

    arr = phantom.array
    print(arr.dtype)
    print(np.sum(arr == 1))

    assert PD_map.shape == canvas_shape