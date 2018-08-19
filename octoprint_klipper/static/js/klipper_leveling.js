// OctoPrint Klipper Plugin
//
// Copyright (C) 2018  Martin Muehlhaeuser <github@mmone.de>
//
// This file may be distributed under the terms of the GNU GPLv3 license.

$(function() {
    function KlipperLevelingViewModel(parameters) {
        var self = this;
        self.settings = parameters[0];
        self.loginState = parameters[1];
        
        self.activePoint = ko.observable(-1);
        self.pointCount = ko.observable();
        self.points = ko.observableArray();
        
        self.initView = function() {
           self.points(self.settings.settings.plugins.klipper.probe.points());
           self.pointCount(
             self.points().length
           );
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
              self.points().indexOf(item)
           );
        }
        /*
        self.pointCount = function() {
           return self.settings.settings.plugins.klipper.probe.points().length;
        }
        */
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
           var point = self.points()[index];

           self.moveToPosition(point.x(), point.y());
           self.activePoint(index);
        }
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: KlipperLevelingViewModel,
        dependencies: ["settingsViewModel", "loginStateViewModel"],
        elements: ["#klipper_leveling_dialog"]
    });
});