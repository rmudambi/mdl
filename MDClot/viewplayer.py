from flask import Blueprint, render_template, abort, session, request, redirect
from jinja2 import TemplateNotFound, filters
from lot import LOTContainer
from utilities.DAL import find_player, find_all_games, find_vetoes, find_history_records, find_notable_games, find_game
import sqlite3
from config.ClotConfig import ClotConfig
from datetime import datetime


view_player_page = Blueprint('view_player_page', __name__,
                        template_folder='templates', static_folder="/static")

#This page follows the instructions at http://wiki.warlight.net/index.php/CLOT_Authentication
@view_player_page.route('/player')
def show():
    try:
        player_id = int(request.args.get('playerId'))
    except:
        redirect("/")
    conn = sqlite3.connect(ClotConfig.database_location) # or use :memory: to put it in RAM
    player = find_player(conn, player_id)
    games = find_all_games(conn, player_id)
    history = find_history_records(conn, player_id=player_id)

    container = LOTContainer()
    players_ranked_nearby = []
    if container.sorted_ranked_players is not None:
        player_rank = [i for i, p in enumerate(container.sorted_ranked_players) if p.player_id == player.player_id]
        if len(player_rank) == 1:
            # Add one since rank = index + 1
            player.rank = player_rank[0] + 1
            (start_rank, end_Rank) = find_ranks_nearby(player.rank, len(container.sorted_ranked_players))
            for j in range(start_rank, end_Rank + 1):
                players_ranked_nearby.append((j, container.sorted_ranked_players[j-1]))
    
    finished_games = []
    ongoing_games = []
    for game in games:
        if game.finish_date is not None:
            finished_games.append(game)
        else:
            ongoing_games.append(game)

    finished_games = sorted(finished_games, key=lambda game: game.finish_date, reverse=True)
    sorted_games = ongoing_games
    sorted_games.extend(finished_games)

    currentPlayer = None
    current_vetoes = {}
    notable_games = []
    current_player_notable_games = []
    templates = ClotConfig.template_names
    retired_templates = ClotConfig.retired_template_names

    if 'authenticatedtoken' in session:
        inviteToken = session['authenticatedtoken']
        currentPlayer = find_player(conn, (inviteToken))
        for veto in find_vetoes(conn, currentPlayer.player_id, ClotConfig.template_veto_count):
            current_vetoes[veto[1]] = True
        
        # Find the logged-in player's notable games(needed for the settings drop-down)
        for notable_game_tuple in find_notable_games(conn, currentPlayer.player_id, ClotConfig.notable_game_count):
            current_player_notable_games.append(find_game(conn, notable_game_tuple[1]))

    if currentPlayer is not None and player.player_id == currentPlayer.player_id:
        notable_games = current_player_notable_games
    else:
        # Find the page player's notable games(needed for the notable games table)
        for notable_game_tuple in find_notable_games(conn, player_id, ClotConfig.notable_game_count):
            notable_game = find_game(conn, notable_game_tuple[1])
            if notable_game is not None:
                notable_games.append(notable_game)

    template_stats_win = templateFrequencyDistribution(list([x.template for x in filter(lambda x: x.winner == player.player_id , finished_games)]))
    template_stats_lost = templateFrequencyDistribution(list([x.template for x in filter(lambda x: x.winner != player.player_id , finished_games)]))

    template_winrates = []
    for key, value in templates.items():
        total_games = (template_stats_win.get(str(key), 0) + template_stats_lost.get(str(key), 0))
        won_games = template_stats_win.get(str(key), 0)
        winrate = won_games / max(1, total_games)
        if total_games >= 2 :
            template_winrates.append({"name": value, "winrate": winrate, "totalGames": total_games, "id": key})

    #template_winrates.sort(key=lambda x: x["winrate"], reverse=True)
    #template_winrates = template_winrates[:20]

    return render_template('viewplayer.html', player = player, games= sorted_games, currentPlayer=currentPlayer, container = container, 
                           templates = templates, retired_templates = retired_templates, current_vetoes = current_vetoes, history = history, 
                           template_winrates = template_winrates, players_ranked_nearby = players_ranked_nearby, notable_games = notable_games,
                           current_player_notable_games = current_player_notable_games)

def templateFrequencyDistribution(data):
    return {i: data.count(i) for i in data}

def find_ranks_nearby(current_rank, total_players):
    if current_rank <= 5:
        start_rank = 1
        end_Rank = 11
    elif current_rank + 5 > total_players:
        start_rank = total_players - 11
        end_Rank = total_players
    else:
        start_rank = current_rank - 5
        end_Rank = current_rank + 5

    return (start_rank, end_Rank)
