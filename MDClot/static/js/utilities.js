$.fn.pageMe = function(opts){
    var $this = this,
        defaults = {
            perPage: 7,
            showPrevNext: false,
            hidePageNumbers: false
        },
        settings = $.extend(defaults, opts);
    
    var listElement = $this;
    var perPage = settings.perPage; 
    var children = listElement.children();
    var pager = $('.pager');
    
    if (typeof settings.childSelector!="undefined") {
        children = listElement.find(settings.childSelector);
    }
    
    if (typeof settings.pagerSelector!="undefined") {
        pager = $(settings.pagerSelector);
    }
    
    var numItems = children.size();
    var numPages = Math.ceil(numItems/perPage);

    pager.data("curr",0);
    
    if (settings.showPrevNext){
        $('<li><a href="#" class="prev_link">«</a></li>').appendTo(pager);
    }
    
    var curr = 0;
    while(numPages > curr && (settings.hidePageNumbers==false)){
        $('<li><a href="#" class="page_link">'+(curr+1)+'</a></li>').appendTo(pager);
        curr++;
    }
    
    if (settings.showPrevNext){
        $('<li><a href="#" class="next_link">»</a></li>').appendTo(pager);
    }
    
    pager.find('.page_link:first').addClass('active');
    pager.find('.prev_link').hide();
    if (numPages<=1) {
        pager.find('.next_link').hide();
    }
  	pager.children().eq(1).addClass("active");
    
    children.hide();
    children.slice(0, perPage).show();
    
    pager.find('li .page_link').click(function(){
        var clickedPage = $(this).html().valueOf()-1;
        goTo(clickedPage,perPage);
        return false;
    });
    pager.find('li .prev_link').click(function(){
        previous();
        return false;
    });
    pager.find('li .next_link').click(function(){
        next();
        return false;
    });
    
    function previous(){
        var goToPage = parseInt(pager.data("curr")) - 1;
        goTo(goToPage);
    }
     
    function next(){
        goToPage = parseInt(pager.data("curr")) + 1;
        goTo(goToPage);
    }
    
    function goTo(page){
        var startAt = page * perPage,
            endOn = startAt + perPage;
        
        children.css('display','none').slice(startAt, endOn).show();
        
        if (page>=1) {
            pager.find('.prev_link').show();
        }
        else {
            pager.find('.prev_link').hide();
        }
        
        if (page<(numPages-1)) {
            pager.find('.next_link').show();
        }
        else {
            pager.find('.next_link').hide();
        }
        
        pager.data("curr",page);
      	pager.children().removeClass("active");
        pager.children().eq(page+1).addClass("active");
    
    }
};



$(document).ready(function(){
    
    // Format date to user's local time
    $(".dateTimeString").each(function () {
        var utc = $(this).text();
        $(this).text(function () {
            utc = utc + "Z";
            utc = utc.replace(" ", "T");
            var date = new Date(utc);
            return date.toLocaleDateString() + " " + date.toLocaleTimeString();
        });
    });

    // Format date to user's local time
    $(".dateString").each(function () {
        var utc = $(this).text();
        $(this).text(function () {
            utc = utc + "Z";
            utc = utc.replace(" ", "T");
            var date = new Date(utc);
            return date.toLocaleDateString();
        });
    });

    $("#profileGamesTable").DataTable({
        "order": [3],
        "paging": true,
        "pageLength": 10,
        "sDom": '<"datatableWrapper"pti',
        "columnDefs": [{
            targets: [0],
            sortable: false
        }, {
            targets: [1],
            sortable: false
        }, {
            targets: [2],
            orderData: [2, 3],
        }, {
            targets: [3],
            orderData: [3, 2],
        }, {
            targets: [4],
            orderData: [4, 3]
        }],
        "aoColumns": [
            { "orderSequence": ["asc", "desc"] },
            { "orderSequence": ["asc", "desc"] },
            { "orderSequence": ["asc", "desc"] },
            { "orderSequence": ["asc", "desc"] },
            { "orderSequence": ["desc", "asc"] }
        ],
        "language": {
            "zeroRecords": "No games created yet",
            "info": "Showing _START_ to _END_ of _TOTAL_ games",
            "infoEmpty": "Showing 0 to 0 of 0 games",
            "infoFiltered": "(filtered from _MAX_ total games)",
        },
    });

    $("#profileTemplateGamesTable").DataTable({
        "order": [2],
        "paging": true,
        "pageLength": 15,
        "sDom": '<"datatableWrapper"pti',
        "columnDefs": [{
            targets: [0],
            sortable: false
        }, {
            targets: [1],
            sortable: false
        }, {
            targets: [2],
            orderData: [2],
        }, {
            targets: [3],
            sortable: false
        }],
        "aoColumns": [
            { "orderSequence": ["asc", "desc"] },
            { "orderSequence": ["asc", "desc"] },
            { "orderSequence": ["asc", "desc"] },
            { "orderSequence": ["desc", "asc"] }
        ],
        "language": {
            "zeroRecords": "No games created yet",
            "info": "Showing _START_ to _END_ of _TOTAL_ games",
            "infoEmpty": "Showing 0 to 0 of 0 games",
            "infoFiltered": "(filtered from _MAX_ total games)",
        },
    });

    $("#latestGamesTable").DataTable({
        "paging": true,
        "pageLength": 15,
        "sDom": '<"datatableWrapper"pti',
        "bSort" : false,
        "language": {
            "zeroRecords": "No games created yet",
            "info": "Showing _START_ to _END_ of _TOTAL_ games",
            "infoEmpty": "Showing 0 to 0 of 0 games",
            "infoFiltered": "(filtered from _MAX_ total games)",
        },
    });
 
    $("#allPlayersTable").DataTable({
        "paging": true,
        "pageLength": 20,
        "sDom": '<"datatableWrapper"pti',
        "bSort": false,
        "language": {
            "zeroRecords": "No players.",
            "info": "Showing _START_ to _END_ of _TOTAL_ players",
            "infoEmpty": "Showing 0 to 0 of 0 players",
            "infoFiltered": "(filtered from _MAX_ total players)",
        },
    });

    //#myInput is a <input type="text"> element
    $('.table_search').on('keyup', function () {
        if ($(this).parent().parent().parent().parent()) {
            $(this).parent().parent().parent().parent().DataTable().search(this.value).draw();
        }
    });

    $("#reportTable").DataTable({
        "order": [[1, "asc"]],
        "paging": true,
        "pageLength": 20,
        "sDom": '<"datatableWrapper"pti',
        "columnDefs": [{
            targets: [0],
            sortable: false
        }, {
            targets: [1],
            orderData: 1
        }, {
            targets: [2],
            orderData: 2
        }, {
            targets: [3],
            orderData: 3
        }, {
            targets: [4],
            orderData: 4
        }, {
            targets: [5],
            orderData: 5
        }, {
            targets: [6],
            orderData: 6
        }, {
            targets: [7],
            orderData: 7
        }, {
            targets: [8],
            orderData: 8
        }],
        "language": {
            "zeroRecords": "No players.",
            "info": "Showing _START_ to _END_ of _TOTAL_ players",
            "infoEmpty": "Showing 0 to 0 of 0 players",
            "infoFiltered": "(filtered from _MAX_ total players)",
        },
    });

    $(".leaderboardTable").DataTable({
        "paging": true,
        "pageLength": 10,
        'sDom': '<"top"p>t<"bottom"i>',
        "pagingType":"simple",
        "bSort": false,
        "language": {
            "zeroRecords": "No records.",
            "info": "Showing _START_ to _END_ of _TOTAL_"
        },
    });

    $(".wins").attr("title", "Games won on MDL. Players must have completed 20 games to be listed.");
    $(".win_rate").attr("title", "Win % on MDL. Players must have completed 20 games to be listed.");
    $(".longest_win_streak").attr("title", "Players must have a win streak of 3 or more games to be listed.");
    $(".most_games_played").attr("title", "Players must have completed 20 games to be listed.");
    $(".first_rank").attr("title", "Sorted by max conescutive days the rank was held. If a player leaves the ladder(or goes on vacation) for a day, the counter is reset.");
    $(".clan_win_rate").attr("title", "Clans must have 3 or more active players on MDL.");
    $(".clan_players").attr("title", "Sorted by player rating in this order - ranked, unranked(active), unranked(inactive)");    

    var template_veto_count = 7;
    // Update veto templates
    $('#saveVetoedTemplates').on('click', function (e) {
        chosen_templates = $(".veto-checkboxes").find("input[type=checkbox]:checked");
        if (chosen_templates && chosen_templates.length <= template_veto_count) {
            template_ids = []
            chosen_templates.each(function (i, item) {
                template_ids.push(item.value);
            });
            templates = template_ids.join(",");
            window.location = '/veto?templates=' + templates;
        }
    });

    chosen_templates = $(".veto-checkboxes").find("input[type=checkbox]:checked");
    $(".numberOfVetoes").text(chosen_templates.length);
    $(".vetoes-container").on("click", function () {
        chosen_templates = $(".veto-checkboxes").find("input[type=checkbox]:checked");
        $(".numberOfVetoes").text(chosen_templates.length)
        if (chosen_templates && chosen_templates.length <= template_veto_count) {
            $('#saveVetoedTemplates').attr("disabled", false);
            $('#saveVetoedTemplates').removeAttr("title");
            if ($(".tooltip").is(":visible")) {
                $('#saveVetoedTemplates').tooltip("hide");
            }
        }
        else {
            $('#saveVetoedTemplates').attr("disabled", true);
            $('#saveVetoedTemplates').attr("title", "You can only veto up to " + template_veto_count + " templates");
            if (!$(".tooltip").is(":visible")) {
                $('#saveVetoedTemplates').tooltip("show");
            }  
        }
    });

    var notable_games_count = 5;
    // Update notable games
    $('#saveNotableGames').on('click', function (e) {
        notable_games = $(".notable-game");
        if (notable_games && notable_games.length <= notable_games_count) {
            game_ids = []
            notable_games.each(function (i, item) {
                var g_id = item.value;
                if (g_id != undefined && g_id != "") {
                    game_ids.push(Number(g_id));
                }
            });
            window.location = '/updatenotablegames?gameIds=' + game_ids.join(",");
        }
    });
    
    $(".notable-game").on("change", function () {
        if (!isNaN(this.value)) {
            $('#saveNotableGames').attr("disabled", false);
            $('#saveNotableGames').removeAttr("title");
            if ($(".tooltip").is(":visible")) {
                $('#saveNotableGames').tooltip("hide");
            }
        }
        else {
            $('#saveNotableGames').attr("disabled", true);
            $('#saveNotableGames').attr("title", "Invalid game Id.");
            if (!$(".tooltip").is(":visible")) {
                $('#saveNotableGames').tooltip("show");
            }
        }
    });

    $('ul.dropdown-menu li.dropdown-submenu > a').on('click', function (event) {
        // Avoid following the href location when clicking
        event.preventDefault();
        // Avoid having the menu to close when clicking
        event.stopPropagation();
    });
});

