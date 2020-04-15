var Plottype = {
    Winrate: {
        Ascending: "ascending",
        Descending: "descending"
    }
}

var templateWinratePlot;
function drawWinratePlot(winrates, formattedWinrates, totalGames, ticks, colors) {
    if (templateWinratePlot) {
        templateWinratePlot.destroy();
    }

    var maxNumOfBars = 20;
    templateWinratePlot = $.jqplot('templateWinrates', [winrates.slice(0, maxNumOfBars)], {
        animate: true,
        animateReplot: true,
        title: 'Winrate per template',
        height: 400,
        seriesColors: colors,
        seriesDefaults: {
            renderer: $.jqplot.BarRenderer,
            pointLabels: {
                show: true,
                labels: formattedWinrates.slice(0, maxNumOfBars)
            }, rendererOptions: {
                varyBarColor: true,
            }
        },
        axesDefaults: {
            tickRenderer: $.jqplot.CanvasAxisTickRenderer,

        },
        axes: {
            xaxis: {
                ticks: ticks.slice(0, maxNumOfBars),
                renderer: $.jqplot.CategoryAxisRenderer,
                tickOptions: {
                    angle: -60,
                },
            },
            yaxis: {
                ticks: [[-0.1, " "], [0, "0%"], [0.25, "25%"], [0.5, "50%"], [0.75, "75%"], [1, "100%"], [1.15, " "]],
            },
        },
        highlighter: {
            show: true,
            sizeAdjust: 3,
            tooltipContentEditor: function (str, seriesIndex, pointIndex, jqPlot) {
                $(".jqplot-highlighter-tooltip").css("left", "0")
                return ticks[pointIndex] + ": " + formattedWinrates[pointIndex] + " (" + totalGames[pointIndex] + " games)"

            },
            tooltipLocation: "ne"
        }
    }).replot();
}

function descendingWinrateSort(x, y) {
    return y.winrate - x.winrate
}

function ascendingWinrateSort(x, y) {
    return x.winrate - y.winrate
}

function getRGB(r, g, b) {
    return "rgb(" + r + ", " + g + ", " + b + ")";
}
