(function() {
  'use strict';

  angular
    .module('webapp').directive('pref', preferencePanel);

  /** @ngInject */
  function preferencePanel(mySharedService) {
    var directive = {
      restrict: 'E',
      templateUrl: 'app/components/preferencepanel/preferencepanel.html',
      controller: PreferencePanelController,
      controllerAs: 'vm',
      bindToController: true
    };

    return directive;

    /** @ngInject */
    function PreferencePanelController(moment, $scope, $log) {
      var vm = this;
      $scope.hidden = true;
      vm.incidentsCount = null;
      vm.casualtiesCount = null;
      vm.toggleIcon = 'glyphicon-chevron-down';
      vm.dateMaxLimit = 'December 31, 2015'; //to be refactored;
      vm.enddateMaxLimit = 'December 31, 2015';
      vm.modeId = 1;

      vm.viewModes = [{
        id: "1",
        name: "by Year"
      }, {
        id: "2",
        name: "by Month"
      }, {
        id: "3",
        name: "by Range"
      }, {
        id: "4",
        name: "by Date"
      }];

      /* event handler */
      $scope.$on('updatePanelStat', function() {
        vm.incidentsCount = mySharedService.accIncidents;
        vm.casualtiesCount = mySharedService.accCasualties;
        $log.log('successfully received request and updated pref pane');
      });

      $scope.$on('togglePrefPanel', function() {
          if (!$scope.hidden) {
              vm.collapse();
          }
      });

      $scope.$watch('vm.modeId', function() {
        vm.isYearModeEnabled = vm.modeId == '1' ? true : false;
        vm.isMonthModeEnabled = vm.modeId == '2' ? true : false;
        vm.isRangeModeEnabled = vm.modeId == '3' ? true : false;
        vm.isDateModeEnabled = vm.modeId == '4' ? true : false;
      });

      /* self defined functions */
      vm.init = function() {
        mySharedService.sendRenderYearRequest('2015');
      };

      vm.changeMarkerStatus = function(status) {
        mySharedService.sendMarkerStatusUpdateRequest(status);
      };

      vm.changeShapeStatus = function(status) {
        mySharedService.sendShapeStatusUpdateRequest(status);
      };

      vm.changeHeatmapStatus = function(status) {
        mySharedService.sendHeatmapStatusUpdateRequest(status);
      };

      vm.applyFeatureFilter = function(status) {
        mySharedService.sendApplyFeatureFilterRequest(status);
      };

      vm.updateEDMaxLimit = function() {
        var result = new Date(vm.selectedstartdate);
        result.setDate(result.getDate() + 90);
        vm.enddateMaxLimit = result.toString();
      };

      vm.placeChanged = function() {
        vm.place = this.getPlace();
        mySharedService.sendRecenterRequest(vm.place.geometry.location);
        $log.log('sending request');
      };

      vm.applyRender = function() {
        mySharedService.sendToggleLoadScreenRequest();
        if (vm.modeId == 1) {
          vm.yearRender();
        } else if (vm.modeId == 2) {
          vm.monthRender();
        } else if (vm.modeId == 3) {
          vm.rangeRender();
        } else if (vm.modeId == 4) {
          vm.dateRender();
        } else {
          $log.log("Error");
        }
      };

      vm.yearRender = function() {
        if (angular.isUndefined(vm.selectedyear)) { //error handling
          vm.invalidYearMessage = 'Please enter a valid year.';
        } else {
          vm.invalidYearMessage = '';
          mySharedService.sendRenderYearRequest(vm.selectedyear);
        }
      };

      vm.monthRender = function() {
        if (angular.isUndefined(vm.selectedyear) && angular.isUndefined(vm.selectedmonth)) { //error handling
          vm.invalidYearMessage = 'Please enter a valid year.';
          vm.invalidMonthMessage = 'Please enter a valid month.';
      } else if (angular.isUndefined(vm.selectedyear) || angular.isUndefined(vm.selectedmonth)) {
          if (angular.isUndefined(vm.selectedyear)) {
            vm.invalidYearMessage = 'Please enter a valid year.';
            vm.invalidMonthMessage = '';
          } else { // if (vm.selectedmonth == undefined)
            vm.invalidMonthMessage = 'Please enter a valid month.';
            vm.invalidYearMessage = '';
          }
        } else {
          vm.invalidYearMessage = '';
          vm.invalidMonthMessage = '';
          mySharedService.sendRenderMonthRequest(vm.selectedyear, vm.selectedmonth);
        }
      };

      vm.rangeRender = function() {
        if (angular.isUndefined(vm.selectedstartdate) && angular.isUndefined(vm.selectedenddate)) {
          vm.invalidSDMessage = 'Date cannot be blank.';
          vm.invalidEDMessage = 'Date cannot be blank.';
      } else if (angular.isUndefined(vm.selectedstartdate) || angular.isUndefined(vm.selectedenddate)) {
          if (angular.isUndefined(vm.selectedstartdate)) {
            vm.invalidSDMessage = 'Date cannot be blank.';
            vm.invalidEDMessage = '';
          } else { // if (vm.selectedenddate == null)
            vm.invalidEDMessage = 'Date cannot be blank.';
            vm.invalidSDMessage = '';
          }
        } else {
          vm.invalidSDMessage = '';
          vm.invalidEDMessage = '';
          mySharedService.sendRenderRangeRequest(new Date(vm.selectedstartdate), new Date(vm.selectedenddate));
        }
      };

      vm.dateRender = function () {
          if (angular.isUndefined(vm.selecteddate)) {
            vm.invalidDateMessage = 'Date cannot be blank.';
        } else {
            vm.invalidDateMessage = '';
            mySharedService.sendRenderDateRequest(new Date(vm.selecteddate));
        }
    };

      /* to be refactored */
      vm.collapse = function() {
        if (!$scope.hidden) {
          angular.element('#panel').css('top', '-1000px');
          vm.toggleIcon = 'glyphicon-chevron-down';
        } else {
          angular.element('#panel').css('top', '0px');
          vm.toggleIcon = 'glyphicon-chevron-up';
        }
        $scope.hidden = !$scope.hidden;
      };

    }
  }
})();
