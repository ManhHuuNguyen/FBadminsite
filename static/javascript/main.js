$(function () {
    $('.column').equalHeight();
});

var application = angular.module("dashboard", []);

application.config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol('a{');
    $interpolateProvider.endSymbol('}a');
}]);
application.controller("myCtrl", function ($scope, $http) {

    $scope.delete_index = null;
    $scope.unban_author_id = null;
    $scope.decision = null;

    $http({
        method: 'GET',
        url: '/return_data'
    }).then(function successCallback(response) {
        $scope.suspicious_posts = response.data;
    }, function errorCallback(response) {
        console.log("Error");
    });

    setInterval(function () {
        $http({
            method: 'GET',
            url: '/return_data'
        }).then(function successCallback(response) {
            $scope.suspicious_posts = response.data;
        }, function errorCallback(response) {
            console.log("Error");
        });
    }, 300000);

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

    $scope.delPost = function (post_id_deleted, index_deleted, reason) {
        $scope.suspicious_posts.splice(index_deleted, 1);
        $scope.post_num = parseInt($scope.post_num) + 1;
        var dataObj = JSON.stringify({type: 'post_deletion', id: post_id_deleted, reason: reason});
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

    $scope.banUser = function (index_deleted, post_id_deleted, reason, timeBan) {
        var banned_id = $scope.suspicious_posts[index_deleted].author_id;
        $scope.suspicious_posts = $scope.suspicious_posts.filter(function (a_post) {
            return a_post.author_id != banned_id;
        });
        $scope.user_num = parseInt($scope.user_num) + 1;
        var dataObj = JSON.stringify({type: 'user_ban', id: post_id_deleted, reason: reason, timeBan: timeBan});
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

    $scope.openDialog = function (which, index_to_delete, post_id) {
        $scope.delete_index = index_to_delete;
        $scope.unban_author_id = unban_author_id;
        $scope.decision = which;
        document.getElementById('myModal').style.display = "block";
        if ($scope.decision=='ban'){
            document.getElementById("timeBan").style.visibility = "visible";
        }
    };

    $scope.closeDialog = function () {
        document.getElementById('myModal').style.display = "none";
        $scope.delete_index = null;
        $scope.unban_author_id = null;
        $scope.decision = null;
        document.getElementById("timeBan").style.visibility = "hidden";
    };

    $scope.confirmReason = function () {
        var reason = document.getElementById('comment_text').value;
        if (reason){
            if ($scope.decision=='ban'){
                var e = document.getElementById("timeBan");
                var timeBan = e.options[e.selectedIndex].value;
                $scope.banUser($scope.delete_index, $scope.unban_author_id, reason, timeBan);
            }
            else {
                $scope.delPost($scope.unban_author_id, $scope.delete_index, reason);
            }
        }
        $scope.closeDialog();
    }
});

function selectionChange() {
    var e = document.getElementById("select_reason");
    document.getElementById('comment_text').value = e.options[e.selectedIndex].value;
}
