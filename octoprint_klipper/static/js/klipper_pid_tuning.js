// OctoPrint Klipper Plugin
//
// Copyright (C) 2018  Martin Muehlhaeuser <github@mmone.de>
//
// This file may be distributed under the terms of the GNU GPLv3 license.

$(function() {
    function KlipperPidTuningViewModel(parameters) {
        var self = this;
        
        self.heaterName = ko.observable();
        self.targetTemperature = ko.observable();
        
        self.onStartup = function() {
           self.heaterName("");
           self.targetTemperature(190);
        }
        
        self.startTuning = function() {
           OctoPrint.control.sendGcode("PID_CALIBRATE HEATER=" + self.heaterName() + " TARGET=" + self.targetTemperature());
        }
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: KlipperPidTuningViewModel,
        dependencies: [],
        elements: ["#klipper_pid_tuning_dialog"]
    });
});
