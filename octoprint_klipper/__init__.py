# coding=utf-8
from __future__ import absolute_import
import datetime
import logging
import octoprint.plugin
import octoprint.plugin.core
from octoprint.util.comm import parse_firmware_line
import flask

class KlipperPlugin(
      octoprint.plugin.StartupPlugin,
      octoprint.plugin.TemplatePlugin,
      octoprint.plugin.SettingsPlugin,
      octoprint.plugin.AssetPlugin,
      octoprint.plugin.EventHandlerPlugin):
   
   _parsingResponse = False
   _message = ""

   #-- Startup Plugin
   
   def on_after_startup(self):
      klipperPort = self._settings.get(["serialport"])
      additionalPorts = self._settings.global_get(["serial", "additionalPorts"])

      if klipperPort not in additionalPorts:
          additionalPorts.append(klipperPort)
          self._settings.global_set(["serial", "additionalPorts"], additionalPorts)
          self._settings.save()
          self._logger.info("Added klipper serial port {} to list of additional ports.".format(klipperPort))

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
         probePoints=[{'x':0, 'y':0}],
         configPath="/home/pi/printer.cfg"
      )

   def on_settings_load(self):
      data = octoprint.plugin.SettingsPlugin.on_settings_load(self)
      f = open(self._settings.get(["configPath"]), "r")
      if f:
         data["config"] = f.read()
         f.close()
      else:
         self._logger.info(
            "Error: Klipper config file not found at: {}".format(self._settings.get(["configPath"]))
         )
      return data

   def on_settings_save(self, data):
      if "config" in data:
         f = open(self._settings.get(["configPath"]), "w")
         if f:
            f.write(data["config"])
            f.close()
            self._logger.info(
               "Write Klipper config to {}".format(self._settings.get(["configPath"]))
            )
            # Restart klipply to reload config
            self._printer.commands("RESTART")
            self.logInfo("Reloading Klipper Configuration.")
         else:
            self._logger.info(
               "Error: Couldn't write Klipper config file: {}".format(self._settings.get(["configPath"]))
               )
         data.pop('config', None) # we dont want to write the klipper conf to the octoprint settings
      else:
         octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

   def get_settings_restricted_paths(self):
      return dict(
         admin=[
            ["serialport"],
            ["configPath"],
            ["replace_connection_panel"]
         ],
         user=[
            ["macros"],
            ["probeHeight"],
            ["probeLift"],
            ["probeSpeedXy"],
            ["probeSpeedZ"],
            ["probePoints"]
         ]
      )

   #-- Template Plugin

   def get_template_configs(self):
      return [
           dict(type="navbar", custom_bindings=True),
           dict(type="settings", custom_bindings=True),
           dict(type="generic", name="Assisted Bed Leveling", template="klipper_leveling_dialog.jinja2", custom_bindings=True),
           dict(type="generic", name="PID Tuning", template="klipper_pid_tuning_dialog.jinja2", custom_bindings=True),
           dict(type="generic", name="Coordinate Offset", template="klipper_offset_dialog.jinja2", custom_bindings=True),
           dict(type="tab", name="Klipper", template="klipper_tab_main.jinja2", suffix="_main", custom_bindings=True),
           dict(type="sidebar",
                 custom_bindings=True,
                 icon="rocket",
                 replaces= "connection" if self._settings.get_boolean(["replace_connection_panel"]) else "")
      ]
   
   #-- Asset Plugin
   
   def get_assets(self):
      return dict(
         js=["js/klipper.js",
              "js/klipper_settings.js",
              "js/klipper_leveling.js",
              "js/klipper_pid_tuning.js",
              "js/klipper_offset.js"],
         css=["css/klipper.css"],
         less=["css/klipper.less"]
      )
   
   #-- Event Handler Plugin
   
   def on_event(self, event, payload):
       if "Connecting" == event:
           self.updateStatus("info", "Connecting ...")
       elif "Connected" == event:
           self.updateStatus("info", "Connected to host")
           self.logInfo("Connected to host via {} @{}bps".format(payload["port"], payload["baudrate"]))
       elif "Disconnected" == event:
           self.updateStatus("info", "Disconnected from host")
       elif "Error" == event:
           self.updateStatus("error", "Error")
           self.logError(payload["error"])
           
   #-- GCODE Hook
   
   def on_parse_gcode(self, comm, line, *args, **kwargs):
      if "FIRMWARE_VERSION" in line:
         printerInfo = parse_firmware_line(line)
         if "FIRMWARE_VERSION" in printerInfo:
             self.logInfo("Firmware version: {}".format(printerInfo["FIRMWARE_VERSION"]))
      elif "//" in line:
         self._message = self._message + line.strip('/')
         if not self._parsingResponse:
            self.updateStatus("info", self._message)
         self._parsingResponse = True
      else:
         if self._parsingResponse:
            self._parsingResponse = False
            self.logInfo(self._message)
            self._message = ""
         if "!!" in line:
            msg = line.strip('!')
            self.updateStatus("error", msg)
            self.logError(msg)
      return line

   #-- Helpers
   def sendMessage(self, type, subtype, payload):
       self._plugin_manager.send_plugin_message(
                self._identifier,
                dict(
                        time=datetime.datetime.now().strftime("%H:%M:%S"),
                        type=type, payload=payload)
                    )     
   
   def pollStatus(self):
       self._printer.commands("STATUS")
       
   def updateStatus(self, type, status):
       self.sendMessage("status", type, status)
   
   def logInfo(self, message):
       self.sendMessage("log", "info", message)

   def logError(self, error):
       self.sendMessage("log", "error", error)




__plugin_name__ = "Klipper"

def __plugin_load__():
   global __plugin_implementation__
   global __plugin_hooks__
      
   __plugin_implementation__ = KlipperPlugin()
   __plugin_hooks__ = {
      "octoprint.comm.protocol.gcode.received": __plugin_implementation__.on_parse_gcode
   }

