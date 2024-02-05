$(function () {

    // Dashboard chart colors
    const body_styles = window.getComputedStyle(document.body);
    const colors = {
        primary: $.trim(body_styles.getPropertyValue('--bs-primary')),
        secondary: $.trim(body_styles.getPropertyValue('--bs-secondary')),
        info: $.trim(body_styles.getPropertyValue('--bs-info')),
        success: $.trim(body_styles.getPropertyValue('--bs-success')),
        danger: $.trim(body_styles.getPropertyValue('--bs-danger')),
        warning: $.trim(body_styles.getPropertyValue('--bs-warning')),
        light: $.trim(body_styles.getPropertyValue('--bs-light')),
        dark: $.trim(body_styles.getPropertyValue('--bs-dark')),
        blue: $.trim(body_styles.getPropertyValue('--bs-blue')),
        indigo: $.trim(body_styles.getPropertyValue('--bs-indigo')),
        purple: $.trim(body_styles.getPropertyValue('--bs-purple')),
        pink: $.trim(body_styles.getPropertyValue('--bs-pink')),
        red: $.trim(body_styles.getPropertyValue('--bs-red')),
        orange: $.trim(body_styles.getPropertyValue('--bs-orange')),
        yellow: $.trim(body_styles.getPropertyValue('--bs-yellow')),
        green: $.trim(body_styles.getPropertyValue('--bs-green')),
        teal: $.trim(body_styles.getPropertyValue('--bs-teal')),
        cyan: $.trim(body_styles.getPropertyValue('--bs-cyan')),
        chartTextColor: $('body').hasClass('dark') ? '#6c6c6c' : '#b8b8b8',
        chartBorderColor: $('body').hasClass('dark') ? '#444444' : '#ededed',
    };

    function downloadChart() {
        if ($('#download-chart').length) {
            let options = {
                series: [{
                    name: 'Download',
                    data: [70, 40, 90, 70, 42, 109, 90]
                }],
                chart: {
                    height: 180,
                    type: 'area',
                    sparkline: {
                        enabled: true
                    }
                },
                colors: [colors.success],
                dataLabels: {
                    enabled: false
                },
                theme: {
                    mode: $('body').hasClass('dark') ? 'dark' : 'light',
                },
                stroke: {
                    curve: 'smooth',
                    width: 1
                },
                xaxis: {
                    type: 'datetime',
                    categories: ["2018-09-19T00:00:00.000Z", "2018-09-19T01:30:00.000Z", "2018-09-19T02:30:00.000Z", "2018-09-19T03:30:00.000Z", "2018-09-19T04:30:00.000Z", "2018-09-19T05:30:00.000Z", "2018-09-19T06:30:00.000Z"]
                },
                tooltip: {
                    x: {
                        format: 'dd/MM/yy HH:mm'
                    },
                },
            };

            new ApexCharts(document.querySelector("#download-chart"), options).render();
        }
    }

    downloadChart();

    function uploadChart() {
        if ($('#upload-chart').length) {
            let options = {
                series: [{
                    name: 'Upload',
                    data: [80, 70, 90, 70, 90, 50, 90]
                }],
                chart: {
                    height: 180,
                    type: 'area',
                    sparkline: {
                        enabled: true
                    }
                },
                colors: [colors.warning],
                dataLabels: {
                    enabled: false
                },
                stroke: {
                    curve: 'smooth',
                    width: 2
                },
                xaxis: {
                    type: 'datetime',
                    categories: ["2018-09-19T00:00:00.000Z", "2018-09-19T01:30:00.000Z", "2018-09-19T02:30:00.000Z", "2018-09-19T03:30:00.000Z", "2018-09-19T04:30:00.000Z", "2018-09-19T05:30:00.000Z", "2018-09-19T06:30:00.000Z"]
                },
                tooltip: {
                    x: {
                        format: 'dd/MM/yy HH:mm'
                    },
                },
            };

            new ApexCharts(document.querySelector("#upload-chart"), options).render();
        }
    }

    uploadChart();

    $.fn.hasAttr = function(name) {
        return this.attr(name) !== undefined;
    };

    // $('.slick-folder-lists').slick({
    //     autoplay: true,
    //     autoplaySpeed: 1500,
    //     prevArrow: $('.slick-folder-lists-prev-arrow'),
    //     nextArrow: $('.slick-folder-lists-next-arrow'),
    //     rtl: $('html').hasAttr('dir') ? true : false
    // });

    function storage() {
        let options4 = {
            labels: ["Images", "Videos", "Music", "Documents"],
            series: [8, 5, 7, 9],
            chart: {
                type: 'donut',
                width: 180,
                height: 180,
                sparkline: {
                    enabled: true
                }
            },
            stroke: {
                width: 0
            },
            colors: [colors.info, colors.warning, colors.success, colors.secondary],
            tooltip: {
                fixed: {
                    enabled: false,
                },
                y: {
                    formatter: function (value) {
                        return value.toString() + ' GB';
                    }
                }
            }
        };

        new ApexCharts(document.querySelector("#storage"), options4).render();
    }

    // storage();

    if (document.getElementById('upgrade-toast')) {
        $(window).on('load', function () {
            setTimeout(function () {
                new bootstrap.Toast(document.getElementById('upgrade-toast'), {
                    autohide: false
                }).show();
            }, 2000);
        });
    }

});
