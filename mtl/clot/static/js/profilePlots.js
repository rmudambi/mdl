$(document).ready(function () {

    plotPoints = plotPoints.filter(function (p) { return p[1] > 0 && p[2] > 0 })

    maxRating = Math.max.apply(Math, plotPoints.map(function (o) { return o[2]; }))
    minRating = Math.min.apply(Math, plotPoints.map(function (o) { return o[2]; }))
    maxRank = Math.max.apply(Math, plotPoints.map(function (o) { return o[1]; }))
    minRank = Math.min.apply(Math, plotPoints.map(function (o) { return o[1]; }))

    var ratingPoints = [];
    var rankPoints = [];
    $.each(plotPoints, function (k, plotPoint) {
        ratingPoints.push([plotPoint[0], Number(plotPoint[2])])
        rankPoints.push([plotPoint[0], Number(plotPoint[1])])
    })

    if (rankPoints.length == 0) {
        $("#playerRating").html("Graphs will be displayed as soon as this player has been ranked for at least one day.").css("color", "gray")
    } else {
        $.jqplot.config.enablePlugins = true;

        /***** Rating Plot *****/
        var ratingPlot = $.jqplot('playerRating', [ratingPoints], {
            title: 'Rating History',
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
                    tickOptions: { formatString: '%d' }
                },
            },
            cursor: {
                zoom: true,
                clickReset: true,
                constrainZoomTo: 'x'
            }
        });


        /***** Rank Plot *****/
        var tickStep = Math.ceil((maxRank - minRank + 2) / 4)
        var minTick = Math.max(minRank - 2, 0)
        var rankTicks = Array(5).fill().map(function (k, v) { return minTick + (4 - v) * tickStep });

        var rankPlot = $.jqplot('playerRank', [rankPoints], {
            title: 'Rank History',
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
                    tickOptions: { formatString: '%d' },
                    ticks: rankTicks
                },
            },
            cursor: {
                zoom: true,
                clickReset: true,
                constrainZoomTo: 'x'
            }
        });
    }
    if(template_winrates.length > 0) {
        /***** Template Winrate Plot *****/
        createWinratePlot(Plottype.Winrate.Descending, false);

        
        //$("#templateWinrates").after("<div><button onclick='createWinratePlotDescending()'>Best</button><button onclick='createWinratePlotAscending()'>Worst</button></div>")
    }
});

function createWinratePlot(mode, showBlacklisted) {
    var current_template_winrates;
    if (mode == Plottype.Winrate.Descending) {
        current_template_winrates = template_winrates.sort(descendingWinrateSort);
    } else {
        current_template_winrates = template_winrates.sort(ascendingWinrateSort);
    }

    if (!showBlacklisted) {
        current_template_winrates = template_winrates.filter(function (template) {
            return blacklisted_templates[template.id] == undefined
        })
    }

    var winrates = current_template_winrates.map(function (x) { return Number(x.winrate) });
    var formattedWinrates = winrates.map(function (x) { return Math.round(x * 100) + "%" });
    var totalGames = current_template_winrates.map(function (x) { return x.totalGames });
    var ticks = current_template_winrates.map(function (x) { return $("<div/>").html(x.name).text() });

    var colors = current_template_winrates.map(function (template) {
        var color;
        if (showBlacklisted && blacklisted_templates[template.id] != undefined) {
            //set color for blacklisted template
            color = getRGB(109, 109, 109);
            color = getRGB(50, 50, 50);
        } else {
            //calculate green to red shades for winrates
            r = Math.round(255 * (1 - template.winrate));
            g = Math.round(255 * template.winrate);
            color = getRGB(r, g, 0);
        }
        return color
    })

    drawWinratePlot(winrates, formattedWinrates, totalGames, ticks, colors);
}

$(".winRatePlotNavigation input").on("change", function(){
    var showBlacklisted = $("input[name='showBlacklisted']").is(":checked");
    var sortDirection = $('input[name=winRateSort]:checked').val();

    if (sortDirection == Plottype.Winrate.Ascending) {
        $(".winrate-descending").removeClass("selected")
        $(".winrate-ascending").addClass("selected")
    } else if (sortDirection == Plottype.Winrate.Descending) {
        $(".winrate-descending").addClass("selected")
        $(".winrate-ascending").removeClass("selected")
    }

    createWinratePlot(sortDirection, showBlacklisted)
})
