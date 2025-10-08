import pytest

from trips.models import Trip


@pytest.mark.parametrize(
    ("x1", "y1", "x2", "y2", "calc_distance"),
    [pytest.param(0, 0, 100, 100, 200), pytest.param(12, 32, 9, 30, 5)],
)
def test_manhattan_distance(
    x1: int, y1: int, x2: int, y2: int, calc_distance: int
) -> None:
    distance = Trip.calculate_manhattan_distance(x1, y1, x2, y2)
    assert distance == calc_distance
