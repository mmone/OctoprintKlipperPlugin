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
           OctoPrint.control.sendGcode("G28")
           self.moveToPoint(0);
        }
        
        self.stopLeveling = function() {
           OctoPrint.control.sendGcode("G1 Z" +
              (self.settings.settings.plugins.klipper.probeHeight()*1 +
               self.settings.settings.plugins.klipper.probeLift()*1)
           );
           self.gotoHome();
        }
        
        self.gotoHome = function() {
           OctoPrint.control.sendGcode("G28");
           self.activePoint(-1);
        }
        
        self.nextPoint = function() {
           self.moveToPoint(self.activePoint()+1);
        }
        
        self.previousPoint = function() {
           self.moveToPoint(self.activePoint()-1);
        }
        
        self.jumpToPoint = function(item) {
           self.moveToPoint(
              self.settings.settings.plugins.klipper.probePoints().indexOf(item)
           );
        }
        
        self.pointCount = function() {
           return self.settings.settings.plugins.klipper.probePoints().length;
        }
        
        self.moveToPosition = function(x, y) {
           OctoPrint.control.sendGcode( 
              "G1 Z" + (self.settings.settings.plugins.klipper.probeHeight() * 1 + 
              self.settings.settings.plugins.klipper.probeLift()*1) +
              " F" + self.settings.settings.plugins.klipper.probeSpeedZ()
           );
           OctoPrint.control.sendGcode(
              "G1 X" + x + " Y" + y +
              " F" + self.settings.settings.plugins.klipper.probeSpeedXy()
           );
           OctoPrint.control.sendGcode(
              "G1 Z" + self.settings.settings.plugins.klipper.probeHeight() +
               " F" + self.settings.settings.plugins.klipper.probeSpeedZ()
           );
        }
        
        self.moveToPoint = function(index) {
           var point = self.settings.settings.plugins.klipper.probePoints()[index];

           self.moveToPosition(point.x(), point.y());
           self.activePoint(index);
        }
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: KlipperLevelingViewModel,
        dependencies: ["settingsViewModel", "loginStateViewModel", "connectionViewModel"],
        elements: ["#klipper_leveling_dialog"]
    });
});