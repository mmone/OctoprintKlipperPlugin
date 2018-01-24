$(function() {
    function KlipperLevelingViewModel(parameters) {
        var self = this;
        self.settings = parameters[0];
        self.loginState = parameters[1];
        self.connectionState = parameters[2];
        
        self.activePoint = ko.observable();
        
        self.onStartup = function() {
           self.activePoint(-1);
        }
        
        self.startLeveling = function() {
           self.activePoint(0);
           OctoPrint.control.sendGcode("G28")
           self.moveToPoint(self.activePoint);
        }
        
        self.stopLeveling = function() {
           self.activePoint(-1);
           OctoPrint.control.sendGcode("G1 Z" + self.settings.settings.plugins.klipper.probeHeight() + self.settings.settings.plugins.klipper.probeLift());
           OctoPrint.control.sendGcode("G28")
        }
        
        self.nextPoint = function() {
           self.activePoint(self.activePoint()+1);
           self.moveToPoint(self.activePoint);
        }
        
        self.previousPoint = function() {
           self.activePoint(self.activePoint()-1);
           self.moveToPoint(self.activePoint);
        }
        
        self.pointCount = function() {
           return self.settings.settings.plugins.klipper.probePoints().length;
        }
        
        self.moveToPoint = function(index) {
           var point = self.settings.settings.plugins.klipper.probePoints()[index];

           OctoPrint.control.sendGcode("G1 Z" + self.settings.settings.plugins.klipper.probeHeight() + self.settings.settings.plugins.klipper.probeLift());
           OctoPrint.control.sendGcode("G1 X" + point.x() + " Y" + point.y());
           OctoPrint.control.sendGcode("G1 Z" + self.settings.settings.plugins.klipper.probeHeight());
        }
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: KlipperLevelingViewModel,
        dependencies: ["settingsViewModel", "loginStateViewModel", "connectionViewModel"],
        elements: ["#tab_plugin_klipper_leveling", "#klipper_leveling_dialog"]
    });
});