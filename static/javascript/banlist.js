$(function () {
    $('.column').equalHeight();
});

var application = angular.module("ban_list", []);

application.config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol('a{');
    $interpolateProvider.endSymbol('}a');
}]);
application.controller("myCtrl", function ($scope, $http) {

    $scope.delete_index = null;
    $scope.unban_author_id = null;
    $scope.name = null;

    $http({
        method: 'GET',
        url: '/return_banlist'
    }).then(function successCallback(response) {
        $scope.banned_users = response.data;
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

    $scope.un_ban = function (author_id, delete_index, name, reason) {
        $scope.banned_users.splice(delete_index, 1);
        var dataObj = JSON.stringify({type: "unban", id: author_id, name: name, reason: reason});
        $http({
            method: 'POST',
            url: '/return_data',
            data: dataObj
        }).then(function successCallback(response) {
            console.log(" post success!");
        }, function errorCallback(response) {
            console.log("Error");
        });
    };

    $scope.openDialog = function (index_to_delete, unban_id, name) {
        $scope.delete_index = index_to_delete;
        $scope.unban_author_id = unban_id;
        $scope.name = name;
        document.getElementById('myModal').style.display = "block";
    };

    $scope.closeDialog = function () {
        document.getElementById('myModal').style.display = "none";
        $scope.delete_index = null;
        $scope.unban_author_id = null;
        $scope.name = null;
    };

    $scope.confirmReason = function () {
        var reason = document.getElementById('comment_text').value;
        if (reason) {
            $scope.un_ban($scope.unban_author_id, $scope.delete_index, $scope.name, reason);
        }
        $scope.closeDialog();
    }
});

function selectionChange() {
    var e = document.getElementById("select_reason");
    document.getElementById('comment_text').value = e.options[e.selectedIndex].value;
}

