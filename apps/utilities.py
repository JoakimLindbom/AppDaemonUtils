#################################################################
"""
Utilities class for various functions used across AppDaemon apps
"""
__author__     = "Joakim Lindbom"
__copyright__  = "Copyright 2020-2022, Joakim Lindbom"
__date__       = "2020-12-29"
__credits__    = ["Joakim Lindbom"]
__license__    = "GPL Public License Version 3"
__maintainer__ = "Joakim Lindbom"
__email__      = 'Joakim.Lindbom@gmail.com'
__status__     = "Experimental"
__version__    = "0.0.1"
#################################################################

import hassapi as hass
from datetime import datetime, timedelta

# General utilities
def return_list(list_or_single):
    """ Returns a list, regardless if inpout is list of single instance"""
    if isinstance(list_or_single, list):
        return list_or_single
    else:
        return [list_or_single]


class Utilities(hass.Hass):
    def initialize(self):
        return

class Util():
    def initialize(self):
        return

    def time_split(self, duration, steps, from_brightness=None, to_brightness=None):
        """
        :param duration: How long duration, expressed as HH:MM:MM, e.g. 00:20:00 for 20 minutes
        :param steps: How many steps to split into
        :return: list of timestamps
        """
        tm_list = []
        br_list = []
        tfmt = '%H:%M:%S'
        br = 0 if from_brightness is None else from_brightness

        if steps > 0:
            br0 = br

            now = datetime.now()  # TODO: self.datetime
            tmdelta = datetime.strptime(duration, tfmt)

            seconds = tmdelta.hour * 3600 + tmdelta.minute * 60 + tmdelta.second

            for i in range(1, steps + 1):
                new_time = now + timedelta(0, i * seconds / steps)
                tm_list.append(new_time)
                br += 0 if from_brightness is None else round((to_brightness - from_brightness) / steps)
                if br > to_brightness:
                    br = to_brightness
                br_list.append(br)

        return tm_list, br_list

    def morning_time(self, time, sunrise):
        print (f"time {time}, sunrise {sunrise}")


class SchedulerItem:
    def __iter__(self):
        pass


class SchedulerItemIterator:
    '''Iterator for SchedulerItem
    '''
    def __init__(self):
        self._si = SchedulerItem
        self._index = 0

    def __next__(self):
        if self._index < (len(self._si)):
            result = (self._si[self._index])
            self._index += 1
            return result
        raise StopIteration

class Scheduler:
    def __init__(self):
        pass

    def addDict (self, dict):
        pass


def truncate(n):
    return int(n * 100000) / 100000


class Fader(hass.Hass):
    def __init__(self, ad, name, logging, args, config, app_config, global_vars):
        pass

    def initialize(self):
        self.handlers = []
        self.remote = None
        self.break_remote = None

        self.set_log_level("DEBUG")

        try:
            self.retry = self.args["retry"].lower() == "true"
            self.log(f"--- Retry: {self.retry}", level="DEBUG")
        except KeyError:
            self.retry = False
        self.log(f"--- Retry: {self.retry}", level="DEBUG")

        try:
            self.retrytimes = self.args["retrytimes"]
            self.log(f"--- Retry times: {self.retrytimes}", level="DEBUG")
        except KeyError:
            self.retrytimes = 3
        self.log(f"--- Retry times: {self.retrytimes}", level="DEBUG")
