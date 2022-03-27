import appdaemon.plugins.hass.hassapi as hass
import subprocess

PACKAGES = ['wheel',
            'workalendar']


class DependencyInstaller(hass.Hass):
    def initialize(self):
        self.set_log_level("DEBUG")
        self.log("Installing packages")

        for package in PACKAGES:
            self.log("--- Installing {}".format(package))
            self.install(package)

        self.stop_app(self.name)

    def install(self, package):
        subprocess.call(['pip3', 'install', package])
