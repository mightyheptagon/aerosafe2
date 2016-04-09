(function() {
  'use strict';

  angular
    .module('webapp')
    .directive('incidentdetails', inctDetail);

  /** @ngInject */
  function inctDetail(mySharedService) {
    var directive = {
      restrict: 'E',
      templateUrl: 'app/components/incidentdetails/incidentdetails.html',
      controller: incidentDetailsController,
      controllerAs: 'idp',
      bindToController: true
    };

    return directive;

    /** @ngInject */
    function incidentDetailsController($scope, $http, $log) {
      var idp = this;
      idp.showincidentDetail = false;
      idp.idp_incidentDate = null;
      idp.idp_casualty = null;
      idp.idp_incidentLocation = null;
      idp.idp_engine = null;
      idp.idp_aircraftMake = null;
      idp.idp_flyingType = null;
      idp.idp_preliminaryNarrative = null;
      idp.idp_finalNarrative = null;
      idp.idp_cause = null;
      idp.relatedIncidents = [];

      idp.closeDetail = function() {
        idp.showincidentDetail = false;
      };

      idp.refreshContent = function(id) {
        idp.showincidentDetail = false;
        mySharedService.sendShowIncidentDetailRequest(id);
      };

      $scope.$on('showIncidentNarrativeDetail', function() {
        idp.relatedIncidents = [];
        idp.si_url = mySharedService.requestSimilarIncidentURL;
        var si_resp = $http.get(idp.si_url)
          .then(function(result) {
            return result.data;
          });
        Promise.resolve(si_resp).then(function(data) {
          console.log(data);
          if (data.indexOf("API Error") > -1) {
            $scope.$apply(function() {
              idp.relatedIncidents = [];
            });
          }

          for (var i = 0; i < data.length; i++) {
            var date = data[i][0].ev_date.substr(0, data[i][0].ev_date.indexOf('T'));
            var loc = data[i][0].ev_city.trim() + ", " + data[i][0].ev_state + ", " + data[i][0].country_name;
            var inj = (data[i][0].inj_count === null) ? 0 : data[i][0].inj_count;
            var ev_id = data[i][0].ev_id;
            $scope.$apply(function() {
              idp.relatedIncidents.push({
                "date": date,
                "loc": loc,
                "inj": inj,
                "ev_id": ev_id
              });
            });
          }
        });

        idp.in_url = mySharedService.requestIncidentDetailURL;
        var in_resp = $http.get(idp.in_url)
          .then(function(result) {
            return result.data;
          });
        Promise.resolve(in_resp).then(function(data) {
          console.log(data);
          var engineSet = [];
          var i;
          for (i = 0; i < data.length; i++) {
            if ("ev_date" in data[i]) { // it exists
              idp.idp_incidentDate = data[i].ev_date.substr(0, data[i].ev_date.indexOf('T'));
              idp.idp_incidentLocation = data[i].ev_city.trim() + ", " + data[i].ev_state + ", " + data[i].country_name;
            } else if ("inj_count" in data[i]) {
              idp.idp_casualty = data[i].inj_count;
            } else if ("eng_model" in data[i]) {
              if (data[i].eng_model === null)
                engineSet.push("No related information");
              else
                engineSet.push(data[i].eng_model.trim() + ", " + data[i].eng_mfgr.trim());
            } else if ("acft_make" in data[i]) {
              idp.idp_aircraftMake = data[i].acft_make.trim() + ", " + data[i].acft_model.trim();
              idp.idp_flyingType = data[i].type_fly;
            } else {
              if (angular.isUndefined(data[i].narr_accp) || (data[i].narr_accp) === null) {
                idp.idp_preliminaryNarrative = "There is no preliminary narrative published by NTSB, or it is temporary unavailable. ";
              } else {
                idp.idp_preliminaryNarrative = data[i].narr_accp;
              }
              if (angular.isUndefined(data[i].narr_accf) || (data[i].narr_accf) === null) {
                idp.idp_finalNarrative = "There is no final narrative published by NTSB, or it is temporary unavailable. ";
              } else {
                idp.idp_finalNarrative = data[i].narr_accf;
              }
              if (angular.isUndefined(data[i].narr_cause) || (data[i].narr_cause) === null) {
                idp.idp_cause = "There is no cause of this incident published by NTSB, or it is temporary unavailable. ";
              } else {
                idp.idp_cause = data[i].narr_cause;
              }
            }
          }
          if (engineSet.length <= 0) {
            idp.idp_engine = "No related information";
          } else if (engineSet.length === 1) {
            idp.idp_engine = engineSet[0];
          } else {
            var engineText = "";
            var j;
            for (j = 0; j < engineSet.length; j++) {
              engineText += "Engine " + (j + 1) + " : " + engineSet[j] + " - ";
            }
            idp.idp_engine = engineText;
          }
        }).then(function() {
          $scope.$apply(function() {
            idp.showincidentDetail = true;
          });
        });
      });
    }
  }

})();
