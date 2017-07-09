$(function () {
    $('.column').equalHeight();
});

var application = angular.module("history", []);

application.config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol('a{');
    $interpolateProvider.endSymbol('}a');
}]);
application.controller("myCtrl", function ($scope, $http) {

    $http({
        method: 'GET',
        url: '/return_history',
        params: {"page": 0}
    }).then(function successCallback(response) {
        $scope.past_posts = response.data[0];
        $scope.numberOfPosts = response.data[1];
    }, function errorCallback(response) {
        console.log("Error");
    });

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

    // start pagination implementation
    $scope.pageSize = 10;

    $scope.range = function () {
        var input = [];
        var pages = Math.ceil($scope.numberOfPosts / $scope.pageSize) - 1;
        for (var i = pages; i >= 0; i -= 1) {
            input.push(i);
        }
        return input;
    };

    $scope.getPosts = function (pageNum) {
        var lastPageNum = Math.ceil($scope.numberOfPosts / $scope.pageSize) - 1;
        $http({
            method: 'GET',
            url: '/return_history',
            params: {"page": lastPageNum-pageNum}
        }).then(function successCallback(response) {
            $scope.past_posts = response.data[0];
            $scope.numberOfPosts = response.data[1];
        }, function errorCallback(response) {
            console.log("Error");
        });
    }
});
application.filter('startFrom', function () {
    return function (input, start) {
        start = +start; //parse to int
        return input.slice(start);
    }
});