import pytest

from phantom.phantom import MagnetizationParams



def test_PD_validation_correct_range():
    with pytest.raises(ValueError):
        mp = MagnetizationParams(PD=-1, T1=100, T2=50)

    with pytest.raises(ValueError):
        mp = MagnetizationParams(PD=1.5, T1=100, T2=50)


def test_T1_validation_is_positive():
    with pytest.raises(ValueError):
        mp = MagnetizationParams(PD=1.0, T1=-100, T2=50)


def test_T2_validation_is_positive():
    with pytest.raises(ValueError):
        mp = MagnetizationParams(PD=1.0, T1=100, T2=-50)