import unittest
from scheduler import *

import datetime as dt

from zoneinfo import ZoneInfo
import time_machine

lights_panels = {"light.panel_vanster", "light.panel_hoger"}


class TestScheduler1(unittest.TestCase):
    def setUp(self) -> None:
        self.s = SchedulerItems()
        self.si = SchedulerItem("10:00", "ON", lights_panels)
        self.s.add_scheduleritem(self.si)
        self.si = SchedulerItem("22:00:00", "OFF", lights_panels)
        self.s.add_scheduleritem(self.si)


    def test_si(self):
        self.assertRaises(ValueError, SchedulerItem, "23:00:00", "XYZ", lights_panels)  # Invalid operation

        self.assertEqual(len(self.s), 2)
        i = 0
        for s1 in self.s:
            print(s1)
            if i == 0:
                self.assertEqual(s1._operation, "ON")
                self.assertEqual(s1._entities, lights_panels)
            if i == 1:
                self.assertEqual(s1._operation, "OFF")
                self.assertEqual(s1._entities, lights_panels)
            i += 1

    def test_si_iterator(self):
        for s1 in self.s:
            print(s1)

        i = 0
        reiterate = False
        for s1 in self.s:
            print(s1)
            if i == 1:
                reiterate = True
            i += 1
        self.assertEqual(reiterate, True)  # Proving you can reiterate

class TestScheduler_tomorrow(unittest.TestCase):
    @time_machine.travel(dt.datetime(2022, 4, 2, 10, 15, 0, tzinfo=ZoneInfo("Europe/Stockholm")))
    def test_time_passed(self):
        self.s = SchedulerItems()
        self.si = SchedulerItem("10:00", "ON", lights_panels)
        self.s.add_scheduleritem(self.si)
        self.si = SchedulerItem("22:00:00", "OFF", lights_panels)
        self.s.add_scheduleritem(self.si)

        i = 0
        for s1 in self.s:
            print(s1)
            t1 = dt.datetime(2022, 4, 3 if i == 0 else 2, 10 if i == 0 else 22, 0, tzinfo=ZoneInfo("Europe/Stockholm"))
            t2 = (t1.year, t1.month, t1.day, t1.hour, t1.minute, t1.second,
                 t1.timetuple().tm_wday, t1.timetuple().tm_yday, t1.timetuple().tm_isdst)
            t3 = mktime(t2)
            self.assertEqual(t3, s1._next)
            i += 1


class TestScheduler_nonworkingdays(unittest.TestCase):

    def test_nonworkingday_sunday(self):
        with time_machine.travel(dt.date(2022, 3, 27)):
            sch = Scheduler()
            self.assertEqual(True, sch.check_nonworkingday())

    def test_nonworkingdays_monday(self):

        with time_machine.travel(dt.date(2022, 3, 28)):  # Monday
            sch = Scheduler()
            self.assertEqual(False, sch.check_nonworkingday())

    def test_nonworkingdays_xmas(self):
        with time_machine.travel(dt.date(2022, 12, 26)):  # Monday and x-mas
            sch = Scheduler()
            self.assertEqual(True, sch.check_nonworkingday())
