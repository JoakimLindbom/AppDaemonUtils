from time import mktime, gmtime
from datetime import datetime

class SchedulerItem:
    def __init__(self, time, operation, entities):

        self._time = time + ":00" if len(time) == 5 else time
        if operation in ["ON", "OFF", "FADE"]:
            self._operation = operation
        else:
            raise ValueError
        self._hour = self._time[0:2]
        self._minute = self._time[3:5]
        self._sec = self._time[6:8]

        self._entities = entities

        now = datetime.now()
        if True:  # Check is time has passed for today
            t = (now.year, now.month, now.day, int(self._hour), int(self._minute), int(self._sec), now.timetuple().tm_wday, now.timetuple().tm_yday, now.timetuple().tm_isdst)
            self._next = mktime(t)

    def __str__(self):
        next = f"{gmtime(self._next).tm_hour}:{gmtime(self._next).tm_min}:{gmtime(self._next).tm_sec}"  # next is in UTC - how to convert to local time zone?
        return f"Time: {self._time} Next: {next} {self._operation} Entities: {self._entities}"

class SchedulerItems:
    def __init__(self):
        self._si = list()

    def __iter__(self):
        return SchedulerItemsIterator(self)

    def __len__(self):
        return len(self._si)

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
        pass

    def add_dict (self, dict):
        pass

