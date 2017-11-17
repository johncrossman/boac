(function(angular) {

  'use strict';

  angular.module('boac').directive('search', function() {

    return {
      // @see https://docs.angularjs.org/guide/directive#template-expanding-directive
      restrict: 'E',

      // @see https://docs.angularjs.org/guide/directive#isolating-the-scope-of-a-directive
      scope: {},
      templateUrl: '/static/app/student/searchBox.html',
      controller: function(studentFactory, $q, $scope, $timeout) {

        var loadOptions = function() {
          return studentFactory.getAllStudents('teamCode').then(function(response) {
            return response.data;
          });
        };

        $scope.lazyLoadOptions = function() {
          var deferred = $q.defer();

          $timeout(function() {
            loadOptions().then(deferred.resolve);
          }, 1000);

          return deferred.promise;
        };
      }
    };
  });

}(window.angular));
