(function() {
  'use strict';

  angular.module('webapp').factory('mySharedService', function($rootScope) {
    var sharedService = {};

    sharedService.message = '';

    sharedService.accIncidents = null;
    sharedService.accCasualties = null;

    sharedService.markerDisplay = null;
    sharedService.shapeDisplay = null;
    sharedService.heatmapDisplay = null;
    sharedService.featureFilterApply = null;

    sharedService.requestURL = null; // for fetching list of incidents to visualize on heatmap
    sharedService.requestIncidentDetailURL = null;
    sharedService.requestSimilarIncidentURL = null;

    sharedService.domain = 'http://localhost:5000'
      //'http://localhost:5000/api/v2/ntsb/incidents/list/listrange?startyear=2015&startmonth=01&startday=01&endyear=2015&endmonth=12&endday=31';

    sharedService.sendRecenterRequest = function(location) {
      this.location = location;
      $rootScope.$broadcast('recenter');
    };

    sharedService.sendPanelStateUpdateRequest = function(accIncidents, accCasualties) {
      this.accIncidents = accIncidents;
      this.accCasualties = accCasualties;
      $rootScope.$broadcast('updatePanelStat');
    };

    sharedService.sendApplyFeatureFilterRequest = function(status) {
      this.featureFilterApply = status;
      $rootScope.$broadcast('applyFeatureFilter');
    }

    sharedService.sendMarkerStatusUpdateRequest = function(status) {
      this.markerDisplay = status;
      $rootScope.$broadcast('toggleMarkerStatusUpdate');
    };

    sharedService.sendShapeStatusUpdateRequest = function(status) {
      this.shapeDisplay = status;
      $rootScope.$broadcast('toggleShapeStatusUpdate');
    };

    sharedService.sendHeatmapStatusUpdateRequest = function(status) {
      this.heatmapDisplay = status;
      $rootScope.$broadcast('toggleHeatmapStatusUpdate');
    };

    sharedService.sendToggleLoadScreenRequest = function(status) {
      $rootScope.$broadcast('toggleLoadScreen');
    };

    sharedService.sendRenderRangeRequest = function(startRange, endRange) {
      var startDay = startRange.getDate();
      var startMonth = startRange.getMonth() + 1;
      var startYear = startRange.getFullYear();
      var endDay = endRange.getDate();
      var endMonth = endRange.getMonth() + 1;
      var endYear = endRange.getFullYear();
      sharedService.requestURL = this.domain + '/api/v2/ntsb/incidents/list/listrange?startyear=' + startYear + '&startmonth=' + startMonth + '&startday=' + startDay + '&endyear=' + endYear + '&endmonth=' + endMonth + '&endday=' + endDay;
      $rootScope.$broadcast('render');
      //sharedService.requestURL =
    };

    sharedService.sendRenderRefreshRequest = function() {
      $rootScope.$broadcast('render');
    }

    sharedService.sendRenderDateRequest = function(date) {
      var day = date.getDate();
      var month = date.getMonth() + 1;
      var year = date.getFullYear();
      sharedService.requestURL = this.domain + '/api/v2/ntsb/incidents/list/listrange?startyear=' + year + '&startmonth=' + month + '&startday=' + day;
      $rootScope.$broadcast('render');
    };

    sharedService.sendRenderYearRequest = function(year) {
      sharedService.requestURL = this.domain + '/api/v2/ntsb/incidents/list/listrange?startyear=' + year + '&startmonth=' + '01' + '&startday=' + '01' + '&endyear=' + year + '&endmonth=' + '12' + '&endday=' + '31';
      $rootScope.$broadcast('render');
    };

    sharedService.sendRenderMonthRequest = function(year, month) {
      var isLeap = (year % 4 == 0);
      var daysInMonth = 31 - ((month == 2) ? (isLeap ? 2 : 3) : ((month - 1) % 7 % 2));
      sharedService.requestURL = this.domain + '/api/v2/ntsb/incidents/list/listrange?startyear=' + year + '&startmonth=' + month + '&startday=' + '01' + '&endyear=' + year + '&endmonth=' + month + '&endday=' + daysInMonth;
      $rootScope.$broadcast('render');
    };

    sharedService.sendShowIncidentDetailRequest = function(eventid) {
      sharedService.requestIncidentDetailURL = this.domain + '/api/v2/ntsb/incidents/incidentdetails?incident=' + eventid;
      sharedService.requestSimilarIncidentURL = this.domain + '/api/v2/ntsb/incidents/similarincidents?incident=' + eventid;
      $rootScope.$broadcast('showIncidentNarrativeDetail');
    };

    sharedService.sendTogglePrefPanelRequest = function() {
      $rootScope.$broadcast('togglePrefPanel');
    };

    return sharedService;
  });


})();
