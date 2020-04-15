$(document).ready(function () {

    if (template_winrates.length > 0) {
        /***** Template Winrate Plot *****/
        createWinratePlot(Plottype.Winrate.Descending);
    }
});

function createWinratePlot(mode) {
    var current_template_winrates;
    if (mode == Plottype.Winrate.Descending) {
        current_template_winrates = template_winrates.sort(descendingWinrateSort);
    } else {
        current_template_winrates = template_winrates.sort(ascendingWinrateSort);
    }

    var winrates = current_template_winrates.map(function (x) { return Number(x.winrate) });
    var formattedWinrates = winrates.map(function (x) { return Math.round(x * 100) + "%" });
    var totalGames = current_template_winrates.map(function (x) { return x.totalGames });
    var ticks = current_template_winrates.map(function (x) { return $("<div/>").html(x.name).text() });

    var colors = current_template_winrates.map(function (template) {
        var color;
        //calculate green to red shades for winrates
        r = Math.round(255 * (1 - template.winrate));
        g = Math.round(255 * template.winrate);
        color = getRGB(r, g, 0);
        
        return color;
    })

    drawWinratePlot(winrates, formattedWinrates, totalGames, ticks, colors);
}

$(".winRatePlotNavigation input").on("change", function () {
    var sortDirection = $('input[name=winRateSort]:checked').val();

    if (sortDirection == Plottype.Winrate.Ascending) {
        $(".winrate-descending").removeClass("selected")
        $(".winrate-ascending").addClass("selected")
    } else if (sortDirection == Plottype.Winrate.Descending) {
        $(".winrate-descending").addClass("selected")
        $(".winrate-ascending").removeClass("selected")
    }

    createWinratePlot(sortDirection)
})