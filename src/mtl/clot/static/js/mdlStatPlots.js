$(document).ready(function () {
    plotTotalGamesGraph();
    plotGamesPerDayGraph();
    plotRatingGraph();

    var vetoes_per_template = vetoPoints.map(function (x) { return Number(x[1]) });
    var ticks = vetoPoints.map(function (x) { return $("<div/>").html(x[0]).text() });

    drawWinratePlot(vetoes_per_template, ticks);
});

var templateVetoPlot;
function drawWinratePlot(vetoes_per_template, ticks) {
    if (templateVetoPlot) {
        templateVetoPlot.destroy();
    }

    templateVetoPlot = $.jqplot('templatesVetoed', [vetoes_per_template], {
        animate: true,
        animateReplot: true,
        title: 'Vetoes per template',
        height: 400,
        seriesDefaults: {
            renderer: $.jqplot.BarRenderer,
        },
        axesDefaults: {
            tickRenderer: $.jqplot.CanvasAxisTickRenderer,
        },
        axes: {
            xaxis: {
                ticks: ticks,
                renderer: $.jqplot.CategoryAxisRenderer,
                tickOptions: {
                    angle: -60,
                },
            }
        },
        highlighter: {
            show: true,
            sizeAdjust: 3,
            tooltipContentEditor: function (str, seriesIndex, pointIndex, jqPlot) {
                $(".jqplot-highlighter-tooltip").css("left", "0")
                return vetoes_per_template[pointIndex]
            },
            tooltipLocation: "ne"
        }
    }).replot();
}

function plotRatingGraph() {
    inputPoints = plotPoints.filter(function (p) { return p[1] > 0 })
    maxPoint = Math.max.apply(Math, inputPoints.map(function (o) { return o[1]; }))
    minPoint = Math.min.apply(Math, inputPoints.map(function (o) { return o[1]; }))

    var yPoints = [];
    $.each(inputPoints, function (k, plotPoint) {
        yPoints.push([Number(plotPoint[0]) / inputPoints.length * 100, Number(plotPoint[1])]);
    })

    if (yPoints.length == 0) {
        $('#ratingDistribution').html("Graphs will be displayed as soon as data is available.").css("color", "gray")
    } else {
        $.jqplot.config.enablePlugins = true;

        var plot = $.jqplot('ratingDistribution', [yPoints], {
            height: 350,
            title: 'Rating Distribution',
            animate: true,
            seriesDefaults: {
                pointLabels: {
                    show: false
                },
            },
            axes: {
                xaxis: {
                    label: 'Percentile'
                },
                yaxis: {
                    label: 'Rating'
                },
            },
            cursor: {
                zoom: true,
                clickReset: true,
                constrainZoomTo: 'x'
            }
        });
    }
}

function plotTotalGamesGraph() {
    inputPoints = total_games_over_time.filter(function (p) { return p[1] > 0 })

    maxPoint = Math.max.apply(Math, inputPoints.map(function (o) { return o[1]; }))
    minPoint = Math.min.apply(Math, inputPoints.map(function (o) { return o[1]; }))

    var yPoints = [];
    $.each(inputPoints, function (k, plotPoint) {
        yPoints.push([plotPoint[0], Number(plotPoint[1])]);
    })

    if (yPoints.length == 0) {
        $('#totalGames').html("Graphs will be displayed as soon as data is available.").css("color", "gray")
    } else {
        $.jqplot.config.enablePlugins = true;

        var plot = $.jqplot('totalGames', [yPoints], {
            height: 350,
            title: 'Total Games',
            animate: true,
            seriesDefaults: {
                pointLabels: {
                    show: false
                },
            },
            axes: {
                xaxis: {
                    renderer: $.jqplot.DateAxisRenderer,
                    tickOptions: { formatString: '%e. %b' }
                },
                yaxis: {
                    label: '#Games',
                    tickOptions: { formatString: '%d' }
                },
            },
            cursor: {
                zoom: true,
                clickReset: true,
                constrainZoomTo: 'x'
            }
        });
    }
}

function plotGamesPerDayGraph() {
    inputPoints = games_per_day_over_time.filter(function (p) { return p[1] > 0 })

    maxPoint = Math.max.apply(Math, inputPoints.map(function (o) { return o[1]; }))
    minPoint = Math.min.apply(Math, inputPoints.map(function (o) { return o[1]; }))

    var yPoints = [];
    $.each(inputPoints, function (k, plotPoint) {
        yPoints.push([plotPoint[0], Number(plotPoint[1])]);
    })

    if (yPoints.length == 0) {
        $('#gamesPerDay').html("Graphs will be displayed as soon as data is available.").css("color", "gray")
    } else {
        $.jqplot.config.enablePlugins = true;

        var plot = $.jqplot('gamesPerDay', [yPoints], {
            height: 350,
            title: 'Games per day',
            animate: true,
            seriesDefaults: {
                pointLabels: {
                    show: false
                },
            },
            axes: {
                xaxis: {
                    renderer: $.jqplot.DateAxisRenderer,
                    tickOptions: { formatString: '%e. %b' }
                },
                yaxis: {
                    label: '#Games',
                    tickOptions: { formatString: '%d' }
                },
            },
            cursor: {
                zoom: true,
                clickReset: true,
                constrainZoomTo: 'x'
            }
        });
    }
}