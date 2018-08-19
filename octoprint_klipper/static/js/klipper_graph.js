// OctoPrint Klipper Plugin
//
// Copyright (C) 2018  Martin Muehlhaeuser <github@mmone.de>
//
// This file may be distributed under the terms of the GNU GPLv3 license.

$(function() {

function KlipperGraphViewModel(parameters) {
   var self = this;
   self.loginState = parameters[0];
   
   self.header = OctoPrint.getRequestHeaders({
      "content-type": "application/json",
      "cache-control": "no-cache"
   });
   
   self.apiUrl = OctoPrint.getSimpleApiUrl("klipper");
   
   self.availableLogFiles = ko.observableArray();
   self.logFile = ko.observable();
   self.status = ko.observable();
   self.datasets = ko.observableArray();
   self.datasetFill = ko.observable(false);
   self.canvas;
   self.canvasContext;
   self.chart;
   self.spinnerDialog;

   self.onStartup = function() {
      self.canvas = $("#klipper_graph_canvas")[0]
      self.canvasContext = self.canvas.getContext("2d");
      self.spinnerDialog = $("#klipper_graph_spinner");
      
      Chart.defaults.global.elements.line.borderWidth=1;
      Chart.defaults.global.elements.line.fill= false;
      Chart.defaults.global.elements.point.radius= 0;
      
      var myChart = new Chart(self.canvas, {
         type: "line"
      });
      
      if(self.loginState.loggedIn()) {
         self.listLogFiles();
      }
   }
   
   self.onUserLoggedIn = function(user) {
      self.listLogFiles();
   }
   
   self.listLogFiles = function() {
      var settings = {
        "crossDomain": true,
        "url": self.apiUrl,
        "method": "POST",
        "headers": self.header,
        "processData": false,
        "dataType": "json",
        "data": JSON.stringify({command: "listLogFiles"})
      }
      
      $.ajax(settings).done(function (response) {
         self.availableLogFiles.removeAll();
         self.availableLogFiles(response["data"]);
      });
   }
   
   self.saveGraphToPng = function() {
      button =  $('#download-btn');
      var dataURL = self.canvas.toDataURL("image/png");//.replace("image/png", "image/octet-stream");
      button.attr("href", dataURL);
   }
   
   self.showSpinner = function(showDialog) {
      if (showDialog) {
         self.spinnerDialog.modal({
            show: true,
            keyboard: false,
            backdrop: "static" 
         });
      } else {
         self.spinnerDialog.modal("hide");
      }
   }
   
   self.toggleDatasetFill = function() {
      if(self.datasets) {
         for (i=0; i < self.datasets().length; i++) {
            self.datasets()[i].fill = self.datasetFill();
         }
         self.chart.update();
      }
      return true
   }
   
   self.convertTime = function(val) {
      return moment(val, "X");
   }
   
   self.loadData = function() {
      var settings = {
        "crossDomain": true,
        "url": self.apiUrl,
        "method": "POST",
        "headers": self.header,
        "processData": false,
        "dataType": "json",
        "data": JSON.stringify(
           {
              command: "getStats",
              logFile: self.logFile()
           }
        )
      }
      
      self.showSpinner(true);
      
      $.ajax(settings).done(function (response) {
         self.status("")
         self.datasetFill(false);
         
         self.showSpinner(false);
         
         if("error" in response) {
            self.status(response.error);
         } else {
            self.datasets.removeAll();
            self.datasets.push(
            {
               label: "MCU Load",
               backgroundColor: "rgba(199, 44, 59, 0.5)",
               borderColor: "rgb(199, 44, 59)",
               yAxisID: 'y-axis-1',
               data: response.loads
            });
            
            self.datasets.push(
            {
               label: "Bandwith",
               backgroundColor: "rgba(255, 130, 1, 0.5)",
               borderColor: "rgb(255, 130, 1)",
               yAxisID: 'y-axis-1',
               data: response.bwdeltas
            });
            
            self.datasets.push(
            {
               label: "Host Buffer",
               backgroundColor: "rgba(0, 145, 106, 0.5)",
               borderColor: "rgb(0, 145, 106)",
               yAxisID: 'y-axis-1',
               data: response.buffers
            });
            
            self.datasets.push(
            {
               label: "Awake Time",
               backgroundColor: "rgba(33, 64, 95, 0.5)",
               borderColor: "rgb(33, 64, 95)",
               yAxisID: 'y-axis-1',
               data: response.awake
            });
            
            self.chart = new Chart(self.canvas, {
               type: "line",
               data: {
                  labels: response.times,
                  datasets: self.datasets()
               },
               options: {
                  elements:{
                     line: {
                        tension: 0
                     }
                  },
                  scales: {
                     xAxes: [{
                        type: 'time',
                        time: {
                           parser:  self.convertTime,
                           tooltipFormat: "HH:mm",
                           displayFormats: {
                              minute: "HH:mm",
                              second: "HH:mm",
                              millisecond: "HH:mm"
                           }
                        },
                        scaleLabel: {
                           display: true,
                           labelString: 'Time'
                        }
                     }],
                     yAxes: [{
                        scaleLabel: {
                           display: true,
                           labelString: '%'
                        },
                        position: 'left',
                        id: 'y-axis-1'
                     }
                     ]
                  },
                  legend: {
                     
                  }
               }
            });
         }
      });
   }
}

OCTOPRINT_VIEWMODELS.push({
      construct: KlipperGraphViewModel,
      dependencies: ["loginStateViewModel"],
      elements: ["#klipper_graph_dialog"]
   });
});
