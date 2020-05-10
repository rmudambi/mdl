from datetime import datetime
import random

import sqlite3

from mtl.ladder.config import clot_config
from mtl.ladder.utilities.api import deleteGame, APIError
from mtl.ladder.utilities.clan_league_logging import get_logger
from mtl.ladder.utilities.dal import find_game, update_game

logger = get_logger()


DEFAULT_GAME_MESSAGE = ("This game has been created by MTL. If you fail to join it within 3 days, vote to end or "
                        "decline, " "it will count as a loss. For latest standings, please visit "
                        "http://md-ladder.cloudapp.net/")
GAME_SHEET_NAME = "All Games"


class GameState:
    in_progress = "In Progress"
    won = "Won"
    loss = "Loss"
    not_started = ''


def get_game_name(team_a, team_b):
    team_a = team_a[:18]
    team_b = team_b[:18]
    name = "{0}|{1} vs {2}".format(clot_config.TOURNAMENT_NAME, team_a, team_b)
    name = name[:50]

    return name


def update_game_winner(api_response, teams, is_any_player_on_vacation):
    game_id = api_response.get('id')
    state = api_response.get('state')

    conn = sqlite3.connect(clot_config.DATABASE_LOCATION)  # or use :memory: to put it in RAM
    game = find_game(conn, game_id)

    winner = None
    if state == 'Finished':
        # It's finished. Record the winner and save it back.
        winner = parse_winner(api_response)
    elif state == 'WaitingForPlayers':
        if not is_any_player_on_vacation:
            # Strip off the tick info.
            created_date = datetime.strptime(game.created_date[:game.created_date.rindex(" ")+9],
                                             '%Y-%m-%d %H:%M:%S')
            # It's in the lobby still. Check if it's been too long.
            elapsed = datetime.now() - created_date
            if elapsed.days < clot_config.MAX_DAYS_TO_JOIN_GAME:
                logger.info(f"Game {game_id} is in the lobby for {elapsed} days.")
            else:
                logger.info(f"Game {game_id} is stuck in the lobby. Marking it as a loss for anyone who didn't "
                            f"join and deleting it.")

                try:
                    # Delete it over at warlight.net so that players know we no longer consider it a real game
                    deleteGame(clot_config.EMAIL, clot_config.TOKEN, game_id)

                    # Update IsGameDeleted to true.
                    game.is_game_deleted = True

                    winner = parse_winner_of_deleted_game(api_response)
                    logger.info("Game %s was marked deleted", game_id)
                except APIError:
                    # If the API doesn't return success, just ignore this game on this run. This can happen if the
                    # game just started between when we checked its status and when we told it to delete.
                    logger.info(f"Delete game {game_id} did not return success. Ignoring this game for this run.")
        else:
            logger.info("The game is waiting on one of the players who is on vacation")
    else:
        # It's still going.
        logger.info(f'Game {game_id} is not finished, state = {state}, numTurns= {api_response["numberOfTurns"]}')

    if winner is not None:
        # Update game with result
        game.winner = teams[int(winner)]
        conn = sqlite3.connect(clot_config.DATABASE_LOCATION)  # or use :memory: to put it in RAM
        update_game(conn, game)


def parse_winner(api_response):
    """Simple helper function to return the Player who won the game.  This takes json data returned by the GameFeed
    API.  We just look for a player with the "won" state."""
    winners = [p for p in api_response['players'] if p['state'] == 'Won']
    if len(winners) == 0:
        # The only way there can be no winner is if the players VTE.  Just pick one at random.
        return random.choice(api_response['players'])["team"]
    else:
        return winners[0]["team"]


def parse_winner_of_deleted_game(api_response):
    """Simple helper function to return the Player who should be declared the winner of a game that never began.
    If it didn't begin, it's because someone either didn't join the game or declined it.  They'll be considered
    the loser, so whoever joined is the winner by default."""
    joined = [p for p in api_response['players'] if p['state'] == 'Playing']
    if len(joined) > 0:
        return random.choice(joined)["team"]

    """If everyone declined or failed to join, we just pick the winner randomly."""
    return random.choice(api_response['players'])["team"]
