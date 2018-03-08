# coding=utf-8
from __future__ import absolute_import
import datetime
import logging
import octoprint.plugin
import octoprint.plugin.core
from octoprint.util.comm import parse_firmware_line

class KlipperPlugin(
      octoprint.plugin.StartupPlugin,
      octoprint.plugin.TemplatePlugin,
      octoprint.plugin.SettingsPlugin,
      octoprint.plugin.AssetPlugin,
      octoprint.plugin.EventHandlerPlugin):
   
   _parsingResponse = False
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
           dict(type="navbar", custom_bindings=True),
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
   
   #-- Event Handler Plugin
   
   def on_event(self, event, payload):
       if "Connecting" == event:
           self.updateStatus("info", "Connecting ...")
       elif "Connected" == event:
           self.updateStatus("info", "Connected to host")
           self.logInfo("Connected to host via %s @%sbps" % (payload["port"], payload["baudrate"]))
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
             self.logInfo("Firmware version: %s" % printerInfo["FIRMWARE_VERSION"])
             
      elif "//" in line:
         self._parsingResponse = True
         self._message = self._message + line.strip('/')
         
      else:
         if self._parsingResponse:
             self._parsingResponse = False
             self.logInfo(self._message)
             self._message = ""
             
         if "!!" in line:
             msg = line.strip('!')
             self.updateStatus("error", "Error")
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
       self.sendMessage("log", "error", message)




__plugin_name__ = "Klipper"

def __plugin_load__():
   global __plugin_implementation__
   global __plugin_hooks__
      
   __plugin_implementation__ = KlipperPlugin()
   __plugin_hooks__ = {
      "octoprint.comm.protocol.gcode.received": __plugin_implementation__.on_parse_gcode
   }

