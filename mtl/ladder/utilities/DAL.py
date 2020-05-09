import sqlite3
from mtl.ladder.entities.Clan import Clan
from mtl.ladder.entities.Game import Game
from mtl.ladder.entities.Player import Player
from mtl.ladder.entities.History import History
from mtl.ladder.config.ClotConfig import ClotConfig
from datetime import datetime, timedelta
from typing import List
 
sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))
 
def create_game_table(conn):
    # create a table
    cursor = conn.cursor() 
    cursor.execute("""CREATE TABLE Games
                        ("CreatedDate" timestamp, "FinishDate" timestamp, "GameId" INTEGER PRIMARY KEY, "GameLink" TEXT, "TeamA" INTEGER, 
                        "TeamB" INTEGER, "Winner" INTEGER, "IsRatingUpdated"  BOOLEAN, "IsGameDeleted"  BOOLEAN, "Template" INTEGER) 
                    """)

def create_leaderboard_table(conn):
    # create a table
    cursor = conn.cursor() 
    cursor.execute("""CREATE TABLE Leaderboard
                        ("CreatedDate" timestamp, "Metric" TEXT, "PlayerId" INTEGER, "Value" REAL) 
                    """)

def create_clan_leaderboard_table(conn):
    # create a table
    cursor = conn.cursor() 
    cursor.execute("""CREATE TABLE ClanLeaderboard
                        ("CreatedDate" timestamp, "ClanName" TEXT, "Metric" TEXT, "Value" REAL) 
                    """)

def create_player_table(conn):
    # create a table
    cursor = conn.cursor() 
    cursor.execute("""CREATE TABLE Players 
                        ("CreatedDate" timestamp, "Name" TEXT, "PlayerId" INTEGER PRIMARY KEY, "Rating" INTEGER, "IsRanked" BOOLEAN, "IsJoined" BOOLEAN, "MaxGames" INTEGER,
                        "BestRating" INTEGER,"BestRank" INTEGER,"Clan" TEXT,"ActivityBonus" FLOAT, "DisplayedRating" INTEGER, "BestDisplayedRating" INTEGER, "WaitCycles" INTEGER,
                        "Rank" INTEGER)
                    """)

def create_notable_games_table(conn):
    # create a table
    cursor = conn.cursor() 
    cursor.execute("""CREATE TABLE NotableGames ("CreatedDate" timestamp, "PlayerId" INTEGER, "GameId" INTEGER)""")

def create_veto_table(conn):
    # create a table
    cursor = conn.cursor() 
    cursor.execute("""CREATE TABLE Veto ("CreatedDate" timestamp, "PlayerId" INTEGER, "TemplateId" INTEGER) """)

def create_clans_table(conn):
    # create a table
    cursor = conn.cursor() 
    cursor.execute("""CREATE  TABLE "Clans" ("Id" INTEGER PRIMARY KEY  NOT NULL , "Name" TEXT, "LogoLink" TEXT) """)

def create_history_table(conn):
    # create a table
    cursor = conn.cursor() 
    cursor.execute("""CREATE  TABLE  IF NOT EXISTS "History" ("RecordedDate" timestamp NOT NULL , "PlayerId" INTEGER NOT NULL , "Rank" INTEGER, "Rating" INTEGER) """)

def create_stat_history_table(conn):
    # create a table
    cursor = conn.cursor() 
    cursor.execute("""CREATE TABLE IF NOT EXISTS "StatHistory" ("RecordedDate" timestamp NOT NULL, "MetricName" TEXT NOT NULL, "Value" FLOAT) """)


def insert_game(conn, game):
    cursor = conn.cursor() 
    args = (game.created_date, game.finish_date, game.game_id, game.game_link, game.team_a, game.team_b, game.winner, game.is_rating_updated, game.is_game_deleted, game.template)
    cursor.execute("INSERT INTO Games VALUES (?,?,?,?,?,?,?,?,?,?)", args)
    conn.commit()

def insert_player(conn, player_record) -> Player:
    """player_record = ("08/20/2016 - 01:19:25", "MotD", 11796766, 12345, 
                    1500, True, True, 5, None, None, False)
    """
    cursor = conn.cursor() 
    cursor.execute("INSERT INTO Players VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", player_record)
    conn.commit()

    if player_record is not None:
        player = Player(player_record)
    else:
        player = None

    return player

def insert_leaderboard(conn, leaderboard_record):
    """leaderboard_record = ("08/20/2016 - 01:19:25", "Top 10", 11796766, 83)
    """
    cursor = conn.cursor() 
    cursor.execute("INSERT INTO Leaderboard VALUES (?,?,?,?)", leaderboard_record)
    conn.commit()

def delete_leaderboard(conn, delete_time):
    cursor = conn.cursor() 
    cursor.execute("DELETE from mtl.clot.leaderboard WHERE CreatedDate < ?", (delete_time,))
    conn.commit()

def insert_clan_leaderboard(conn, clan_leaderboard_record):
    """leaderboard_record = ("08/20/2016 - 01:19:25", "MASTER", "Top 10", 83)
    """
    cursor = conn.cursor() 
    cursor.execute("INSERT INTO ClanLeaderboard VALUES (?,?,?,?)", clan_leaderboard_record)
    conn.commit()

def delete_clan_leaderboard(conn, delete_time):
    cursor = conn.cursor() 
    cursor.execute("DELETE FROM ClanLeaderboard WHERE CreatedDate < ?", (delete_time,))
    conn.commit()

def insert_notable_game(conn, notable_game_record):
    if len(notable_game_record) != 3:
        raise Exception("Invalid notable game record")

    cursor = conn.cursor()
    cursor.execute("INSERT INTO NotableGames VALUES (?,?,?)", notable_game_record)
    conn.commit()

def delete_notable_games(conn, player_id):
    cursor = conn.cursor() 
    cursor.execute("DELETE FROM NotableGames WHERE PlayerId = ?", (player_id,))
    conn.commit()

def insert_veto(conn, veto_record):
    if len(veto_record) != 3:
        raise Exception("Invalid veto record")

    cursor = conn.cursor()
    cursor.execute("INSERT INTO Veto VALUES (?,?,?)", veto_record)
    conn.commit()

def delete_vetoes(conn, player_id):
    cursor = conn.cursor() 
    cursor.execute("DELETE FROM Veto WHERE PlayerId = ?", (player_id,))
    conn.commit()

def insert_or_update_clan(conn, clan_record):
    if len(clan_record) != 3:
        raise Exception("Invalid clan record")

    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO Clans VALUES (?, ?, ?)", clan_record)
    conn.commit()

def insert_history_record(conn, history_record):
    """ Insert a history record. Each record uses the displayed_rating."""
    if len(history_record) != 4:
        raise Exception("Invalid history record")

    cursor = conn.cursor()
    cursor.execute("INSERT INTO History VALUES (?,?,?,?)", history_record)
    conn.commit()

def insert_stat_history_record(conn, stat_history_record):
    if len(stat_history_record) != 3:
        raise Exception("Invalid stat history record")

    cursor = conn.cursor()
    cursor.execute("INSERT INTO StatHistory VALUES (?,?,?)", stat_history_record)
    conn.commit()

def update_game(conn, game):
    cursor = conn.cursor() 
    query = 'UPDATE Games SET "FinishDate"=?, "Winner"=?, "IsRatingUpdated"=?, "IsGameDeleted"=? WHERE GameId=?'
    if game.finish_date is None:
        game.finish_date = datetime.now()
    cursor.execute(query, (game.finish_date, game.winner, game.is_rating_updated, game.is_game_deleted, game.game_id))
    conn.commit()

def update_games(conn, games):
    for game in games:
        update_game(conn, game)

def update_player(conn, player: Player) -> None:
    cursor = conn.cursor() 
    query = """UPDATE Players SET 'Name' = ?, 'Rating' = ?, 'IsRanked' = ?, 'IsJoined' = ?, 'MaxGames' = ?, 
        'BestRating' = ?, 'BestRank' = ?, 'Clan' = ?, 'ActivityBonus' = ?, 'DisplayedRating' = ?, 'BestDisplayedRating' = ?, 
        'WaitCycles' = ?, 'Rank' = ?, 'OnVacation' = ? WHERE PlayerId=?"""
    cursor.execute(query , (player.player_name, player.Rating, player.is_ranked, player.is_joined, player.max_games, 
                            player.best_rating, player.best_rank, player.clan, player.activity_bonus, player.displayed_rating, 
                            player.best_displayed_rating, player.wait_cycles, player.rank, player.on_vacation, player.player_id))
    conn.commit()

def update_players(conn, players):
    for player in players:
        update_player(conn, player)

def find_game(conn, game_id):
    cursor = conn.cursor() 
    cursor.execute('SELECT * FROM Games WHERE "GameId"=?', (game_id,))
    game_tuple= cursor.fetchone()

    if game_tuple is not None:
        game = Game(GameTuple=game_tuple)
    else:
        game = None

    return game

def find_player(conn, player_id):
    cursor = conn.cursor() 
    cursor.execute('SELECT * FROM Players WHERE "PlayerId"=?', (player_id,))
    player_tuple= cursor.fetchone()

    if player_tuple is not None:
        player = Player(player_tuple)
    else:
        player = None

    return player

def find_clan(conn, clan_id):
    cursor = conn.cursor() 
    cursor.execute('SELECT * FROM Clans WHERE "Id"=?', (clan_id,))
    clan_tuple= cursor.fetchone()

    if clan_tuple is not None:
        clan = Clan(clan_tuple)
    else:
        clan = None

    return clan

def find_all_clans(conn):
    cursor = conn.cursor() 
    cursor.execute('SELECT * FROM Clans')
    all_clan_tuples= cursor.fetchall()
    all_clans = []

    if all_clan_tuples is not None:
        for clan_tuple in all_clan_tuples:
            clan = Clan(clan_tuple)
            all_clans.append(clan)

    return all_clans

def find_notable_games(conn, player_id, number_of_notable_games):
    cursor = conn.cursor() 
    cursor.execute('SELECT DISTINCT CreatedDate, GameId FROM NotableGames WHERE "PlayerId"=? ORDER BY CreatedDate DESC LIMIT ?', (player_id, number_of_notable_games))
    game_tuples= cursor.fetchall()

    # Players can make multiple updates in a short period of time. If the latest update had less than N games, we want to avoid picking the last N games.
    # Check for the timestamp on each games in the TOP N(N=5). Any games updated before 2 seconds of the latest one, are considered part of a previous update. 
    games = []
    latest_update_time = None
    for game_tuple in game_tuples:
        tuple_update_time = datetime.strptime(game_tuple[0][:game_tuple[0].rindex(" ")+9], '%Y-%m-%d %H:%M:%S')
        if latest_update_time is None:
            latest_update_time = tuple_update_time
            games.append(game_tuple)
        else:
            elapsed = latest_update_time - tuple_update_time
            if elapsed.seconds < 2:
                games.append(game_tuple)

    return games

def find_vetoes(conn, player_id, number_of_vetos):
    cursor = conn.cursor() 
    cursor.execute('SELECT DISTINCT CreatedDate, TemplateId FROM Veto WHERE "PlayerId"=? ORDER BY CreatedDate DESC LIMIT ?', (player_id, number_of_vetos))
    template_tuples= cursor.fetchall()

    # Players can make multiple updates in a short period of time. If the latest update had less than N templates, we want to avoid picking the last N templates.
    # Check for the timestamp on each template in the TOP N(N=3). Any templates updated before 5 seconds of the latest one, are considered part of a previous update. 
    templates = []
    latest_update_time = None
    for template_tuple in template_tuples:
        tuple_update_time = datetime.strptime(template_tuple[0][:template_tuple[0].rindex(" ")+9], '%Y-%m-%d %H:%M:%S')
        if latest_update_time is None:
            latest_update_time = tuple_update_time
            templates.append(template_tuple)
        else:
            elapsed = latest_update_time - tuple_update_time
            if elapsed.seconds < 2:
                templates.append(template_tuple)

    return templates

def find_history_records(conn, recorded_date=None, player_id=None):
    cursor = conn.cursor()
    records = None 
    if recorded_date is not None:
        cursor.execute('SELECT * FROM History where RecordedDate=?', (recorded_date,))
        records = cursor.fetchone()
    elif player_id is not None:
        cursor.execute('SELECT * FROM History WHERE "PlayerId"=?', (player_id, ))
        records = cursor.fetchall()
        
    result = []
    if records is not None:
        if isinstance(records, tuple):
            history = History(HistoryTuple=records)
            result.append(history)
        else:
            for record in records:
                history = History(HistoryTuple=record)
                result.append(history)

    return result
  
def find_all_pending_games(conn):
    """ Find all on-going games whose winner is undecided
    """
    cursor = conn.cursor() 
    cursor.execute('SELECT * FROM Games WHERE "Winner" IS NULL')
    all_game_tuples= cursor.fetchall()
    all_games = []

    if all_game_tuples is not None:
        for game_tuple in all_game_tuples:
            game = Game(GameTuple=game_tuple)
            all_games.append(game)
    else:
        all_games = None

    return all_games

def find_all_recent_games(conn):
    """ Find all games in the past ClotConfig.min_days_between_rematch days. 
        Two players who have played recently cannot be matched again.
    """
    cursor = conn.cursor() 

    cursor.execute('SELECT * FROM Games')
    all_game_tuples= cursor.fetchall()
    all_games = []

    if all_game_tuples is not None:
        for game_tuple in all_game_tuples:
            game = Game(GameTuple=game_tuple)

            if game.finish_date is not None:
                finish_date = datetime.strptime(game.finish_date[:game.finish_date.rindex(" ")+9], '%Y-%m-%d %H:%M:%S')
                elapsed = datetime.now() - finish_date
                if elapsed.days < ClotConfig.min_days_between_rematch:
                    all_games.append(game)
            else:
                all_games.append(game)
    else:
        all_games = None

    return all_games

def find_last_n_games(conn, player_id, n):
    """ Find last n(=5) games for this player. The next template will exclude the templates used on these n games.
    """
    last_n_games = []
    cursor = conn.cursor()     
    if player_id is not None :
        cursor.execute("SELECT * FROM Games WHERE TeamA=:player OR TeamB=:player ORDER BY CreatedDate DESC LIMIT :n", {"player": player_id, "n":n})
        game_tuples= cursor.fetchall()
        if game_tuples is not None:
            for game_tuple in game_tuples:
                game = Game(GameTuple=game_tuple)
                last_n_games.append(game)

    return last_n_games

def find_all_unexpired_games(conn, player_id = None, current_date = None):
    """ Find all games in the past ClotConfig.days_before_game_expiry days. 
        Player ratings are effected by unexpired games only.

        If player_id is specified, find unexpired games for that player_id only.
    """
    if current_date is None:
        current_date = datetime.now()

    cursor = conn.cursor()
    if player_id is not None :
        cursor.execute("SELECT * FROM Games WHERE (TeamA=:player OR TeamB=:player) AND FinishDate NOT NULL AND FinishDate <= :current_date ", {"player": player_id, "current_date": current_date})
    else:
        cursor.execute("SELECT * FROM Games WHERE FinishDate NOT NULL AND FinishDate <= :current_date ORDER BY CreatedDate ASC", {"current_date": current_date})

    all_game_tuples= cursor.fetchall()
    return parse_unexpired_games(all_game_tuples, permissible_end_date = current_date)

def find_recent_unexpired_games(conn, topk=None):
    """ Find the last 15 games in the past ClotConfig.days_before_game_expiry days. 
    """
    if topk is None:
        topk = 15
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Games WHERE FinishDate NOT NULL ORDER BY FinishDate DESC LIMIT :topk", {"topk": topk})

    game_tuples= cursor.fetchall()
    return parse_unexpired_games(game_tuples)

def parse_unexpired_games(game_tuples, permissible_end_date = None):
    unexpired_games = []

    if game_tuples is not None:
        if permissible_end_date is None:
            permissible_end_date = datetime.now()
        permissible_start_date = permissible_end_date - timedelta(days=ClotConfig.days_before_game_expiry)
        for game_tuple in game_tuples:
            game = Game(GameTuple=game_tuple)

            if game.finish_date is not None:
                finish_date = datetime.strptime(game.finish_date[:game.finish_date.rindex(" ")+9], '%Y-%m-%d %H:%M:%S')
                if finish_date > permissible_start_date and finish_date < permissible_end_date:
                    unexpired_games.append(game)

    return unexpired_games

def find_games_since_last_update(conn, current_date = None):
    """ Find all games which have finished since the last update. 
        Player ratings are effected by these new games only. We re-use the previously computed Rating for 
        each player(which was computed using the games before these recent games).

        If a current_Date is specified only games until that date are returned. 
        This is useful for replaying scenarios where you want to run the rating calculation for every day over a time period.
    """    
    if current_date is None:
        current_date = datetime.now()

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Games WHERE IsRatingUpdated=0 AND FinishDate NOT NULL AND FinishDate <= :current_date ORDER BY CreatedDate ASC", {"current_date": current_date})

    all_game_tuples= cursor.fetchall()
    games_since_last_update = []
    if all_game_tuples is not None:
        for game_tuple in all_game_tuples:
            game = Game(GameTuple=game_tuple)
            if game.finish_date is not None:
                games_since_last_update.append(game)

    return games_since_last_update

def find_all_games(conn, player_id = None):
    """ Find all games.
        If player_id is specified, find games for that player_id only.
    """
    cursor = conn.cursor()    
    if player_id is not None :
        cursor.execute("SELECT * FROM Games WHERE TeamA=:player OR TeamB=:player", {"player": player_id})
    else:
        cursor.execute("SELECT * FROM Games")

    all_games = []
    all_game_tuples= cursor.fetchall()
    for game_tuple in all_game_tuples:
        game = Game(GameTuple=game_tuple)
        all_games.append(game)

    return all_games

def find_all_finished_games_by_clan(conn, clan_name):
    """ Find all games for a clan.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT Template, WinnerClan FROM ClanGameInfo WHERE (ClanA=:clan_name OR ClanB=:clan_name) AND FinishDate IS NOT NULL", {"clan_name": clan_name})
    all_game_tuples= cursor.fetchall()

    return all_game_tuples

def find_template_games(conn, template_id = None):
    """ Find template games.
        If template_id is specified, find games for that template_id only.
    """
    cursor = conn.cursor()    
    if template_id is not None :
        cursor.execute("SELECT * FROM Games WHERE Template=:template AND IsGameDeleted=0",{ "template": template_id})

    all_games = []
    all_game_tuples= cursor.fetchall()
    for game_tuple in all_game_tuples:
        game = Game(GameTuple=game_tuple)
        all_games.append(game)

    return all_games

def find_all_players(conn) -> List[Player]:
    """ Find all players.
    """
    cursor = conn.cursor() 

    cursor.execute('SELECT * FROM Players')
    all_player_tuples= cursor.fetchall()
    all_players = []

    if all_player_tuples is not None:
        for player_tuple in all_player_tuples:
            player = Player(player_tuple)
            all_players.append(player)

    return all_players


def find_players_on_vacation(conn) -> List[Player]:
    """ Find all players on vacation.
    """
    cursor = conn.cursor() 

    cursor.execute('SELECT * FROM Players WHERE OnVacation=?', (True,))
    all_player_tuples = cursor.fetchall()
    return [Player(player_tuple) for player_tuple in all_player_tuples] if all_player_tuples else []


def find_joined_players(conn):
    """ Find all players active on the ladder.
    """
    cursor = conn.cursor() 

    cursor.execute('SELECT * FROM Players WHERE IsJoined=?', (True,))
    all_player_tuples= cursor.fetchall()
    all_players = []

    if all_player_tuples is not None:
        for player_tuple in all_player_tuples:
            player = Player(player_tuple)
            all_players.append(player)

    return all_players

def get_report(conn, start_date = None, end_date = None):
    if end_date is None or type(end_date) is not datetime:
        end_date = datetime.now()
    if start_date == None or type(start_date) is not datetime:
        start_date = end_date - timedelta(days=7)

    end_date = end_date.strftime('%Y-%m-%d')
    start_date = start_date.strftime('%Y-%m-%d')

    cursor = conn.cursor() 
    query = """SELECT Players.Clan, Players.PlayerId, Players.Name, U.CurrentRank, U.PreviousRank,  U.RankDifference, U.CurrentRating, U.PreviousRating, U.RatingDifference, U.Wins, U.Losses
               FROM (
                 SELECT  HT.PlayerId, HT.CurrentRank, HT.PreviousRank, HT.RankDifference, HT.CurrentRating, HT.PreviousRating, HT.RatingDifference, WT.Wins, LT.Losses
                 FROM
                 (SELECT H1.PlayerId, H1.Rank AS CurrentRank, H2.Rank AS PreviousRank, H2.Rank - H1.Rank AS RankDifference,
                               H1.Rating AS CurrentRating, H2.Rating AS PreviousRating, H1.Rating - H2.Rating AS RatingDifference
                 FROM History H1 JOIN History H2 ON H2.PlayerId = H1.PlayerId 
                 WHERE H2.RecordedDate = ? AND H1.RecordedDate = ? AND H1.Rank <= 100) AS HT
                 LEFT JOIN
                 (SELECT Loser AS playerId, count(*) AS Losses
                  FROM ( SELECT Winner, CASE  WHEN Winner = TeamA THEN TeamB ELSE TeamA END AS Loser
                         FROM Games WHERE Winner NOT NULL AND FinishDate > ? AND FinishDate < ?)
                  GROUP BY Loser) AS LT
                 ON HT.playerId = LT.playerId
                 LEFT JOIN 
                 (SELECT Winner AS playerId, count(*) AS Wins
                  FROM ( SELECT Winner, CASE  WHEN Winner = TeamA THEN TeamB ELSE TeamA END AS Loser
                         FROM Games WHERE Winner NOT NULL AND FinishDate > ? AND FinishDate < ?)
                  GROUP BY Winner) AS WT
                 ON HT.playerId = WT.playerId) AS U
                LEFT JOIN Players
                ON Players.PlayerId = U.PlayerId
                ORDER BY U.CurrentRank
            """

    cursor.execute(query, (start_date, end_date, start_date, end_date, start_date, end_date))#, (end_date,start_date, start_date, end_date, start_date, end_date))
    all_player_tuples= cursor.fetchall()
    return all_player_tuples

def setup_db():
    conn = sqlite3.connect(ClotConfig.database_location) # or use :memory: to put it in RAM
    create_game_table(conn)
    create_player_table(conn)
    create_notable_games_table(conn)
    create_veto_table(conn)
    create_history_table(conn)
    create_clans_table(conn)
    create_leaderboard_table(conn)
    pass

#setup_db()