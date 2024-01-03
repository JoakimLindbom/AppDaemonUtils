#################
#
# Global constants and Ids
#
#TODO: Update with new input_selects

import hassapi as hass

FADE = "fade"
ON = "on"
OFF = "off"

#Family states
test123 = "testabc"
WORKING = "Working"
NON_WORKING = "Non_working"
VACATION = "Vacation (away)"
family_state_sensor = "input_select.family_mode"  # TODO: Get from apps.yaml in __init__ ??

class globals (hass.Hass):
    test321 = "test321"
    def initialize(self):
        pass
