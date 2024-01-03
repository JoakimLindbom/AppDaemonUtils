import hassapi as hass
#import time

# Entity                                    Power off       Power on        Printing    After printing
# sensor.octoprint_current_state            Unavailable     Operational     Printing    Operational         Cancelling
# binary_sensor.octoprint_printing          Unavailable     Off             On          Off
# binary_sensor.octoprint_printing_error    Unavailable     Off             Off         Off
# Cooling period

# TODO: Add a way of cancelling an ongoing wait for power off - now checking for changed state after cooldown period

class PrinterPower(hass.Hass):
    """
    Utility to power off a 3 printer using OctoPrint after printing has ended
    Expected configuration in apps.yaml:
    3Dprinter:
      module: 3Dprinter_power
      class: PrinterPower
      printer: sensor.myoctoprinter_current_state
      switch: switch.my3Dprinterswitch
      cooling_period_night: 5
      cooling_period_day: 10
      night_start: 22:00
      night_end: 09:00

    """

    def initialize(self):
        self.printer = None
        self.switch = None
        self.cooling_period_day = None
        self.cooling_period_night = None
        self.timer = None

        try:
            self.printer = self.args["printer"]
            self.switch = self.args["switch"]
            try:
                self.cooling_period_day = self.args["cooling_period_day"]
            except KeyError:
                self.cooling_period_day = 10
            try:
                self.cooling_period_night = self.args["cooling_period_night"]
            except KeyError:
                self.cooling_period_night = 5
            try:
                self.night_start = self.args["night_start"] + ":00"
            except KeyError:
                self.night_start = "22:00:00"
            try:
                self.night_end = self.args["night_end"] + ":00"
            except KeyError:
                self.night_end = "08:00:00"


            self.log("3D-printer power controller initiated")
            self.log(f"--- 3D printer: {self.printer}")
            self.log(f"--- Switch: {self.switch}")
            self.log(f"--- Cooling period day/night (minutes): {self.cooling_period_day}/{self.cooling_period_night}")
            self.log(f"--- Night start: {self.night_start}")
            self.log(f"--- Night end: {self.night_end}")

            self.listen_state(self.state_changed, self.printer)

        except KeyError:
            self.log("Missing parameters in apps.yaml file. Cannot continue")

    def state_changed(self, entity, attribute, old, new, kwargs):
        self.log("Printing - state_change detected", level="DEBUG")

        if new.lower() in ["printing"]: #TODO: Handle Cancelling
            if old.lower() == "operational" and self.timer is not None:
                self.cancel_timer(self.timer)
                self.timer = None
        elif new.lower() == "operational":
            if old.lower() == "printing":
                # if self.now_is_between("22:00:00", "10:00:00"):
                if self.now_is_between(self.night_start, self.night_end):
                    self.log("Printing stopped (night/morning - powering off)", level="DEBUG")
                    self.wait_for_power_off(self.cooling_period_night)
                else:
                    self.log("Printing stopped (day/night)", level="DEBUG")
                    self.wait_for_power_off(self.cooling_period_day)
        else:
            self.log(f"unknown state: {new}")

    def power_off(self, kwargs):
        self.log("Cooldown period ended. Powering off")
        self.turn_off(self.switch)

    def wait_for_power_off(self, cooling_period):
        self.log("Idle/paused  - setting off timer", level="DEBUG")
        self.timer = self.run_in(self.power_off, cooling_period*60)
