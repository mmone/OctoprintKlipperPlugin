$(function() {
    function KlipperViewModel(parameters) {
        var self = this;

        self.settings = parameters[0];
        self.loginState = parameters[1];
        self.connectionState = parameters[2];
        
        self.shortStatus = ko.observable();
        self.logMessages = ko.observableArray();

        self.showLevelingDialog = function() {
           var dialog = $("#klipper_leveling_dialog");
           dialog.modal({
                show: 'true',
                backdrop: 'static',
                keyboard: false
            });
        }
        
        self.showPidTuningDialog = function() {
           var dialog = $("#klipper_pid_tuning_dialog");
           dialog.modal({
                show: 'true',
                backdrop: 'static',
                keyboard: false
            });;
        }
        
        self.onGetStatus = function() {
           self.shortStatus("Updating Status ...")
           OctoPrint.control.sendGcode("Status")
        }
        
        self.onRestartFirmware = function() {
           self.shortStatus("Restarting Firmware ...");
           OctoPrint.control.sendGcode("FIRMWARE_RESTART")
        };
        
        self.onRestartHost = function() {
           self.shortStatus("Restarting Host ...");
           OctoPrint.control.sendGcode("RESTART")
        };
        
        self.onAfterBinding = function() {
           self.connectionState.selectedPort(self.settings.settings.plugins.klipper.serialport());
           self.shortStatus("Idle");
        }
        
        self.onDataUpdaterPluginMessage = function(plugin, message) {
           self.logMessage(message["time"], message["type"], message["message"]);
        }

        self.logMessage = function(timestamp, type, message) {
           self.logMessages.push({time: timestamp, type: type, msg: message});
        }
        
        self.onClearLog = function() {
           self.logMessages.removeAll();
        };
        
        self.isActive = function() {
           return self.connectionState.isOperational() && self.loginState.isUser();
        }
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: KlipperViewModel,
        dependencies: ["settingsViewModel", "loginStateViewModel", "connectionViewModel"],
        elements: ["#tab_plugin_klipper_main", "#sidebar_plugin_klipper", "#navbar_plugin_klipper"]
    });
});