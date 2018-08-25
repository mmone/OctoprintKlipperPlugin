// OctoPrint Klipper Plugin
//
// Copyright (C) 2018  Martin Muehlhaeuser <github@mmone.de>
//
// This file may be distributed under the terms of the GNU GPLv3 license.

$(function() {
    function KlipperMacroDialogViewModel(parameters) {
        var self = this;
        
        self.parameters = ko.observableArray();
        self.interpolatedCmd;
        self.macro;
        self.macroName = ko.observable();
        
        var paramObjRegex = /{(.*?)}/g;
        var keyValueRegex = /(\w*)\s*:\s*([\w°"|]*)/g;
              
        self.process = function(macro) {
           self.macro = macro.macro();
           self.macroName(macro.name());
           
           var matches = self.macro.match(paramObjRegex);
           var params = [];
           
           for (var i=0; i < matches.length; i++) {
              var obj = {};
              var res = keyValueRegex.exec(matches[i]);
              
              while (res != null) {
                 if("options" == res[1]) {
                    obj["options"] = res[2].split("|");
                 } else {
                    obj[res[1]] = res[2];
                 }
                 res = keyValueRegex.exec(matches[i]);
              }
              
              if(!("label" in obj)) {
                 obj["label"] = "Input " + (i+1);
              }
              
              if(!("unit" in obj)) {
                 obj["unit"] = "";
              }
              
              if("default" in obj) {
                 obj["value"] = obj["default"];
              }
              
              params.push(obj);
           }
           self.parameters(params);
        }
        
        self.executeMacro = function() {
           var i=-1;
           
           function replaceParams(match) {
              i++;
              return self.parameters()[i]["value"];
           }
           
           expanded = self.macro.replace(paramObjRegex, replaceParams)
           expanded = expanded.replace(/(?:\r\n|\r|\n)/g, " ");
           
           OctoPrint.control.sendGcode(expanded);
        }
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: KlipperMacroDialogViewModel,
        dependencies: [],
        elements: ["#klipper_macro_dialog"]
    });
});
