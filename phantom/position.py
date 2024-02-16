"""
EZ 2D vector :O

@jsteb 2024
"""
from typing import NamedTuple


class Position(NamedTuple):
    x: int
    y: int

    @property
    def P(self) -> 'Position':
        """Return permutation.
        Useful for scenarios where 'ij' (matrix-like)
        and 'xy' (math plotting) conventions are used simultaneously.
        """
        return Position(self.y, self.x)