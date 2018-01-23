$(function() {
    function KlipperViewModel(parameters) {
        var self = this;
        // injection settingsViewModel
        self.settings = parameters[0];
        // injection loginStateViewModel
        self.loginState = parameters[1];
        // injection connectionViewModel
        self.connectionState = parameters[2];
        
        self.shortStatus = ko.observable();
        
        self.logMessages = ko.observableArray();
        /*
        self.onConnectToHost = function() {
           console.log("Connecting");
           self.shortStatus("Connecting to Host");
           OctoPrint.connection.connect({"port" : "VIRTUAL"});
           self.connectButtonText("Disconnect");
           console.log(self.loginState);
        }*/
        
        self.onGetStatus = function() {
           self.shortStatus("Update Status")
        }
        
        self.onRestartFirmware = function() {
            //OctoPrint.control.sendGcode("FIRMWARE_RESTART")
           self.shortStatus("Restarting Firmware");
           console.log("Restart firmware");
        };
        
        self.onRestartHost = function() {
           
           self.shortStatus("Restarting Host");
           console.log("Restart Host");
           self.logMessage("Restarted Host");
            //OctoPrint.control.sendGcode("RESTART")
        };
        
        self.onBeforeBinding = function() {
           self.connectionState.selectedPort("VIRTUAL");
        }
        
        self.onAfterBinding = function() {
           self.connectionState.selectedPort("VIRTUAL");
           console.log(self.connectionState.selectedPort());
           self.shortStatus("Idle");
        }
        
        self.onDataUpdaterPluginMessage = function(plugin, message) {
           //console.log(message);
           self.logMessage("plugin: " +plugin+ " message recieved: " + message["message"]);
        }

        self.logMessage = function(message) {
           self.logMessages.push({time: Date.now(), msg: message});
        }
        
        self.onClearLog = function() {
           self.logMessages.removeAll();
        };
        
        self.isActive = function() {
           return self.connectionState.isOperational() && self.loginState.isUser();
        }
        
        // ------------ Settings ---------------- //
        
        self.moveItemDown = function(list, item) {
           var i = list().indexOf(item);
           if (i < list().length - 1) {
               var rawList = list();
              list.splice(i, 2, rawList[i + 1], rawList[i]);
           }
        }
        
        self.moveItemUp = function(list, item) {
           var i = list().indexOf(item);
           if (i > 0) {
              var rawList = list();
              list.splice(i-1, 2, rawList[i], rawList[i-1]);
           }
        }

        self.executeMacro = function(macro) {
           console.log(macro.name());
           OctoPrint.control.sendGcode(macro.macro());
        }
                
        self.addMacro = function() {
           self.settings.settings.plugins.klipper.macros.push({name: 'Macro', macro: ''});
        }
        
        self.removeMacro = function(macro) {
           self.settings.settings.plugins.klipper.macros.remove(macro);
        }
        
        self.moveMacroUp = function(macro) {
           self.moveItemUp(self.settings.settings.plugins.klipper.macros, macro)
        }
                
        self.moveMacroDown = function(macro) {
           self.moveItemDown(self.settings.settings.plugins.klipper.macros, macro)
        }
        
        
        
        self.addProbePoint = function() {
           self.settings.settings.plugins.klipper.probePoints.push({x: 0, y:0, z:0});
        }
        
        self.removeProbePoint = function(point) {
           self.settings.settings.plugins.klipper.probePoints.remove(point);
        }
        
        self.moveProbePointUp = function(macro) {
           self.moveItemUp(self.settings.settings.plugins.klipper.probePoints, macro)
        }
                
        self.moveProbePointDown = function(macro) {
           self.moveItemDown(self.settings.settings.plugins.klipper.probePoints, macro)
        }
    }
   /* 
    var KlipperMacroCollection = function(name, gcode) {
        this.name = name;
        this.macros =  ko.observableArray(macros);
        
        this.addMacro = function() {
            this.push({name: 'macro 2', macro: 'G1 X1 Y2 Z3'});
        }.bind(this);
    }*/

    // This is how our plugin registers itself with the application, by adding some configuration
    // information to the global variable OCTOPRINT_VIEWMODELS
    OCTOPRINT_VIEWMODELS.push({
        // This is the constructor to call for instantiating the plugin
        construct: KlipperViewModel,

        // dependencies to inject into the plugin.
        dependencies: ["settingsViewModel", "loginStateViewModel", "connectionViewModel"],

        // elements this view model will be bound to.
        elements: ["#tab_plugin_klipper", "#sidebar_plugin_klipper", "#settings_plugin_klipper"]
    });
});