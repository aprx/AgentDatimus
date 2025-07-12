import pytest
from agentdatimus.weektimerangevalue import WeekDay, TimeBoundary, WeekTimeRange, WeekTimeRangeValue

def test_boundaries():
    with pytest.raises(ValueError):
        TimeBoundary('Monday', 1, 10)
    with pytest.raises(ValueError):
        TimeBoundary(1, 1, 10)
    with pytest.raises(ValueError):
        TimeBoundary(WeekDay.MONDAY, 25, 42)
    with pytest.raises(ValueError):
        TimeBoundary(WeekDay.MONDAY, 20, 92)

    a = TimeBoundary(WeekDay.MONDAY, 20, 42)
    b = TimeBoundary(WeekDay.MONDAY, 20, 40)
    assert b < a
    assert b <= a
    assert a > b
    assert a >= b

    a = TimeBoundary(WeekDay.MONDAY, 20, 42)
    b = TimeBoundary(WeekDay.MONDAY, 20, 42)
    assert a == b
    assert b <= a
    assert b >= a
    assert not b > a
    assert not b < a

def test_boundary_parsing():
    with pytest.raises(ValueError):
        TimeBoundary.from_string('monday 09:00')
    with pytest.raises(ValueError):
        TimeBoundary.from_string('Morning')
    with pytest.raises(ValueError):
        TimeBoundary.from_string('mon beforenoone:midnight')

def test_weektimerange():
    a = TimeBoundary(WeekDay.MONDAY, 20, 42)
    b = TimeBoundary(WeekDay.TUESDAY, 20, 42)
    t = WeekTimeRange(a, b)
    with pytest.raises(ValueError):
        WeekTimeRange(b, a)

