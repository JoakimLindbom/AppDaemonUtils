#     raise self._exception
#   File "/usr/lib/python3.9/site-packages/appdaemon/adapi.py", line 2593, in run_daily
#     handle = await self.run_every(callback, event, 24 * 60 * 60, **kwargs)
#   File "/usr/lib/python3.9/site-packages/appdaemon/adapi.py", line 2768, in run_every
#     handle = await self.AD.sched.insert_schedule(
#   File "/usr/lib/python3.9/site-packages/appdaemon/scheduler.py", line 314, in insert_schedule
#     pin_app = self.AD.ap


import hassapi as hass
from utilities import Util
from utilities import remove_list_from_list
from utilities import return_list
from globals import *

lights_first = ["light.kok_lampa_sideboard", "light.vardagsrum_lampa_sideboard_vanster",
                    "light.vardagsrum_lampa_sideboard_hoger", "light.vardagsrum_lampor_20talsbyra",
                    "light.hall_byra_lampa", "light.hall_fonsterlampa", "light.kok_vaxtlampa"]
lights_windows_downstairs = ["light.hall_fonsterlampa"]
lights_inner_downstairs = ["light.kok_lampa_sideboard", "light.vardagsrum_lampa_sideboard_vanster",
                           "light.vardagsrum_lampa_sideboard_hoger", "light.vardagsrum_lampor_20talsbyra",
                           "light.hall_byra_lampa"]
lights_early = ["light.kok_lampa_sideboard", "light.vardagsrum_lampa_sideboard_vanster",
                    "light.vardagsrum_lampa_sideboard_hoger", "light.vardagsrum_lampor_20talsbyra",
                    "light.hall_byra_lampa", "light.hall_fonsterlampa", "light.vardagsrum_lampa_sideboard_vanster",
                    "light.vardagsrum_lampa_sideboard_hoger", "light.kok_vaxtlampa"]
lights_all = ["light.kok_lampa_sideboard", "light.vardagsrum_lampa_sideboard_vanster",
              "light.vardagsrum_lampa_sideboard_hoger", "light.vardagsrum_lampor_20talsbyra", "light.hall_byra_lampa",
              "light.hall_fonsterlampa", "light.arbetsrum_fonsterlampor", "light.kok_lampa_sideboard",
              "light.vardagsrum_lampa_sideboard_vanster", "light.vardagsrum_lampa_sideboard_hoger",
              "light.vardagsrum_lampor_20talsbyra", "light.Fonsterlampa_Syd_Vardagsrum"]
lights_on_afternoon = ["light.kok_lampa_sideboard", "light.vardagsrum_lampa_sideboard_vanster",
                       "light.vardagsrum_lampa_sideboard_hoger", "light.vardagsrum_lampor_20talsbyra",
                       "light.hall_byra_lampa", "light.hall_fonsterlampa", "light.arbetsrum_fonsterlampor",
                       "light.kok_lampa_sideboard", "light.vardagsrum_lampa_sideboard_vanster",
                       "light.vardagsrum_lampa_sideboard_hoger", "light.vardagsrum_lampor_20talsbyra",
                       "light.Fonsterlampa_Syd_Vardagsrum"]
lights_off_day = ["light.alices_taklampa", "light.petters_taklampa", "light.entre_syd"]
lights_off_evening = ["light.arbetsrum_fonsterlampor", "light.kok_lampa_sideboard", "light.sonoff_switch2", "light.entre_syd"]  # "light.arbetsrum_julstjarna",
lights_panel = ["light.panel_vanster", "light.panel_hoger_2"]
lights_last_midnight = ["light.kok_vaxtlampa", "light.Fonsterlampa_Syd_Vardagsrum", "light.sonoff_switch2", "light.entre_syd"]
lights_test = ["group.paneler_skrivbord", "light.arbetsrum_fonsterlampor"]
# sensor = "binary_sensor.multisensor_6_home_security_motion_detected"

# TODO: Implement fade as a separate class, allowing several to run
# TODO: Add Lower: lower brightness if light is on, else leave it off. Also Increase

#FADE = "fade"
#ON = "on"
#OFF = "off"


class WindowLights(hass.Hass):
    # def __init__(self, ad, name, logging, args, config, app_config, global_vars):
    # f = Fader(ad, name, logging, args, config, app_config, global_vars)

    def initialize(self):
        self.handlers = []
        self.run_handles = []
        self.remote = None
        self.break_remote = None

        self.set_log_level("INFO")

        try:
            self.remote = self.args["remote"]

            self.log("Light scheduler - initiated")
            self.log("--- Remote: {0}".format(self.remote))

            self.listen_state(self.state_changed, self.remote)
        except KeyError:
            self.log("Missing parameter (remote) in apps.yaml file. Continuing with degraded functionality")

        try:
            self.break_remote = self.args["break_remote"]
            self.log("--- Break remote: {0}".format(self.break_remote))
            self.listen_state(self.break_remote_handler, self.break_remote)
        except KeyError:
            self.log("No break_remote defined")
            self.break_remote = None

        try:
            self.retry = self.args["retry"].lower() == "true"
            self.log(f"--- Retry: {self.retry}", level="DEBUG")
        except KeyError:
            self.retry = False

        try:
            self.retrytimes = self.args["retrytimes"]
            self.log(f"--- Retry times: {self.retrytimes}", level="DEBUG")
        except KeyError:
            self.retrytimes = 3

        schedule = None
        try:
            for x in self.args["schedule"]:
                self.log(f"Reading entities for {x}", level="DEBUG")
                for l in self.args["schedule"][x]:
                    self.log(f"- {l}", level="DEBUG")

        except KeyError:
            self.log("No scheduler key. Disabling scheduling.")

        if schedule is not None:
            try:
                self.lights_first = self.args["schedule", "lights_first"]
                self.log(f"{self.lights_first}")
            except KeyError:
                self.log("No scheduler key for lights_first.")

        handle = self.run_daily(self.set_schedule, "03:11:00")
        handle = self.run_in(self.set_schedule, 1)

    def get_timing_working(self):
        """
        :return: morning_first, morning_early, morning_all, morning_end1, morning_end2, afternoon based on month of the year
        """
        # TODO: Create time object - add relative time (minutes) to base time

        timings = []

        try:
            now = self.get_now()
            month = str(now.month)
            if len(str(month)) < 2:
                month = "0" + month
            self.log(f"Reading timings for month (str) {month}")
            for l in self.args["schedule"]["timings"]["working"][month]:
                timings.append(l)
        except KeyError:
            try:
                now = self.get_now()
                month = now.month
                self.log(f"Reading timings for month (int) {month}")
                for l in self.args["schedule"]["timings"]["working"][month]:
                    timings.append(l)
            except KeyError:
                self.log(f"TesterWL: No working timings key for {month}. Disabling scheduling.")
                return None

        self.log(f"Timings {timings}")

        return timings[0], timings[1], timings[2], timings[3], timings[4], timings[5]

    def get_timing_nonworking(self):
        """
        :return: morning_first, morning_early, morning_all, morning_end1, morning_end2, afternoon based on month of the year
        """
        # TODO: Create time object - add relative time (minutes) to base time

        timings = []

        try:
            now = self.get_now()
            month = str(now.month)
            if len(str(month)) < 2:
                month = "0" + month
            self.log(f"Reading timings for month (str) {month}")
            for l in self.args["schedule"]["timings"]["non-working"][month]:
                timings.append(l)
        except KeyError:
            try:
                now = self.get_now()
                month = now.month  #cast?
                self.log(f"Reading timings for month (int) {month}")
                for l in self.args["schedule"]["timings"]["non-working"][month]:
                    timings.append(l)
            except KeyError:
                self.log(f"Window-lights: No non-working timings key for {month}. Disabling scheduling.")
                return None

        self.log(f"Timings {timings}")

        return timings[0], timings[1], timings[2], timings[3], timings[4], timings[5]

    def set_schedule(self, kwargs):
        family_state = self.get_state(family_state_sensor)
        self.log(f"Family state: {family_state}", level="DEBUG")

        if family_state == WORKING:
            morning_first, morning_early, morning_all, morning_end1, morning_end2, afternoon = self.get_timing_working()
        else:
            morning_first, morning_early, morning_all, morning_end1, morning_end2, afternoon = self.get_timing_nonworking()

        self.log(
            f"Morning first {morning_first} early {morning_early} all {morning_all} end1 {morning_end1}, end2 {morning_end2}, afternoon {afternoon}",
            level="INFO")

        now = self.get_now()
        month = now.month

        self.cleanup_daily()

        if family_state == WORKING:
            self.log("Setting schedule for working (at home) day")
            # ON morning
            if month not in [1, 2, 11, 12]:  # Remove window light when not Winter/early spring
                lights_first1 = remove_list_from_list(lights_first, lights_windows_downstairs)
                lights_early1 = remove_list_from_list(lights_early, lights_windows_downstairs)
                lights_all1 = remove_list_from_list(lights_all, lights_windows_downstairs)
            else:
                lights_first1 = lights_first
                lights_early1 = lights_early
                lights_all1 = lights_all

            #--self.register_daily(ON, morning_first, lights=lights_first1)
            #--self.register_daily(ON, morning_early, lights=lights_early1)
            #--self.register_daily(ON, morning_all, lights=lights_all1)
            # self.register_daily(ON,   "07:20", lights=["light.50_talslampa"], brightness=1)
            #--if month in [1, 2, 11, 12]:  # Fall/Winter
                #--    self.register_daily(FADE, "07:50", lights=lights_panel, duration="00:20", brightness_from=1,
            #--                    brightness_to=50, steps=20, ignore_if_on=True)
            # OFF morning
            #--self.register_daily(OFF, morning_end1, lights=lights_windows_downstairs + lights_off_day)
            #--self.register_daily(OFF, morning_end2, lights=lights_inner_downstairs + lights_all)
            self.register_daily(OFF, "09:20", lights=["light.50_talslampa"])
            #self.log(f'Växtlampa: {"09:23" if month in [1, 2, 11, 12] else "07:50"}')
            #--self.register_daily(OFF, "09:23" if month in [1, 2, 11, 12] else "07:50", lights=["light.kok_vaxtlampa"])

            # self.register_daily(FADE, "08:32", lights=lights_panel, duration="00:04", brightness_from=1, brightness_to=80, steps=20, ignore_if_on=True)

            # ON afternoon
            #--self.register_daily(ON, afternoon, lights=lights_all)
            #--self.register_daily(ON, "16:02" if month in [1, 2, 11, 12] else "18:02" if month in [3, 4, 9, 10] else "21:00", lights=["light.kok_vaxtlampa"])
            #--self.register_daily(ON, "17:01" if month in [1, 2, 11, 12] else "21:00",
            #--                    lights=["light.Fonsterlampa_Syd_Vardagsrum"])
            self.register_daily(OFF, "21:30", lights=["light.50_talslampa"])
            self.register_daily(OFF, "22:55", lights=lights_off_evening)
            self.register_daily(OFF, "22:57", lights=lights_off_day)
            self.register_daily(OFF, "23:25", lights=lights_off_day)
            self.register_daily(OFF, "23:35", lights=lights_last_midnight)
            self.register_daily(OFF, "23:40", lights=lights_all)
            self.register_daily(OFF, "23:50", lights=lights_all)
        elif family_state == NON_WORKING:
            self.log("Setting schedule for non-working (at home) day")
            # ON Morning
            #--self.register_daily(ON, morning_first, lights=lights_first)
            #--self.register_daily(ON, morning_early, lights=lights_early)
            #--self.register_daily(ON, morning_all, lights=lights_all)

            # OFF Morning
            #--self.register_daily(OFF, morning_end1, lights=lights_windows_downstairs + lights_off_day)
            #--self.register_daily(OFF, morning_end2, lights=lights_inner_downstairs + lights_all)
            self.register_daily(OFF, "09:20", lights=["light.50_talslampa"])
            #self.log(f'Växtlampa: {"09:23" if month in [1, 2, 11, 12] else "07:50"}')
            #--self.register_daily(OFF, "09:23" if month in [1, 2, 11, 12] else "07:50", lights=["light.kok_vaxtlampa"])


            # OFF if manually overridden
            #--self.register_daily(OFF, "11:00", lights=lights_all)
            #--self.register_daily(OFF, "11:05", lights=lights_off_day)

            # ON Afternoon
            #--self.register_daily(ON, afternoon, lights=lights_all)
            #--self.register_daily(ON, "16:02" if month in [1, 2, 11, 12] else "18:02" if month in [3, 4, 9, 10] else "21:00", lights=["light.kok_vaxtlampa"])
            #-- self.register_daily(ON, "17:01" if month in [1, 2, 11, 12] else "21:00",
            #--                    lights=["light.Fonsterlampa_Syd_Vardagsrum"])

            # OFF Evening
            self.register_daily(OFF, "22:15", lights=["light.50_talslampa"])
            #--self.register_daily(OFF, "22:55", lights=lights_off_day)
            #--self.register_daily(OFF, "23:08", lights=lights_off_day)
            #--self.register_daily(OFF, "22:30", lights=lights_off_evening)
            #--self.register_daily(OFF, "23:25", lights=lights_last_midnight)
            self.register_daily(OFF, "23:40", lights=lights_all)
            self.register_daily(OFF, "23:50", lights=lights_all)
        elif family_state == VACATION:
            self.log("Setting schedule for vacation (away) day")
            self.register_daily(ON, morning_first, random_start=-600, random_end=600, lights=lights_first)
            self.register_daily(ON, morning_early, random_start=-600, random_end=600, lights=lights_early)
            self.register_daily(ON, morning_all, random_start=-600, random_end=600, lights=lights_all)
            self.register_daily(OFF, "09:23" if month in [1, 2, 11, 12] else "08:30", random_start=-600, random_end=600,
                                                                                      lights=["light.kok_vaxtlampa"])
            self.register_daily(OFF, "10:00", random_start=-600, random_end=600, lights=lights_all)
            self.register_daily(OFF, "10:05", random_start=-600, random_end=600, lights=lights_off_day)
            # ---
            self.register_daily(ON, "16:02" if month in [1, 2, 11, 12] else "18:02" if month in [3, 4, 9, 10] else "21:00", lights=["light.kok_vaxtlampa"])
            self.register_daily(ON, "16:02" if month in [1, 2, 11, 12] else "18:02" if month in [3, 4, 9, 10] else "21:00", random_start=-300, random_end=300,
                                lights=["light.kok_vaxtlampa"])
            self.register_daily(ON, "17:01" if month in [1, 2, 11, 12] else "21:00", random_start=-300, random_end=300,
                                lights=["light.Fonsterlampa_Syd_Vardagsrum"])
            self.register_daily(ON, afternoon, random_start=-60, random_end=600, lights=lights_all)
            self.register_daily(OFF, "22:00", random_start=-150, random_end=600, lights=lights_off_evening)
            self.register_daily(OFF, "22:55", random_start=-1, random_end=600, lights=lights_off_day)
            self.register_daily(OFF, "22:40", random_start=-1, random_end=600, lights=lights_all)
            self.register_daily(OFF, "22:45", random_start=-1, random_end=600, lights=lights_last_midnight)

        # Safety
        self.register_daily(OFF, "09:35" if month in [1, 2, 11, 12] else "08:01", lights=["light.kok_vaxtlampa"])
        self.register_daily(OFF, "23:58", lights=lights_all)

    # TODO: Add global state - sleeping/good night command/scene?

    def cleanup_daily(self):
        self.log("cleanup_daily()", level="DEBUG")
        for h in self.run_handles:
            self.log(h, level="DEBUG")
            if self.info_timer(h) is not None:
                self.cancel_timer(h)
        self.run_handles = []

    def register_daily(self, action, time, lights, duration=None, brightness_from=None, brightness=None,
                       brightness_to=None, steps=None, random_start=0, random_end=0, ignore_if_on=False):
        self.log("register_daily", level="DEBUG")

        if time == "--:--":  # Skip this entry
            return

        if len(time) == 5:
            time += ":00"

        if action == FADE:
            handle = self.run_daily(self.fade, time, lights=lights, duration=duration,
                                    brightness_from=brightness_from, brightness_to=brightness_to, steps=steps,
                                    random_start=random_start, random_end=random_end, ignore_if_on=ignore_if_on)
        else:
            if brightness is not None:
                handle = self.run_daily(self.on if action == ON else self.off, time, lights=lights,
                                        random_start=random_start, random_end=random_end, brightness=brightness)
            else:
                #self.log(f"290 lights: {lights}")
                handle = self.run_daily(self.on if action == ON else self.off, time, lights=lights,
                                        random_start=random_start, random_end=random_end)

        self.run_handles.append(handle)
        self.log(f"Number of run_handles: {len(self.run_handles)}", level="DEBUG")

    def state_changed(self, entity, attribute, old, new, kwargs):
        self.log("State change - detected")
        # if new.lower() == "playing":
        self.log("new state: {}".format(new), level="DEBUG")
        # IKEA
        # 87    dim down
        # 74 dim up?

    def break_remote_handler(self, entity, attribute, old, new, kwargs):
        self.log("Break_remote change detected", level="DEBUG")
        if new == "off":
            self.cancel_fade()

    def cancel_fade(self):
        for h in self.handlers:
            self.log(h, level="DEBUG")
            if self.info_timer(h) is not None:
                self.cancel_timer(h)
        self.handlers = []

    def motion(self, entity, attribute, old, new, kwargs):
        # self.log("Motion - detected")
        if self.sun_down():
            self.log("Motion - detected - sun down", level="DEBUG")
            for light in lights_all:
                self.turn_on(light)
            # self.run_in(self.light_off, 60, light)

    def ungroup(self, group):
        # return entities within a group
        g = self.get_state(group, attribute="all")
        return 'x' in group["attributes"]["entity_id"]

    def on(self, kwargs):
        """
        Turn on one or several lights
        :param kwargs:
            brightness: 0-100 % - non-mandatory. If left out current brightness will be used
            lastbrightness: 0-100%. Used for fading to identify manual changes during a fade operation
        :return:
        """
        self.log("On: lights {0}".format(kwargs["lights"]), level="DEBUG")
        lights = return_list(kwargs["lights"])
        for light in lights:
            if "brightness" in kwargs:
                if "lastbrightness" in kwargs:
                    if len(self.handlers) > 0:
                        self.log(f"handlers.pop len={len(self.handlers)}", level="DEBUG")
                        self.handlers.pop(0)  # Remove first entry (== the one triggering this call)
                    else:
                        self.log(f"handlers.pop cannot run. len={len(self.handlers)}")
                    last = self.get_state(light, attribute="brightness")
                    self.log(
                        f"last={last} lastbrightness={kwargs['lastbrightness']}% expected={round(kwargs['lastbrightness'] * 255 / 100)}",
                        level="DEBUG")
                    if last != round(kwargs["lastbrightness"] * 255 / 100):
                        self.log("Someone changed the light level during fade", level="DEBUG")
                        self.cancel_fade()

                brightness = round(kwargs["brightness"] * 255 / 100)
                br = brightness if brightness <= 255 else 255

                try:
                    self.turn_on(light, brightness=br)
                except TimeoutError:
                    try:
                        self.log(f"Timeout error received in on() for {light} brightness={brightness}", level="ERROR")
                        if self.retry:
                            if "retry" in kwargs:
                                if kwargs["retry"] >= self.retrytimes:
                                    self.log(
                                        f"Retry didn't work for on() (fade). Retried {self.retrytimes} times with no effect.")
                                else:
                                    retry = kwargs["retry"]
                                    self.log(f"Retrying, #{retry}")
                                    # TODO: Verify change. lights={light} --> lights=light - seems ok 2022-03-12
                                    self.run_in(self.on, 5 + retry * 3, retry=retry + 1, lights=light,
                                                brightness=kwargs["brightness"])
                            else:
                                self.run_in(self.on, 5, retry=1, lights=light, brightness=kwargs["brightness"])
                            # TODO: Move to on() ?
                    except Exception as e:
                        self.log(f"Something else occurred in on()! for {light}. Exception {e}", level="ERROR")

                # TODO: Check if dimmable?
                actual = self.get_state(light, attribute="brightness")
                self.log(f"new expected={br} new actual={actual}", level="DEBUG")
            else:  # No brigtness in kwargs:
                try:
                    self.turn_on(light)
                except TimeoutError:
                    try:
                        self.log(f"Timeout error received in on()! for {light}", level="ERROR")
                        if self.retry:
                            if "retry" in kwargs:
                                if kwargs["retry"] >= self.retrytimes:
                                    self.log(
                                        f"Retry didn't work for on(). Retried {self.retrytimes} times with no effect.")
                                else:
                                    retry = kwargs["retry"]
                                    self.log(f"Retrying, #{retry}")
                                    self.run_in(self.on, 5 + retry * 3, retry=retry + 1, lights={light})
                            else:
                                self.run_in(self.on, 5, retry=1, lights={light})
                            # TODO: Move to on() ?
                    except:
                        self.log("Well, that didn't work - on()")

    def fade(self, kwargs):
        """
        Fade a light
        :param kwargs:
            brightness_from: 0-100 %
            brightness_to: 0-100 %
            duration: minutes for the fade operation
            steps: How many steps to fade
            ignore_if_on: Should the fade operation be ignored if the light is already on?
            lastbrightness: (hidden) 0-100%. Used for fading to identify manual intervention during a fade operation
        :return:
        """
        self.log("fade: lights {} from {} to {} duration {} steps: {} ignore: {}".format(kwargs["lights"],
                                                                                         kwargs["brightness_from"],
                                                                                         kwargs["brightness_to"],
                                                                                         kwargs["duration"],
                                                                                         kwargs["steps"],
                                                                                         kwargs["ignore_if_on"]),
                 level="DEBUG")
        lights = return_list(kwargs["lights"])
        for light in lights:
            current = self.get_state(light, attribute="brightness")
            self.log(f"current={current} brightness", level="DEBUG")
            if current is not None and current > 0 and kwargs["ignore_if_on"] is True:
                self.log(f"Lights already on, ignoring fade operation", level="INFO")
                return

        steps = kwargs["steps"] if "steps" in kwargs else 10

        util = Util()
        duration = kwargs["duration"]
        if len(duration) == 5:
            duration += ":00"
        # times, brl = Utilities.time_split(self, duration=duration, steps=steps, from_brightness=kwargs["brightness_from"], to_brightness=kwargs["brightness_to"])
        times, brl = util.time_split(duration=duration, steps=steps, from_brightness=kwargs["brightness_from"],
                                     to_brightness=kwargs["brightness_to"])

        br = kwargs["brightness_from"]
        for light in lights:
            self.turn_on(light, brightness=round(br * 255 / 100))

        for t in times:
            br0 = br
            br += round((kwargs["brightness_to"] - kwargs["brightness_from"]) / steps)
            handler = self.run_once(self.on, t.time(), lights=lights, brightness=br, lastbrightness=round(br0))
            self.log(f"time {t} brightness {br}%", level="DEBUG")
            self.handlers.append(handler)
        self.log(f"len: {len(self.handlers)}", level="DEBUG")

    def off(self, kwargs):
        self.log("Off: lights {0}".format(kwargs["lights"]), level="DEBUG")
        lights = return_list(kwargs["lights"])
        for light in lights:
            try:
                self.turn_off(light)
            except TimeoutError:
                self.log(f"Timeout error received in off()! for {light}", level="ERROR")
            except Exception as e:
                self.log(f"Something else occurred in off()! for {light}. Exception {e}", level="ERROR")
