# coding=utf-8
from __future__ import absolute_import
import datetime
import logging
import octoprint.plugin
import octoprint.plugin.core

class KlipperPlugin(
      octoprint.plugin.StartupPlugin,
      octoprint.plugin.TemplatePlugin,
      octoprint.plugin.SettingsPlugin,
      octoprint.plugin.AssetPlugin):
   
   _parsingReturn = False
   _message = ""
   
   #-- Startupt Plugin
   
   def on_after_startup(self):
      klipperPort = self._settings.get(["serialport"])
      additionalPorts = self._settings.global_get(["serial", "additionalPorts"])

      if klipperPort not in additionalPorts:
          additionalPorts.append(klipperPort)
          self._settings.global_set(["serial", "additionalPorts"], additionalPorts)
          self._settings.save()
          self._logger.info("Added klipper serial port (%s) to list of additional ports." % klipperPort)

   #-- Settings Plugin
      
   def get_settings_defaults(self):
      return dict(
         serialport="/tmp/printer",
         replace_connection_panel=True,
         macros=[{'name':"E-Stop", 'macro':"M112", 'sidebar':True, 'tab':True}],
         probeHeight=0,
         probeLift=5,
         probeSpeedXy=1500,
         probeSpeedZ=500,
         probePoints=[{'x':0, 'y':0}])
         
   #-- Template Plugin
   
   def get_template_configs(self):
      return [
#           dict(type="navbar", custom_bindings=True),
           dict(type="settings", custom_bindings=True),
           dict(type="generic", name="Assisted Bed Leveling", template="klipper_leveling_dialog.jinja2", custom_bindings=True),
           dict(type="generic", name="PID Tuning", template="klipper_pid_tuning_dialog.jinja2", custom_bindings=True),           
           dict(type="tab", name="Klipper", template="klipper_tab_main.jinja2", suffix="_main", custom_bindings=True),
           dict(type="sidebar",
                 custom_bindings=True,
                 replaces= "connection" if self._settings.get_boolean(["replace_connection_panel"]) else "")
      ]
   
   #-- Asset Plugin
   
   def get_assets(self):
      return dict(
         js=["js/klipper.js",
              "js/klipper_settings.js",
              "js/klipper_leveling.js",
              "js/klipper_pid_tuning.js"],
         css=["css/klipper.css"],
         less=["css/klipper.less"]
      )
   
   #-- GCODE Hook
   
   def on_parse_gcode(self, comm, line, *args, **kwargs):
      if "//" in line:
         self._parsingReturn = True
         self._message = self._message + line.strip('/')
      else:
         if self._parsingReturn:
             self._parsingReturn = False
             self.logInfo(self.message)
             self._message = ""
         if "!!" in line:
             self.logError(line.strip('!'))
      return line
   
   
   #-- Helpers
   
   
   def logInfo(self, message):
       self._plugin_manager.send_plugin_message(
                self._identifier,
                dict(
                        time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        type="info", message=message)
                    )
   
   def logError(self, error):
       self._plugin_manager.send_plugin_message(
               self._identifier,
               dict(
                       time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                       type="error",
                       message=error)
                    )





__plugin_name__ = "Klipper"

def __plugin_load__():
   global __plugin_implementation__
   global __plugin_hooks__
      
   __plugin_implementation__ = KlipperPlugin()
   __plugin_hooks__ = {
      "octoprint.comm.protocol.gcode.received": __plugin_implementation__.on_parse_gcode,
   }

