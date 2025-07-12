from datetime import datetime
from enum import IntEnum

class WeekDay(IntEnum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

    def __str__(self):
        return self.name.capitalize()

    def __repr__(self):
        return self.name.capitalize()

STRTOWEEKDAY = {
    'mon' : WeekDay.MONDAY,
    'tue' : WeekDay.TUESDAY,
    'wed' : WeekDay.WEDNESDAY,
    'thu' : WeekDay.THURSDAY,
    'fri' : WeekDay.FRIDAY,
    'sat' : WeekDay.SATURDAY,
    'sun' : WeekDay.SUNDAY
}

class TimeBoundary():

    def __init__(self, day: WeekDay, hour: int, minute: int):
        if not isinstance(day, WeekDay):
            raise ValueError('Day needs to be a valid WeekDay')
        if not isinstance(hour, int):
            raise ValueError('hour needs to be a valid integer')
        if not 0 <= hour <= 23:
            raise ValueError('hour needs to be between 0 and 23')
        if not isinstance(minute, int):
            raise ValueError('minute needs to be a valid integer')
        if not 0 <= minute <= 59:
            raise ValueError('minute needs to be between 0 and 59')

        self.day = day
        self.hour = hour
        self.minute = minute
        self.inthour = hour * 100 + minute

    def __str__(self):
        return f"{self.day} {self.hour:02}:{self.minute:02}"

    def __lt__(self, other):
        if isinstance(other, TimeBoundary):
            if self.day < other.day:
                return True
            if self.day == other.day:
                if self.inthour < other.hour * 100 + other.minute:
                    return True
            return False
        if isinstance(other, datetime):
            if self.day < other.isoweekday():
                return True
            if self.day == other.isoweekday():
                if self.inthour < other.hour * 100 + other.minute:
                    return True
            return False
        raise NotImplemented()

    def __le__(self, other):
        if isinstance(other, TimeBoundary):
            if self.day < other.day:
                return True
            if self.day == other.day:
                if self.inthour <= other.hour * 100 + other.minute:
                    return True
            return False
        if isinstance(other, datetime):
            if self.day < other.isoweekday():
                return True
            if self.day == other.isoweekday():
                if self.inthour <= other.hour * 100 + other.minute:
                    return True
            return False
        raise NotImplemented()

    def __gt__(self, other):
        if isinstance(other, TimeBoundary):
            if self.day > other.day:
                return True
            if self.day == other.day:
                if self.inthour > other.hour * 100 + other.minute:
                    return True
            return False
        if isinstance(other, datetime):
            if self.day > other.isoweekday():
                return True
            if self.day == other.isoweekday():
                if self.inthour > other.hour * 100 + other.minute:
                    return True
            return False
        raise NotImplemented()

    def __ge__(self, other):
        if isinstance(other, TimeBoundary):
            if self.day > other.day:
                return True
            if self.day == other.day:
                if self.inthour >= other.hour * 100 + other.minute:
                    return True
            return False
        if isinstance(other, datetime):
            if self.day > other.isoweekday():
                return True
            if self.day == other.isoweekday():
                if self.inthour >= other.hour * 100 + other.minute:
                    return True
            return False
        raise NotImplemented()

    def __eq__(self, other):
        if isinstance(other, TimeBoundary):
            if all([self.day == other.day,
                    self.hour == other.hour,
                    self.minute == other.minute]):
                return True
            return False
        if isinstance(other, datetime):
            if all([self.day == other.isoweekday(),
                    self.hour == other.hour,
                    self.minute == other.minute]):
                return True
            return False
        raise NotImplemented()

    @classmethod
    def from_string(cls, buf: str):
        day = STRTOWEEKDAY.get(buf[:3])
        if day is None:
            raise ValueError(f'{buf[:3]} is not valid')
        hour, minute = buf[4:].split(':')
        if not hour.isdigit():
            raise ValueError(f'{hour} is not a valid hour')
        if not minute.isdigit():
            raise ValueError(f'{minute} is not a valid hour')
        return TimeBoundary(day, int(hour), int(minute))

class WeekTimeRange():

    def __init__(self, begin: TimeBoundary, end: TimeBoundary):
        if end < begin:
            raise ValueError('Begin must be < to end')
        self._begin = begin
        self._end = end

    def __str__(self):
        return f'WeekTimeRange from {self._begin} to {self._end}'

    def __repr__(self):
        return str(self)

    def match(self, dt: datetime) -> bool:
        if self._begin <= dt <= self._end:
            return True
        return False

class WeekTimeRangeValue(WeekTimeRange):

    def __init__(self, begin: TimeBoundary, end: TimeBoundary, value: int):
        self.value = value
        super().__init__(begin, end)

    def __str__(self):
        return f'WeekTimeRangeValue from {self._begin} to {self._end} = {self.value}'

    @classmethod
    def from_string(cls, buf):
        timerange, value = buf.split('=')
        if not value.isdigit():
            raise ValueError('{value} needs to be an int')
        b_str, e_str = timerange.split(';')
        begin = TimeBoundary.from_string(b_str)
        end = TimeBoundary.from_string(e_str)
        return WeekTimeRangeValue(begin, end, int(value))
