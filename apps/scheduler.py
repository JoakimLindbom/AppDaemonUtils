from time import mktime, localtime
from datetime import datetime

from datetime import date
from zoneinfo import ZoneInfo
#from workalendar.europe import Sweden

class SchedulerItem:
    def __init__(self, time, operation, entities):
        self._time = time + ":00" if len(time) == 5 else time
        if operation in ["ON", "OFF", "FADE"]:
            self._operation = operation
        else:
            raise ValueError
        self._hour = int(self._time[0:2])
        self._minute = int(self._time[3:5])
        self._sec = int(self._time[6:8])

        self._entities = entities

        now = datetime.now(ZoneInfo("Europe/Stockholm"))
        if now.hour >= self._hour and now.minute >= self._minute:  # Check if time has passed for today
            t = (now.year, now.month, now.day, int(self._hour), int(self._minute), int(self._sec),
                 now.timetuple().tm_wday, now.timetuple().tm_yday, now.timetuple().tm_isdst)
            self._next = mktime(t) + 24*60*60  # tomorrow - add 24*60*60 to epoch?? What about DST?
        else:
            t = (now.year, now.month, now.day, int(self._hour), int(self._minute), int(self._sec),
                 now.timetuple().tm_wday, now.timetuple().tm_yday, now.timetuple().tm_isdst)
            self._next = mktime(t)

        self._sort_order = "C"  # Calendar based

    def __str__(self):
        next = f"{localtime(self._next).tm_hour}:{localtime(self._next).tm_min}:{localtime(self._next).tm_sec}"
        return f"Time: {self._time} Next: {next} - {self._operation} Entities: {self._entities}"

    def __repr__(self):
        next = f"{localtime(self._next).tm_hour}:{localtime(self._next).tm_min}:{localtime(self._next).tm_sec}"
        return f"Time: {self._time} Next: {next} - {self._operation} Entities: {self._entities}"

    def set_sort_order(self, sort_order) -> None:
        if sort_order in ("C", "T"):
            self._sort_order = sort_order
        else:
            raise ValueError

    def __lt__(self, other):
        if self._sort_order == "C":
            return self._next < other._next
        else:
            return self._time < other._time

class SchedulerItems:
    def __init__(self):
        self._si = list()
        self._sort_order = "C"

    def __iter__(self):
        return SchedulerItemsIterator(self)

    def __len__(self):
        return len(self._si)

    def sort(self):
        for s in self._si:
            s._sort_order = self._sort_order
        return sorted(self._si)  # , key=self._si._next ) # if self._sort_order=="C" else self._si._time)

    def get_index(self, ix):
        return self._si[ix]

    def add_scheduleritem(self, si: SchedulerItem) -> bool:
        if si._sort_order is not None:
            si._sort_order = self._sort_order
        self._si += [si]
        return True

    def set_sort_order(self, sort_order):
        if sort_order in ("C", "T"):
            self._sort_order = sort_order
            for s in self._si:
                s._sort_order = self._sort_order
        else:
            raise ValueError

class SchedulerItemsIterator:
    '''Iterator for SchedulerItems
    '''
    def __init__(self, scheduleritems: SchedulerItems):
        self._sis = scheduleritems
        self._index = 0

    def __next__(self):
        if self._index < len(self._sis):
            result = (self._sis.get_index(self._index))
            self._index += 1
            return result
        raise StopIteration

class Scheduler:
    def __init__(self):
        now = datetime.now(ZoneInfo("Europe/Stockholm"))
        #cal = Sweden()
        #self.holidays = cal.holidays(now.year)
        self.working_day_sensor = "binary_sensor.workday"
        self.sis = SchedulerItems()
        self._random_low = 0
        self._random_high = 0

    @property
    def random_low(self):
        return self._random_low

    @random_low.setter
    def random_low(self, low):
        self._random_low = low

    @property
    def random_high(self):
        return self._random_high

    @random_high.setter
    def random_high(self, high):
        self._random_high = high

    def add(self, time, operation, entities):
        s = SchedulerItem(time, operation, entities)
        self.sis.add_scheduleritem(s)

    def list_items(self, from_time=None, to_time=None):
        print("Sorting")
        for s in self.sis.sort():
            print(s)

    def add_dict(self, dict):
        pass

    def set_sort_order(self, sort_order):
        self.sis.set_sort_order(sort_order)

    # TODO: Check All saints day 2022-11-05 - bug?
    def check_nonworkingday(self) -> bool:
        workingday = self.get_state(self.working_day_sensor)
        return workingday

        #now = datetime.now()
        #if now.weekday() in [5, 6]:  # Weekend
        #    return True

        #for h in self.holidays:
        #    if h[0].month == now.month and h[0].day == now.day:
        #        return True

        #return False
