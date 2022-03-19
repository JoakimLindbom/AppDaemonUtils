import hassapi as hass
from follow import followers
import globals as g
from globals import *

class Follower(hass.Hass):
    """
    Utility to allow one or several lights to follow another light.
    On/off, brightness and colour temperature changes are supported

    Configuration expected in apps.yaml:
    lights:
      module: lights
      class: Follower
      origin: light.kitchen_roof
      targets:
        - light.kitchen_sideboard
        - light.kitchen_workbench_lights
    """
    def initialize(self):
        self.set_log_level("DEBUG")
        self.follow = followers()

        try:
            self.origin = self.args["origin"]

            self.log("Lights - follower - initiated")
            self.log(f"--- Origin: {self.origin}")
        except KeyError:
            self.log("Missing parameter (origin) in apps.yaml file. Cannot continue")
        else:
            try:
                for t in self.args["targets"]:
                    self.log(f"--- Target: {t}", level="DEBUG")
                    self.target = t
                    self.follow.add_follower(t, self.origin)

                self.listen_state(self.on_off_handler, self.origin)
                self.enitity = self.get_entity(self.origin)
                self.enitity.listen_state(self.brightness_handler, attribute="brightness")
                self.enitity.listen_state(self.colour_handler, attribute="color_temp")

            except KeyError:
                self.log("Missing parameter (targets) in apps.yaml file. Cannot continue")

    def on_off_handler(self, entity, attribute, old, new, kwargs):
        self.log(f"OnOff {entity} - {attribute} - {old} - {new}", level="DEBUG")
        for t in self.follow.get_followers(self.origin):
            if new == ON:
                brightness = self.get_state(self.origin, attribute="brightness")
                self.turn_on(t, brightness=brightness)
            elif new == OFF:
                self.turn_off(t)

    def brightness_handler(self, entity, attribute, old, new, kwargs):
        self.log(f"Brightness {entity} - {attribute} - {old} - {new}", level="DEBUG")
        for t in self.follow.get_followers(self.origin):
            brightness = self.get_state(self.origin, attribute="brightness")
            self.turn_on(t, brightness=brightness)

    def colour_handler(self, entity, attribute, old, new, kwargs):
        self.log(f"Colour {entity} - {attribute} - {old} - {new}", level="DEBUG")
        for t in self.follow.get_followers(self.origin):
            self.turn_on(t, color_temp=new)
