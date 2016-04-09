(function() {
  'use strict';

  var main = angular
    .module('webapp')
    .controller('MainController', MainController);
  main.$inject = ['$scope', 'mySharedService'];

  /** @ngInject */
  function MainController(NgMap, $scope, $http, mySharedService, $log) {

    var vm = this;
    var aeroData = [];
    var heatMapLayer = null;
    var aeroIncidentArray = [];
    var impactCircle = [];
    vm.firstRun = true;
    vm.incidentsMark = {};
    vm.accumulatedIncidents = 0;
    vm.accumulatedCasualties = 0;
    vm.markerStatus = false;
    vm.shapeStatus = false;
    vm.applyFilter = false;

    vm.showDetail = function(e, incident) {

      mySharedService.sendTogglePrefPanelRequest();
      vm.incident = incident;
      vm.map.showInfoWindow('incident-infoWindow', incident.event_identifier);
      mySharedService.sendRecenterRequest({
        lat: incident.position[0],
        lng: incident.position[1]
      });
    };

    vm.showDetailNarrative = function(event_identifier) {
      mySharedService.sendTogglePrefPanelRequest();
      mySharedService.sendShowIncidentDetailRequest(event_identifier);
    };

    vm.drawCircle = function(center, radius, projection) {
      var i, angle, x1, y1;
      var circle = [];
      var point = projection.fromLatLngToPoint(center);
      var x = point.x;
      var y = point.y;
      for (var i = 0; i < 360; i += 10) {
        angle = i;
        x1 = radius * Math.cos(angle * Math.PI / 180);
        y1 = radius * Math.sin(angle * Math.PI / 180);
        circle.push(projection.fromPointToLatLng(new google.maps.Point(x + x1, y + y1)));
      }
      return circle;
    };

    vm.colorDetermine = function(x) {
      var scale = [
        '#1DAA97',
        '#1D64AA',
        '#5F1DAA',
        '#A01DAA',
        '#AA1D60',
        '#AA251D',
        '#FF0000'
      ];
      if (x < 10) {
        return scale[0];
      } else if (x < 25) {
        return scale[1];
      } else if (x < 50) {
        return scale[2];
      } else if (x < 75) {
        return scale[3];
      } else if (x < 100) {
        return scale[4];
      } else if (x < 150) {
        return scale[5];
      } else {
        return scale[6];
      }
    };

    vm.getIcon = function(x) {
      var icon = null;
      if (x == 'real') {
        icon = {
          url: 'assets/images/app/exactmark.png'
        };
      } else if (x == 'estimated') {
        icon = {
          url: 'assets/images/app/approxmark.png'
        };
      }
      return icon;
    };

    /* event handler */
    vm.isLoading = function() {
      return $http.pendingRequests.length > 0;
    };

    $scope.$watch(vm.isLoading, function(v) {
      if (v) {
        vm.isLoading = true;
      } else {
        vm.isLoading = false;
      }
    });

    $scope.$on('recenter', function() {
      var location = mySharedService.location;
      vm.map.panTo(location);
    });

    $scope.$on('applyFeatureFilter', function() {
      vm.applyFilter = mySharedService.featureFilterApply;
      mySharedService.sendRenderRefreshRequest();
    });

    $scope.$on('toggleMarkerStatusUpdate', function() {
      vm.markerStatus = mySharedService.markerDisplay;
      // for (var key in vm.map.markers) {
      //   vm.map.markers[key].setMap(null);
      // }
    });

    $scope.$on('toggleHeatmapStatusUpdate', function() {
      if (mySharedService.heatmapDisplay) {
        heatMapLayer.setMap(vm.map);
      } else {
        heatMapLayer.setMap(null);
      }
    });

    $scope.$on('toggleShapeStatusUpdate', function() {
      if (mySharedService.shapeDisplay) {
        $log.log("service request received!");
        var projection = vm.map.getProjection();
        for (var data in aeroData) {
          var populationOptions = {
            strokeColor: vm.colorDetermine(aeroData[data].weight),
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillColor: vm.colorDetermine(aeroData[data].weight),
            fillOpacity: 0.15,
            map: vm.map,
            center: aeroData[data].location,
            radius: Math.sqrt(aeroData[data].weight) * 100,
            path: vm.drawCircle(aeroData[data].location, Math.sqrt(aeroData[data].weight) * 1, projection)
          };
          impactCircle.push(new google.maps.Polygon(populationOptions));
        }
      } else {
        for (var circle in impactCircle) {
          impactCircle[circle].setMap(null);
        }
      }
    });

    $scope.$on('render', function() {
      vm.url = mySharedService.requestURL;

      if (!vm.firstRun) {
        //reset start here
        
        aeroData = [];
        heatMapLayer.setData([]);
        heatMapLayer.setMap(vm.map);
        vm.incidentsMark = {};
        vm.accumulatedIncidents = 0;
        vm.accumulatedCasualties = 0;
        $log.log('reset done.');
      }

      var resp = $http.get(vm.url)
        .then(function(result) {
          return result.data;
        });

      Promise.resolve(resp).then(function(data) {
        for (var i = 0; i < data.length; i++) {
          var lat = data[i].lat;
          var lon = data[i].lon;
          var idx = data[i].inj_count;
          var eventid = data[i].ev_id;
          var date = data[i].ev_date;
          var approxLocation = data[i].approx_loc;
          if (vm.applyFilter && idx === 0)
            continue;

          vm.incidentsMark[eventid] = {
            "event_identifier": eventid,
            "event_date": date.substr(0, date.indexOf('T')),
            "population": idx,
            "approx_loc": (approxLocation == '0') ? 'real' : 'estimated',
            "position": [lat, lon]
          };

          vm.accumulatedIncidents++;
          vm.accumulatedCasualties += idx;

          aeroData.push({
            location: new google.maps.LatLng(lat, lon),
            weight: idx
          });
        }
      }).then(function() {

        $log.log('successfully hitting API and resolved promise to various data structures');
        mySharedService.sendPanelStateUpdateRequest(vm.accumulatedIncidents, vm.accumulatedCasualties);
        aeroIncidentArray = new google.maps.MVCArray(aeroData);

        heatMapLayer = new google.maps.visualization.HeatmapLayer({
          data: aeroIncidentArray,
          radius: 60
        });
        $scope.$apply(function() {
          NgMap.getMap({
            id: 'aeromap'
          }).then(function(map) {
            vm.map = map;
            map.setOptions({
              minZoom: 3
            });
            heatMapLayer.setMap((mySharedService.heatmapDisplay === null || mySharedService.heatmapDisplay === true) ? map : null);
            var gradient = [
              'rgba(251, 255, 31, 0)',
              'rgba(251, 255, 31, 0.5)',
              'rgba(245, 235, 28, 0.75)',
              'rgba(239, 216, 26, 1)',
              'rgba(234, 197, 23, 1)',
              'rgba(228, 177, 21, 1)',
              'rgba(223, 158, 19, 1)',
              'rgba(217, 139, 16, 1)',
              'rgba(212, 119, 14, 1)',
              'rgba(206, 100, 11, 1)',
              'rgba(201, 81, 9, 1)',
              'rgba(195, 61, 7, 1)',
              'rgba(190, 42, 4, 1)',
              'rgba(184, 23, 2, 1)'
            ];
            heatMapLayer.set('gradient', heatMapLayer.get('gradient') ? null : gradient);
            // if shape is turned on
            if (mySharedService.shapeDisplay) {
              mySharedService.sendShapeStatusUpdateRequest(false); //reset
              mySharedService.sendShapeStatusUpdateRequest(true);
            }
          });
        });
      });
      vm.firstRun = false;
    });

  }
})();
