$(function() {
    function KlipperPidTuningViewModel(parameters) {
        var self = this;
        
        self.heaterIndex = ko.observable();
        self.targetTemperature = ko.observable();
        
        self.onStartup = function() {
           self.heaterIndex(0);
           self.targetTemperature(190);
        }
        
        self.startTuning = function() {
           OctoPrint.control.sendGcode("PID_TUNE E" + self.heaterIndex() + " S" + self.targetTemperature());
        }
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: KlipperPidTuningViewModel,
        dependencies: [],
        elements: ["#klipper_pid_tuning_dialog"]
    });
});