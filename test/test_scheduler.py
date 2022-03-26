import unittest
from scheduler import *
lights_panels = {"light.panel_vanster", "light.panel_hoger"}


class TestScheduler1(unittest.TestCase):

    def test_si(self):
        s = SchedulerItems()
        si = SchedulerItem("10:00", "ON", lights_panels)
        s.add_scheduleritem(si)
        si = SchedulerItem("22:00:00", "OFF", lights_panels)
        s.add_scheduleritem(si)
        self.assertRaises(ValueError, SchedulerItem, "23:00:00", "XYZ", lights_panels)  # Invalid operation

        self.assertEqual(len(s), 2)
        i = 0
        for s1 in s:
            print(s1)
            if i == 0:
                self.assertEqual(s1._operation, "ON")
                self.assertEqual(s1._entities, lights_panels)
            if i == 1:
                self.assertEqual(s1._operation, "OFF")
                self.assertEqual(s1._entities, lights_panels)
            i += 1
