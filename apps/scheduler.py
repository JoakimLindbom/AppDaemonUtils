from time import mktime, localtime
from datetime import datetime

from datetime import date
from zoneinfo import ZoneInfo
from workalendar.europe import Sweden

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
            # tomorrow - add 24*60*60 to epoch?? What about DST?
            t = (now.year, now.month, now.day, int(self._hour), int(self._minute), int(self._sec),
                 now.timetuple().tm_wday, now.timetuple().tm_yday, now.timetuple().tm_isdst)
            self._next = mktime(t) + 24*60*60
        else:
            t = (now.year, now.month, now.day, int(self._hour), int(self._minute), int(self._sec),
                 now.timetuple().tm_wday, now.timetuple().tm_yday, now.timetuple().tm_isdst)
            self._next = mktime(t)

    def __str__(self):
        next = f"{localtime(self._next).tm_hour}:{localtime(self._next).tm_min}:{localtime(self._next).tm_sec}"  # next is in UTC - how to convert to local time zone?
        return f"Time: {self._time} Next: {next} {self._operation} Entities: {self._entities}"

class SchedulerItems:
    def __init__(self):
        self._si = list()

    def __iter__(self):
        return SchedulerItemsIterator(self)

    def __len__(self):
        return len(self._si)

    def sort(self):
        pass

    def get_index(self, ix):
        return self._si[ix]

    def add_scheduleritem(self, si: SchedulerItem) -> bool:
        self._si += [si]
        return True

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
        cal = Sweden()
        self.holidays = cal.holidays(now.year)
        self.sis = SchedulerItems()

    def add(self, time, operation, entities):
        s = SchedulerItem(time, operation, entities)
        self.sis.add_scheduleritem(s)

    def list_items(self, from_time=None, to_time=None):
        pass


    def add_dict(self, dict):
        pass

    # TODO: Check All saints day 2022-11-05 - bug?
    def check_nonworkingday(self) -> bool:
        now = datetime.now()
        if now.weekday() in [5, 6]:  # Weekend
            return True

        for h in self.holidays:
            if h[0].month == now.month and h[0].day == now.day:
                return True

        return False
