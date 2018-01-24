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
      octoprint.plugin.AssetPlugin,
      octoprint.plugin.WizardPlugin):
   
   def on_after_startup(self):
      pass
      #self._logger.info("startup hook ---------- {value} ----------".format(value=self._settings.get(["replace_connection_panel"])) )
      #self._settings.set(["appearance"]["components"]["order"]["sidebar"]["test"])
      
   def get_settings_defaults(self):
      return dict(
         serialport="/tmp/printer",
         replace_connection_panel=True,
         macros=[{'name':"Echo", 'macro':"ECHO", 'sidebar':True, 'tab':True}],
         probeHeight=0,
         probeLift=5,
         probeSpeedXy=1500,
         probeSpeedZ=500,
         probePoints=[{'x':0, 'y':0}])
       
   def get_template_configs(self):
      return [
           dict(type="navbar", custom_bindings=True),
           dict(type="settings", custom_bindings=True),
           dict(type="generic", name="Assisted Bed Leveling", template="klipper_leveling_dialog.jinja2", custom_bindings=True),
           dict(type="generic", name="PID Tuning", template="klipper_pid_tuning_dialog.jinja2", custom_bindings=True),           
           dict(type="tab", name="Klipper", template="klipper_tab_main.jinja2", suffix="_main", custom_bindings=True),
           dict(type="sidebar",
                 custom_bindings=True,
                 replaces= "connection" if self._settings.get(["replace_connection_panel"]) else "")
      ]
   
   def get_assets(self):
      return dict(
         js=["js/klipper.js",
              "js/klipper_settings.js",
              "js/klipper_leveling.js",
              "js/klipper_pid_tuning.js"],
         css=["css/klipper.css"],
         less=["css/klipper.less"]
      )
   
   parsingReturn = False
   message = ""
   
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
       
   def on_parse_gcode(self, comm, line, *args, **kwargs):
      if "//" in line:
         self.parsingReturn = True
         self.message = self.message + line.strip('/')
      else:
         if self.parsingReturn:
             self.parsingReturn = False
             self.logInfo(self.message)
             self.message = ""
         if "!!" in line:
             self.logError(line.strip('!'))
      return line
   
   def on_printer_action(self, comm, line, action, *args, **kwargs):
      #if not action == "custom":
      #    return
      self._plugin_manager.send_plugin_message(self._identifier, dict(message=line))
      self._plugin_manager.send_plugin_message(self._identifier, dict(message=action))
      #self._logger.info("action recieved:".action)
      
   def is_wizard_required(self):
       return True;

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

