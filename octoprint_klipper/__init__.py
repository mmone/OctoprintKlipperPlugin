# coding=utf-8
# OctoPrint Klipper Plugin
#
# Copyright (C) 2018  Martin Muehlhaeuser <github@mmone.de>
#
# This file may be distributed under the terms of the GNU GPLv3 license.

from __future__ import absolute_import
import datetime
import logging
import octoprint.plugin
import octoprint.plugin.core
import glob
import os
from octoprint.util.comm import parse_firmware_line
from .modules import KlipperLogAnalyzer
import flask

class KlipperPlugin(
      octoprint.plugin.StartupPlugin,
      octoprint.plugin.TemplatePlugin,
      octoprint.plugin.SettingsPlugin,
      octoprint.plugin.AssetPlugin,
      octoprint.plugin.SimpleApiPlugin,
      octoprint.plugin.EventHandlerPlugin):
   
   _parsing_response = False
   _message = ""

   #-- Startup Plugin
   
   def on_after_startup(self):
      klipper_port = self._settings.get(["connection", "port"])
      additional_ports = self._settings.global_get(["serial", "additionalPorts"])

      if klipper_port not in additional_ports:
          additional_ports.append(klipper_port)
          self._settings.global_set(["serial", "additionalPorts"], additional_ports)
          self._settings.save()
          self._logger.info("Added klipper serial port {} to list of additional ports.".format(klipper_port))

   #-- Settings Plugin

   def get_settings_defaults(self):
      return dict(
         connection = dict(
            port="/tmp/printer",
            replace_connection_panel=True
         ),
         macros = [dict(
            name="E-Stop",
            macro="M112",
            sidebar=True,
            tab=True
         )],
         probe = dict(
            height=0,
            lift=5,
            speed_xy=1500,
            speed_z=500,
            points=[dict(
               name="point-1",
               x=0,
               y=0
            )]
         ),
         configuration = dict(
            path="~/printer.cfg",
            reload_command="RESTART"
         )
      )
   
   def on_settings_load(self):
      data = octoprint.plugin.SettingsPlugin.on_settings_load(self)
      
      filepath = os.path.expanduser(
         self._settings.get(["configuration", "path"])
      )
      try:
         f = open(filepath, "r")
         data["config"] = f.read()
         f.close()
      except IOError:
         self._logger.error(
            "Error: Klipper config file not found at: {}".format(filepath)
         )
      return data

   def on_settings_save(self, data):
      if "config" in data:
         try:
            filepath = os.path.expanduser(
               self._settings.get(["configuration", "path"])
            )
            f = open(filepath, "w")
            f.write(data["config"])
            f.close()
            self._logger.info(
               "Writing Klipper config to {}".format(filepath)
            )
            # Restart klipply to reload config
            self._printer.commands(self._settings.get(["configuration", "reload_command"]))
            self.logInfo("Reloading Klipper Configuration.")
         except IOError:
            self._logger.error(
               "Error: Couldn't write Klipper config file: {}".format(filepath)
            )
         data.pop("config", None) # we dont want to write the klipper conf to the octoprint settings
      else:
         octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

   def get_settings_restricted_paths(self):
      return dict(
         admin=[
            ["connection", "port"],
            ["configuration", "path"],
            ["configuration", "replace_connection_panel"]
         ],
         user=[
            ["macros"],
            ["probe"]
         ]
      )

   def get_settings_version(self):
      return 2

   def on_settings_migrate(self, target, current):
      if current is None:
         settings = self._settings
         
         if settings.has(["serialport"]):
            settings.set(["connection", "port"], settings.get(["serialport"]) )
            settings.remove(["serialport"])

         if settings.has(["replace_connection_panel"]):
            settings.set(
               ["connection", "replace_connection_panel"],
               settings.get(["replace_connection_panel"])
            )
            settings.remove(["replace_connection_panel"])

         if settings.has(["probeHeight"]):
            settings.set(["probe", "height"], settings.get(["probeHeight"]))
            settings.remove(["probeHeight"])
         
         if settings.has(["probeLift"]):
            settings.set(["probe", "lift"], settings.get(["probeLift"]))
            settings.remove(["probeLift"])
         
         if settings.has(["probeSpeedXy"]):
            settings.set(["probe", "speed_xy"], settings.get(["probeSpeedXy"]))
            settings.remove(["probeSpeedXy"])
         
         if settings.has(["probeSpeedZ"]):
            settings.set(["probe", "speed_z"], settings.get(["probeSpeedZ"]))
            settings.remove(["probeSpeedZ"])
            
         if settings.has(["probePoints"]):
            points = settings.get(["probePoints"])
            points_new = []
            for p in points:
               points_new.append(dict(name="", x=int(p["x"]), y=int(p["y"]), z=0))
            settings.set(["probe", "points"], points_new)
            settings.remove(["probePoints"])

         if settings.has(["configPath"]):
            settings.set(["config_path"], settings.get(["configPath"]))
            settings.remove(["configPath"])
         
   #-- Template Plugin

   def get_template_configs(self):
      return [
         dict(type="navbar", custom_bindings=True),
         dict(type="settings", custom_bindings=True),
         dict(
            type="generic",
            name="Assisted Bed Leveling",
            template="klipper_leveling_dialog.jinja2",
            custom_bindings=True
         ),
         dict(
            type="generic",
            name="PID Tuning",
            template="klipper_pid_tuning_dialog.jinja2",
            custom_bindings=True
         ),
         dict(
            type="generic",
            name="Coordinate Offset",
            template="klipper_offset_dialog.jinja2",
            custom_bindings=True
         ),
         dict(
            type="tab",
            name="Klipper",
            template="klipper_tab_main.jinja2",
            suffix="_main",
            custom_bindings=True
         ),
         dict(type="sidebar",
            custom_bindings=True,
            icon="rocket",
            replaces= "connection" if self._settings.get_boolean(["connection", "replace_connection_panel"]) else ""
         ),
         dict(
            type="generic",
            name="Performance Graph",
            template="klipper_graph_dialog.jinja2",
            custom_bindings=True
         ),
         dict(
            type="generic",
            name="Macro Dialog",
            template="klipper_param_macro_dialog.jinja2",
            custom_bindings=True
         )
      ]
   
   #-- Asset Plugin
   
   def get_assets(self):
      return dict(
         js=["js/klipper.js",
             "js/klipper_settings.js",
             "js/klipper_leveling.js",
             "js/klipper_pid_tuning.js",
             "js/klipper_offset.js",
             "js/klipper_param_macro.js",
             "js/klipper_graph.js"
         ],
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
         if not self._parsing_response:
            self.updateStatus("info", self._message)
         self._parsing_response = True
      else:
         if self._parsing_response:
            self._parsing_response = False
            self.logInfo(self._message)
            self._message = ""
         if "!!" in line:
            msg = line.strip('!')
            self.updateStatus("error", msg)
            self.logError(msg)
      return line

   def get_api_commands(self):
      return dict(
         listLogFiles=[],
         getStats=["logFile"],
         loadConfig=["configFile"]
      )
      
   def on_api_command(self, command, data):
      if command == "listLogFiles":
         files = []
         for f in glob.glob("/tmp/*.log*"):
            filesize = os.path.getsize(f)
            files.append(dict(
               name=os.path.basename(f) + " ({:.1f} KB)".format(filesize / 1000.0),
               file=f,
               size=filesize
            ))
         return flask.jsonify(data=files)
      elif command == "getStats":
         if "logFile" in data:
            log_analyzer = KlipperLogAnalyzer.KlipperLogAnalyzer(data["logFile"])
            return flask.jsonify(log_analyzer.analyze())
      elif command == "loadConfig":
         kc = Parser()
         sections = kc.load(data["configFile"])
         return flask.jsonify(sections)

   def get_update_information(self):
      return dict(
         klipper=dict(
            displayName=self._plugin_name,
            displayVersion=self._plugin_version,
            type="github_release",
            current=self._plugin_version,
            user="mmone",
            repo="OctoprintKlipperPlugin",
            pip="https://github.com/mmone/OctoPrintKlipper/archive/{target_version}.zip"
         )
      )
    
   #-- Helpers
   def sendMessage(self, type, subtype, payload):
      self._plugin_manager.send_plugin_message(
         self._identifier,
         dict(
            time=datetime.datetime.now().strftime("%H:%M:%S"),
            type=type,
            subtype=subtype,
            payload=payload
         )
      )
   
   def pollStatus(self):
      self._printer.commands("STATUS")

   def updateStatus(self, type, status):
      self.sendMessage("status", type, status)
   
   def logInfo(self, message):
      self.sendMessage("log", "info", message)

   def logError(self, error):
      self.sendMessage("log", "error", error)

def __plugin_load__():
   global __plugin_implementation__
   global __plugin_hooks__

   __plugin_implementation__ = KlipperPlugin()
   __plugin_hooks__ = {
      "octoprint.comm.protocol.gcode.received": __plugin_implementation__.on_parse_gcode,
      "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
   }

