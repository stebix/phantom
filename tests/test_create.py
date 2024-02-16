from  phantom.compartment.create import int_ID_homogenous, int_ID_are_unique, from_dicts


def test_int_ID_homogenous_None_positive():
    dicts = [
        {'int_ID' : None} for _ in range(4)
    ]
    assert int_ID_homogenous(dicts)


def test_int_ID_homogenous_None_negative():
    dicts = [
        {'int_ID' : None} for _ in range(4)
    ]
    dicts.append({'int_ID' : 42})
    assert not int_ID_homogenous(dicts)


def test_int_ID_unique_positive():
    dicts = [
        {'int_ID' : i} for i in range(5)
    ]
    dicts.append({'int_ID' : 6})
    assert int_ID_are_unique(dicts)


def test_int_ID_unique_negative():
    dicts = [
        {'int_ID' : i} for i in range(4)
    ]
    dicts.append({'int_ID' : 2})
    assert not int_ID_are_unique(dicts)



def test_from_dicts():
    canvas_shape = (256, 256)
    radius = 12
    morphology = 'disk'
    parameters = [
        {'PD' : 1.0, 'T1' : 100, 'T2' : 50},
        {'PD' : 0.7, 'T1' : 1000, 'T2' : 250},
        {'PD' : 0.9, 'T1' : 700, 'T2' : 300}
    ]
    compartments = from_dicts(canvas_shape=canvas_shape,
                              radius=radius,
                              morphology=morphology,
                              parameters=parameters)
    assert len(compartments) == len(parameters)
    print(compartments)
