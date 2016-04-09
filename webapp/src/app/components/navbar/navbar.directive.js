(function() {
  'use strict';

  angular
    .module('webapp')
    .directive('navbar', acmeNavbar);

  /** @ngInject */
  function acmeNavbar() {
    var directive = {
      restrict: 'E',
      templateUrl: 'app/components/navbar/navbar.html',
      controller: NavbarController,
      controllerAs: 'vm',
      bindToController: true
    };

    return directive;

    /** @ngInject */
    function NavbarController() {


      // "vm.creation" is avaible by directive option "bindToController: true"
      // vm.relativeDate = moment(vm.creationDate).fromNow();
    }
  }

})();
