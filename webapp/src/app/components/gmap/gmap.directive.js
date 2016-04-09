(function() {
  'use strict';

  angular
    .module('webapp')
    .directive('gmap', googleMap);

  /** @ngInject */
  function googleMap() {
    var directive = {
      restrict: 'E',
      controller: GMapController,
      controllerAs: 'vm',
      bindToController: true,
      heatmapData: null
    };

    return directive;

    /** @ngInject */
    function GMapController() {

    }

  }

})();
