#################
#
# Controls family state (Working, vacation, etc.)
#
# TODO: Read vacation plans from calendar
# TODO: Add support for other non-working days, based on country or other external source.. Or also get from calendar?

import hassapi as hass
from datetime import datetime
from globals import *


class FamilyStateController(hass.Hass):
    """
    Utility to control scheduling, providing family state (WORKING, NONWORKING & VACATION)
    Also controls an input_number if it's day or night, usable in graphs to provide x-scale 12h shading

    Configuration expected in apps.yaml:
    family_state_controller:
      module: family_state
      class: FamilyStateController
      input_select: input_select.myfamily_mode_indicator
      night_select: input_number.mynight_time_indicator
    """

    def initialize(self):
        self.set_log_level("DEBUG")
        self.log("Family state controller")
        handle = self.run_in(self.check_weekday, 1)
        handle = self.run_daily(self.check_weekday, "03:06:00")
        handle = self.run_daily(self.set_daytime, "08:00:00")
        handle = self.run_daily(self.set_nighttime, "20:00:00")

        try:
            self.input_select = self.args["input_select"]
        except KeyError:
            self.log("Missing input_select configuration. Cannot continue")
        try:
            self.night_select = self.args["night_select"]
        except KeyError:
            self.night_select = None
            self.log("Missing night_select configuration. Gracefully degrading")


    def check_weekday(self, kwargs):
        self.log("Setting family state based on weekday")
        family_state = self.get_state(self.input_select)
        self.log(f"Current state: {family_state}")
        if family_state != VACATION:
            day = datetime.today().weekday()  # TODO: self.datetime
            if day >= 5:
                self.log("It's week-end!")
                self.select_option(self.input_select, NON_WORKING)
            else:
                self.log("It's work day")
                self.select_option(self.input_select, WORKING)
        family_state = self.get_state(self.input_select)
        self.log(f"New state: {family_state}", level="DEBUG")

    def set_daytime(self, kwargs):
        self.log("Set daytime")
        if self.night_select is not None:
            self.set_value(self.night_select, 0.0)

    def set_nighttime(self, kwargs):
        self.log("Set nighttime")
        if self.night_select is not None:
            self.set_value(self.night_select, 1.0)
