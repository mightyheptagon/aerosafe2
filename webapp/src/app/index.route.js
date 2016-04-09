(function() {
  'use strict';

  angular
    .module('webapp')
    .config(routeConfig);

  function routeConfig($routeProvider) {
    $routeProvider
      .when('/', {
        templateUrl: 'app/main/main.html'
      })
      .otherwise({
        redirectTo: '/'
      });
  }

})();
