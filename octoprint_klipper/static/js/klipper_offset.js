// OctoPrint Klipper Plugin
//
// Copyright (C) 2018  Martin Muehlhaeuser <github@mmone.de>
//
// This file may be distributed under the terms of the GNU GPLv3 license.

$(function() {
    function KlipperOffsetDialogViewModel(parameters) {
        var self = this;
        
        self.offsetX = ko.observable();
        self.offsetY = ko.observable();
        self.offsetZ = ko.observable();
        self.adjust = ko.observable();
        
        self.onStartup = function() {
           self.offsetX(0);
           self.offsetY(0);
           self.offsetZ(0);
           self.adjust(false); 
        }
        
        self.setOffset = function() {
           if(self.adjust()) {
              OctoPrint.control.sendGcode("SET_GCODE_OFFSET X_ADJUST=" + self.offsetX() +
              " Y_ADJUST=" + self.offsetY() +
              " Z_ADJUST=" + self.offsetZ());
           } else {
              OctoPrint.control.sendGcode("SET_GCODE_OFFSET X=" + self.offsetX() +
              " Y=" + self.offsetY() +
              " Z=" + self.offsetZ());
           }
        }
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: KlipperOffsetDialogViewModel,
        dependencies: [],
        elements: ["#klipper_offset_dialog"]
    });
});
