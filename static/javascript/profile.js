$(function () {
    $('.column').equalHeight();
});


var application = angular.module("profile", []);

application.config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol('a{');
    $interpolateProvider.endSymbol('}a');
}]);
application.controller("myCtrl", function ($scope, $http) {

    $http({
        method: 'GET',
        url: '/return_admin_info'
    }).then(function successCallback(response) {
        $scope.name = response.data[0];
        $scope.avatar = response.data[1];
        $scope.post_num = response.data[2];
        $scope.user_num = response.data[3];
        $scope.superstatus = response.data[4];
        $scope.admin_id = response.data[5];
    }, function errorCallback(response) {
        console.log("Error");
    });

    $http({
        method: 'GET',
        url: '/return_admins'
    }).then(function successCallback(response) {
        $scope.namelist = response.data[0];
        $scope.post_stat = response.data[1];
        $scope.user_stat = response.data[2];
    }, function errorCallback(response) {
        console.log("Error");
    });
});




