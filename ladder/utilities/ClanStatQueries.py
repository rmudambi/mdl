from config.ClotConfig import ClotConfig
from datetime import datetime, timedelta
import sqlite3
from utilities.DAL import *
from utilities.clan_league_logging import get_logger


logger = get_logger()

active_players = "Active Players"
total_players = "Total Players"
total_games = "Total Games Played"
win_rate = "Win Rate"
wins = "Wins"
all_time_highest_rating = "All-time highest rating"
all_time_highest_rank = "All-time highest rank"
current_average_rating = "Current average rating"
current_highest_rating = "Current highest rating"
players_with_first_rank = "First Rank on MTL"
players_with_top5 = "Top 5 Rank on MTL"
players_with_top10 = "Top 10 Rank on MTL"

def find_total_active_players(conn):
    """ Find count of players(Isjoined = true) for every clan.
    """
    cursor = conn.cursor()
    cursor.execute("""SELECT Clan, COUNT(*) AS PlayerCount, MAX(DisplayedRating) AS CurrentHighestRating,
                            CAST(AVG(DisplayedRating) AS INT) AS CurrentAverageRating
                        FROM Players 
                        WHERE IsJoined = 1 AND Clan !=""
                        GROUP BY Clan""")

    clan_tuples= cursor.fetchall()
    return clan_tuples

def find_total_players(conn):
    """ Find count of players for every clan.
    """
    cursor = conn.cursor()
    cursor.execute("""SELECT Clan, COUNT(*) AS PlayerCount, MAX(BestDisplayedRating) AS AllTimeHighestRating, MIN(BestRank) AS AllTimeHighestRank
                        FROM Players 
                        WHERE Clan !=""
                        GROUP BY Clan""")

    clan_tuples= cursor.fetchall()
    return clan_tuples

def create_clan_game_info(conn):
    """ 
    """
    cursor = conn.cursor()
    
    cursor.execute("""CREATE TABLE TempClanGameInfo AS 
                        SELECT A.gid AS Id, A.FinishDate AS FinishDate, A.Template AS Template, A.TeamA AS TeamA, A.TeamB AS TeamB, A.winner AS Winner, 
                                PlayerAName, PlayerBName, ClanA, ClanB,  CASE WHEN A.winner = A.TeamA THEN ClanA ELSE ClanB end  AS WinnerClan
                        FROM (
                            SELECT Games.GameId AS gid, Games.FinishDate AS FinishDate, Games.Template AS Template, Games.Winner AS winner, Games.TeamA AS TeamA, 
                                    Games.TeamB AS TeamB, Players.Clan AS ClanA, Players.Name AS PlayerAName 
                            FROM Games 
                            JOIN Players
                            ON Games.TeamA = Players.PlayerId) A
                        JOIN
                            (SELECT Games.GameId AS gid, Games.FinishDate AS FinishDate, Games.Template AS Template, Games.Winner AS winner, Games.TeamA AS TeamA, 
                                    Games.TeamB AS TeamB, Players.Clan AS ClanB, Players.Name AS PlayerBName FROM Games 
                            JOIN Players
                            ON Games.TeamB = Players.PlayerId) B
                        ON A.gid = B.gid""")
    cursor.execute("""DROP TABLE IF EXISTS ClanGameInfo""")
    cursor.execute("""ALTER TABLE TempClanGameInfo RENAME TO ClanGameInfo""")

def find_games_played_per_clan(conn):
    cursor = conn.cursor()
    cursor.execute("""SELECT Clan, sum(totalGames)
                        FROM(
                        SELECT ClanA AS Clan, count(*) AS totalGames
                        FROM ClanGameInfo
                        WHERE ClanA IS NOT NULL
                        GROUP BY ClanA
                        UNION ALL
                        SELECT ClanB AS Clan, count(*) AS totalGames
                        FROM ClanGameInfo
                        WHERE ClanB IS NOT NULL
                        GROUP BY ClanB)
                        GROUP BY Clan""")

    clan_tuples= cursor.fetchall()
    return clan_tuples

def find_games_won_per_clan(conn):
    cursor = conn.cursor()
    cursor.execute("""SELECT WinnerClan, count(*)
                        FROM ClanGameInfo
                        WHERE WinnerClan IS NOT NULL
                        GROUP BY WinnerClan""")

    clan_tuples= cursor.fetchall()
    return clan_tuples

def find_top_k_per_clan(conn, k):
    cursor = conn.cursor()
    cursor.execute("""SELECT Clan, COUNT(*) AS PlayerCount
                        FROM Players 
                        WHERE BestRank <= ? AND Clan !=""
                        GROUP BY Clan""", (k,))

    clan_tuples= cursor.fetchall()
    return clan_tuples

def compute_clan_stats():
    conn = sqlite3.connect(ClotConfig.database_location)
    record_insert_time = datetime.now()

    # create intermediate clan game info table
    logger.info("create intermediate clan game info table")
    create_clan_game_info(conn)

    # Insert active_players, current_highest_rating, current_average_rating
    logger.info("Insert active_players, current_highest_rating, current_average_rating")
    clan_tuples = find_total_active_players(conn)
    for clan_tuple in clan_tuples:
        clan_name = clan_tuple[0]
        if clan_tuple[1] is not None:
            insert_clan_leaderboard(conn, (record_insert_time, clan_name, active_players, clan_tuple[1]))
        if clan_tuple[2] is not None:
            insert_clan_leaderboard(conn, (record_insert_time, clan_name, current_highest_rating, clan_tuple[2]))
        if clan_tuple[3] is not None:
            insert_clan_leaderboard(conn, (record_insert_time, clan_name, current_average_rating, clan_tuple[3]))

    # Insert total_players, all_time_highest_rating, all_time_highest_rank
    logger.info("Insert total_players, all_time_highest_rating, all_time_highest_rank")
    clan_tuples = find_total_players(conn)
    for clan_tuple in clan_tuples:
        clan_name = clan_tuple[0]
        if clan_tuple[1] is not None:
            insert_clan_leaderboard(conn, (record_insert_time, clan_name, total_players, clan_tuple[1]))
        if clan_tuple[2] is not None:
            insert_clan_leaderboard(conn, (record_insert_time, clan_name, all_time_highest_rating, clan_tuple[2]))
        if clan_tuple[3] is not None:
            insert_clan_leaderboard(conn, (record_insert_time, clan_name, all_time_highest_rank, clan_tuple[3]))

    # Insert players_with_first_rank
    logger.info("Insert players_with_first_rank")
    clan_tuples = find_top_k_per_clan(conn, 1)
    for clan_tuple in clan_tuples:
        clan_name = clan_tuple[0]
        insert_clan_leaderboard(conn, (record_insert_time, clan_name, players_with_first_rank, clan_tuple[1]))

    # Insert players_with_top5
    logger.info("Insert players_with_top5")
    clan_tuples = find_top_k_per_clan(conn, 5)
    for clan_tuple in clan_tuples:
        clan_name = clan_tuple[0]
        insert_clan_leaderboard(conn, (record_insert_time, clan_name, players_with_top5, clan_tuple[1]))

    # Insert players_with_top10
    logger.info("Insert players_with_top10")
    clan_tuples = find_top_k_per_clan(conn, 10)
    for clan_tuple in clan_tuples:
        clan_name = clan_tuple[0]
        insert_clan_leaderboard(conn, (record_insert_time, clan_name, players_with_top10, clan_tuple[1]))

    won_games_per_clan = {}
    # Insert games won per clan
    logger.info("# Insert games won per clan")
    clan_tuples = find_games_won_per_clan(conn)
    for clan_tuple in clan_tuples:
        clan_name = clan_tuple[0]
        won_games_per_clan[clan_name] = clan_tuple[1]
        if clan_tuple[1] is not None:
            insert_clan_leaderboard(conn, (record_insert_time, clan_name, wins, clan_tuple[1]))

    # Insert Total games per clan
    logger.info("Insert Total games per clan")
    clan_tuples = find_games_played_per_clan(conn)
    for clan_tuple in clan_tuples:
        clan_name = clan_tuple[0]
        if clan_tuple[1] is not None:
            insert_clan_leaderboard(conn, (record_insert_time, clan_name, total_games, clan_tuple[1]))
            won_games = 0
            if clan_name in won_games_per_clan:
                won_games = won_games_per_clan[clan_name]
            insert_clan_leaderboard(conn, (record_insert_time, clan_name, win_rate, won_games / clan_tuple[1] * 100))

    delete_clan_leaderboard(conn, record_insert_time)

def find_clan_metrics(clan):
    conn = sqlite3.connect(ClotConfig.database_location)
    cursor = conn.cursor()
    cursor.execute("""SELECT ClanName, group_concat(Metric), group_concat(Value), datetime((strftime('%s', CreatedDate) / 7200) * 7200, 'unixepoch') AS createdTime
                        FROM ClanLeaderboard WHERE ClanName = ?
                        GROUP BY CreatedDate
                        ORDER BY CreatedDate DESC
                        LIMIT 1""", (clan.name,))

    tuples= cursor.fetchall()
    if len(tuples) !=  1:
        return None
    
    metric_names = tuples[0][1].split(",")
    metric_values = tuples[0][2].split(",")

    result = []
    for i, metric_name in enumerate(metric_names):
        result.append((metric_name, metric_values[i]))

    return result

def find_clan_leaderboard(metric_name, sort_desc = True):
    conn = sqlite3.connect(ClotConfig.database_location)
    cursor = conn.cursor()
    cursor.execute("""SELECT group_concat(ClanName, "__!!__"), group_concat(Value), datetime((strftime('%s', CreatedDate) / 7200) * 7200, 'unixepoch') AS createdTime
                         FROM ClanLeaderboard 
                         WHERE Metric=?
                         GROUP BY createdTime
                         ORDER BY createdTime DESC
                         LIMIT 1""", (metric_name,))

    tuples= cursor.fetchall()
    if len(tuples) !=  1:
        return None
    
    clans = tuples[0][0].split("__!!__")
    metric_values = tuples[0][1].split(",")

    if len(clans) != len(metric_values):
        filler = [None] * (len(clans) - len(metric_values))
        filler.extend(metric_values)
        metric_values = filler

    result = []
    for i, clan in enumerate(clans):
        result.append((clan, metric_values[i]))

    result = sorted(result, key=lambda x: float(x[1]), reverse=sort_desc)
    return result