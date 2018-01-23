# coding=utf-8
from __future__ import absolute_import
import logging
import octoprint.plugin
import octoprint.plugin.core

class KlipperPlugin(
      octoprint.plugin.StartupPlugin,
      octoprint.plugin.TemplatePlugin,
      octoprint.plugin.SettingsPlugin,
      octoprint.plugin.AssetPlugin):
   
   def on_after_startup(self):
      #self._settings.set(["appearance"]["components"]["order"]["sidebar"]["test"]);
      self._logger.info("startup hook ---------- {value} ----------".format(value=self._settings.get(["replace_connection_panel"])) )   
   
   def get_settings_defaults(self):
      return dict(
         serialport="/tmp/printer",
         replace_connection_panel=True,
         macros=[],
         probePoints=[])
       
   def get_template_configs(self):
      return [
           dict(type="navbar", custom_bindings=False),
           dict(type="settings", custom_bindings=True),
           dict(type="sidebar",
                 custom_bindings=True,
                 replaces= "connection" if self._settings.get(["replace_connection_panel"]) else "")
      ]
   
   def get_assets(self):
      return dict(
         js=["js/klipper.js"],
         css=["css/klipper.css"],
         less=["css/klipper.less"]
      )

   def on_parse_gcode(self, comm, line, *args, **kwargs):
      if "ok" not in line:
         return line
         
      self._plugin_manager.send_plugin_message(self._identifier, dict(message=line))
      #from octoprint.util.comm import parse_firmware_line
      
      # Create a dict with all the keys/values returned by the M115 request
      #printer_data = parse_firmware_line(line)
      self._logger.info("Machine type detected {line}.".format(line=line))
      #self._logger.info("Machine type detected: {machine}.".format(machine=printer_data["MACHINE_TYPE"]))
      
      return line
   
   def on_printer_action(self, comm, line, action, *args, **kwargs):
      #if not action == "custom":
      #    return
      
      self._logger.info("action recieved:".action)

__plugin_name__ = "Klipper"

def __plugin_load__():
   global __plugin_implementation__
   global __plugin_hooks__
      
   __plugin_implementation__ = KlipperPlugin()
   __plugin_hooks__ = {
      "octoprint.comm.protocol.gcode.received": __plugin_implementation__.on_parse_gcode,
      "octoprint.comm.protocol.action": __plugin_implementation__.on_printer_action
   }

#__plugin_name__ = "Klipper"
#__plugin_implementation__ = KlipperPlugin()

