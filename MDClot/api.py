from flask import Blueprint, jsonify, abort, make_response, request
from lot import LOTContainer
from config.ClotConfig import ClotConfig
from utilities.DAL import *
import sqlite3

api = Blueprint('api', __name__)

@api.route('/api/v1.0/players/', methods=['GET'])
def get_players():
    container = LOTContainer()
    players = []
    filtered_players = []
    if 'topk' in request.args and request.args['topk'].isdigit():
        topk = int(request.args['topk'])
        if topk <= len(container.players_sorted_by_rating):
            filtered_players = container.players_sorted_by_rating[:topk]
        else:
            filtered_players = container.players_sorted_by_rating
    else:
        # Get all players
        filtered_players = container.all_players.values()

    for player in filtered_players:
        record = populate_player_clan(player, container)
        players.append(record)

    return jsonify({'players': players})

@api.route('/api/v1.0/players/<int:player_id>', methods=['GET'])
def get_player(player_id):
    container = LOTContainer()
    if player_id in container.all_players:
        player = container.all_players[player_id]
        record = populate_player_clan(player, container)
        return jsonify({'player': record})
    abort(404)

@api.route('/api/v1.0/games/', methods=['GET'])
def get_games():
    conn = sqlite3.connect(ClotConfig.database_location)
    container = LOTContainer()
    games = []
    filtered_games = []
    if 'topk' in request.args and request.args['topk'].isdigit():
        topk = int(request.args['topk'])
    else:
        topk = 15
    filtered_games = find_recent_unexpired_games(conn, topk)
    for game in filtered_games:
        if not(game.team_a in container.all_players and game.team_b in container.all_players):
            abort(404)

        players = []
        players.append(populate_player_clan(container.all_players[game.team_a], container, isMinified=True))
        players.append(populate_player_clan(container.all_players[game.team_b], container, isMinified=True))
        record = game.serialize(players)
        games.append(record)

    return jsonify({'games': games})

@api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Resource does not exist on MDL'}), 404)


def populate_player_clan(player, container, isMinified=False):
    clan = None
    if player.clan in container.all_clans:
        clan = container.all_clans[player.clan]
    record = player.serialize(clan, isMinified)
    return record