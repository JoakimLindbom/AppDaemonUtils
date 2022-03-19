import hassapi as hass
import time


class Power4Mediaplayer(hass.Hass):
    """
    Utility to control media players/amplifiers and power off when the music has ended
    Optionally power off also when a person is leaving the home

    Expected configuration in apps.yaml:
    mediaplayer_aca_power:
      module: mediaplayer_power
      class: Power4Mediaplayer
      player: media_player.my_media_player
      switch: switch.my_power_amplifier_switch
      person: person.me_myself_and_I
    """

    def initialize(self):
        self.timer = None

        try:
            self.player = self.args["player"]
            self.switch = self.args["switch"]
            try:
                self.person = self.args["person"]
            except KeyError:
                self.person = None

            self.log("Mediaplayer power controller initiated")
            self.log(f"--- Player: {self.player}")
            self.log(f"--- Switch: {self.switch}")
            self.log(f"--- Person: {self.person}")

            self.listen_state(self.state_changed, self.player)
            if self.person is not None:
                self.log("Adding person tracker")
                self.listen_state(self.state_changed_person, self.person)

            handle = self.run_daily(self.good_night, "23:05:00")

            # self.playing()
            # self.announce2(self.player, "Just testing if this works as it should", 0.80)

        except KeyError:
            self.log("Missing parameters in apps.yaml file. Cannot continue")


    def state_changed(self, entity, attribute, old, new, kwargs):
        self.log("Playing - state_change detected", level="DEBUG")

        if new.lower() == "playing":
            self.playing()
        elif new.lower() == "idle":
            self.wait_for_power_off()
        elif new.lower() == "paused":
            self.wait_for_power_off()
        else:
            self.log("unknown state: {0}".format(new))

    def state_changed_person(self, entity, attribute, old, new, kwargs):
        self.log("Playing - state_change_person detected", level="DEBUG")

        if new.lower() == "home":
            if self.now_is_between("15:00:00", "22:00:00"):
                self.playing()
                self.announce(self.player, "Just testing if this works as it should")
        elif new.lower() == "not_home":
            self.power_off()
        else:
            self.log(f"unknown state: {new}")

    def playing(self):
        self.log("Playing - detected", level="DEBUG")

        if self.timer is not None:
            self.cancel_timer(self.timer)
            self.timer = None

        self.turn_on(self.switch)

    def stopped_playing(self, kwargs):  # callback - needs to have kwargs
        self.log("Playing  - timer expired - power off", level="DEBUG")
        self.power_off()

    def power_off(self):
        self.turn_off(self.switch)

    def wait_for_power_off(self):
        self.log("Idle/paused  - setting off timer", level="DEBUG")
        self.timer = self.run_in(self.stopped_playing, 60)

    def good_night(self, kwargs):
        self.log("Playing  - power down at night ", level="DEBUG")
        self.turn_off(self.switch)

    def announce(self, player, text):
        self.call_service("tts/google_translate_say", entity_id=player, message=text)
        self.log(f"Just announced to {player }: {text}")

    def announce2(self, player, text, volume):
        try:
            volume_save = self.get_state(player, attribute="volume_level")

            # Turn on Google and Set to the desired volume
            self.call_service("media_player/turn_on", entity_id=player)
            self.call_service("media_player/volume_set", entity_id=player, volume_level=volume)

            self.call_service("tts/google_translate_say", entity_id=player, message=text)

            #self.log("Now sleeping")
            time.sleep(10 + 3)

            if volume_save is not None:
                self.call_service("media_player/volume_set", entity_id=player, volume_level=volume_save)  # Restore volume

            # Set state locally as well to avoid race condition
            # self.set_state(player, attributes={"volume_level": volume})

        except:
            self.log("announce2 - Error")
            # self.log(sys.exc_info())
