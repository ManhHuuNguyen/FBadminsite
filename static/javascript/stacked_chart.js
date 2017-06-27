var admins = angular.element(document.getElementById("angular_app")).scope().admins;
var names = [];
var post_deleted = [];
var user_banned = [];
for (var i=0; i< admins.length; i++){
    names.push(admins[i][0]);
    post_deleted.push(admins[i][1]);
    user_banned.push(admins[i][2]);
}
Highcharts.chart('admin_chart', {
    chart: {
        type: 'column'
    },
    title: {
        text: "Admins' Stats Chart"
    },
    xAxis: {
        categories: names
    },
    yAxis: {
        min: 0,
        title: {
            text: 'Total activity'
        },
        stackLabels: {
            enabled: true,
            style: {
                fontWeight: 'bold',
                color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
            }
        }
    },
    legend: {
        align: 'right',
        x: -30,
        verticalAlign: 'top',
        y: 25,
        floating: true,
        backgroundColor: (Highcharts.theme && Highcharts.theme.background2) || 'white',
        borderColor: '#CCC',
        borderWidth: 1,
        shadow: false
    },
    tooltip: {
        headerFormat: '<b>{point.x}</b><br/>',
        pointFormat: '{series.name}: {point.y}<br/>Total: {point.stackTotal}'
    },
    plotOptions: {
        column: {
            stacking: 'normal',
            dataLabels: {
                enabled: true,
                color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white'
            }
        }
    },
    series: [{
        name: 'POST DELETED',
        data: post_deleted
    }, {
        name: 'USER BANNED',
        data: user_banned
    }]
});