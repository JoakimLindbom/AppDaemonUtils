#################################################################
AGO_WEATHERREPORTER_VERSION = '0.0.3'
"""
Weather reporing support for AppDaemon
Uploading temperature to crowd sourced weather data sites

"""
__author__     = "Joakim Lindbom"
__copyright__  = "Copyright 2014-2022, Joakim Lindbom"
__date__       = "2020-12-28"
__credits__    = ["Joakim Lindbom"]
__license__    = "GPL Public License Version 3"
__maintainer__ = "Joakim Lindbom"
__email__      = 'Joakim.Lindbom@gmail.com'
__status__     = "Experimental"
#################################################################

# TODO: Check value to be numeric before sending
# TODO: Add humidity

import hassapi as hass
import threading
import requests


class temperaturnu(hass.Hass):
    """
    Utility to send temperature data to temperatur.nu

    Expected configuration in apps.yaml:
    temperatur_nu_logger:
      module: temperaturnu
      class: temperaturnu
      tnhash: my_very_secret_hash
      sensor: sensor.my_temperature_sensor
    """

    def initialize(self):
        self.set_log_level("INFO")

        self.timer = None
        self.l = False

        self.TN_hash = self.args["tnhash"]
        self.sensor1 = self.args["sensor"]

        self.log("Temperatur.nu logger initiated")
        self.log("--- Sensor: {0}".format(self.TN_hash))
        self.log("--- hash: {0}".format(self.sensor1))

        self.listen_state(self.state_changed, self.sensor1)
        self.temperaturenu_lock = threading.Lock()

    def state_changed(self, entity, attribute, old, new, kwargs):
        self.log(f"State_change detected. New state: {new}", level="DEBUG")
        self.sendTemperaturNu(new, self.TN_hash)

    def sendTimer(self, kwargs):
        self.sendTemperaturNu(kwargs["temp"], kwargs["reporthash"])

    def sendTemperaturNu(self, temp, reporthash):
        """ Send temperature data to http://temperatur.nu
        """
        if self.timer != None:
            self.cancel_timer(self.timer)
        self.timer = self.run_in(self.sendTimer, 600, temp=temp, reporthash=reporthash) # kwargs


        self.log(f"temperatur.nu reporting temp={temp} {str(temp)} for hash={reporthash}", level="DEBUG")

        # Critical section, don't want two of these running at the same time
        with self.temperaturenu_lock:
            r = requests.get('http://www.temperatur.nu/rapportera.php?hash=' + reporthash + '&t=' + str(temp))

            if r.status_code == 200 and "ok! (" in r.text and len(r.text) > 6:
                self.log("OK from temperatur.nu", level="DEBUG")
                #self.log(r.text)
                return True
            else:
                self.log("Something went wrong when reporting. response={}".format(r.text))
                self.log("Full response object={}".format(r))
                return False
