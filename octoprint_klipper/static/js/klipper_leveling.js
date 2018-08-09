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
              (self.settings.settings.plugins.klipper.probe.height()*1 +
               self.settings.settings.plugins.klipper.probe.lift()*1)
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
              self.settings.settings.plugins.klipper.probe.points().indexOf(item)
           );
        }
        
        self.pointCount = function() {
           return self.settings.settings.plugins.klipper.probe.points().length;
        }
        
        self.moveToPosition = function(x, y) {
           OctoPrint.control.sendGcode( 
              "G1 Z" + (self.settings.settings.plugins.klipper.probe.height() * 1 + 
              self.settings.settings.plugins.klipper.probe.lift()*1) +
              " F" + self.settings.settings.plugins.klipper.probe.speed_z()
           );
           OctoPrint.control.sendGcode(
              "G1 X" + x + " Y" + y +
              " F" + self.settings.settings.plugins.klipper.probe.speed_xy()
           );
           OctoPrint.control.sendGcode(
              "G1 Z" + self.settings.settings.plugins.klipper.probe.height() +
               " F" + self.settings.settings.plugins.klipper.probe.speed_z()
           );
        }
        
        self.moveToPoint = function(index) {
           var point = self.settings.settings.plugins.klipper.probe.points()[index];

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