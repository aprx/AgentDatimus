
from datetime import datetime
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

def test_boundary_parsing():
    with pytest.raises(ValueError):
        TimeBoundary.from_string('monday 09:00')
    with pytest.raises(ValueError):
        TimeBoundary.from_string('Morning')
    with pytest.raises(ValueError):
        TimeBoundary.from_string('mon beforenoone:midnight')
    with pytest.raises(ValueError):
        TimeBoundary.from_string('monmonmonmon')

def test_boundray_operators():
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

    with pytest.raises(NotImplementedError):
        a > 42
    with pytest.raises(NotImplementedError):
        a < 42
    with pytest.raises(NotImplementedError):
        a <= 42
    with pytest.raises(NotImplementedError):
        a >= 42
    with pytest.raises(NotImplementedError):
        a == 42

    now = datetime.now()
    c = TimeBoundary(WeekDay(now.isoweekday()), now.hour, now.minute)
    assert c == now
    assert c >= now
    assert c <= now

    now = datetime.strptime('2025/01/01 10:10', '%Y/%m/%d %H:%M')
    b = TimeBoundary(WeekDay.TUESDAY, 10, 10)
    d = TimeBoundary(WeekDay.WEDNESDAY, 10, 10)
    a = TimeBoundary(WeekDay.THURSDAY, 10, 10)
    assert d == now
    assert b < now
    assert b <= now
    assert a > now
    assert a >= now

def test_weektimerange():
    now = datetime.strptime('2025/01/01 10:10', '%Y/%m/%d %H:%M')
    anotherday = datetime.strptime('2025/01/03 10:10', '%Y/%m/%d %H:%M')
    a = TimeBoundary(WeekDay.TUESDAY, 20, 42)
    b = TimeBoundary(WeekDay.THURSDAY, 20, 42)
    t = WeekTimeRange(a, b)
    with pytest.raises(ValueError):
        WeekTimeRange(b, a)
    assert t.match(now)
    assert not t.match(anotherday)

def test_weektimerangevalue():
    a = TimeBoundary(WeekDay.TUESDAY, 20, 42)
    b = TimeBoundary(WeekDay.THURSDAY, 20, 42)
    WeekTimeRangeValue(a, b, 42)
    with pytest.raises(ValueError):
        WeekTimeRangeValue(a, b, 'fourtytwo')

def test_weektimerangevalue_parsing():
    with pytest.raises(ValueError):
        WeekTimeRangeValue.from_string('mon 10:10;tue 10:10')
    with pytest.raises(ValueError):
        WeekTimeRangeValue.from_string('mon1010tue1010=10')
    with pytest.raises(ValueError):
        WeekTimeRangeValue.from_string('mon 10:10tue;10:10=fourtytwo')
    with pytest.raises(ValueError):
        WeekTimeRangeValue.from_string('coucou 10:10;tue10:10=42')
    with pytest.raises(ValueError):
        WeekTimeRangeValue.from_string('mon 10:10;coucou 10:10=42')
