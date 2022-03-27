#import appdaemon.appapi as appapi
import appdaemon.plugins.hass.hassapi as hass
import subprocess

PACKAGES = ['wheel',
            'workalendar']


#class DependencyInstaller(appapi.AppDaemon):
class DependencyInstaller(hass.Hass):
    def initialize(self):
        self.set_log_level("DEBUG")
        self.log("Installing packages")

        for package in PACKAGES:
            self.log("--- Installing {}".format(package))
            self.install(package)

    def install(self, package):
        # https://github.com/pypa/pip/issues/2553
        subprocess.call(['pip3', 'install', package])
