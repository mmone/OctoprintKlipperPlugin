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
