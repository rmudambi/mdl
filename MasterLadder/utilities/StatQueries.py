from datetime import datetime, timedelta
import sqlite3
from typing import List, Tuple

from utilities.DAL import delete_leaderboard, insert_leaderboard, insert_stat_history_record
from utilities.clan_league_logging import get_logger
from config.ClotConfig import ClotConfig
from utilities.metricleaderboard import (MetricLeaderboardMetadata,
                                         DAYS,
                                         GAME_COUNT,
                                         LEADERBOARD_METRICS as METRICS,
                                         PERCENTAGE,
                                         RATING,
                                         WINS, )

logger = get_logger()

mdl_stat_finished_games = "Finished Games"
mdl_stat_finished_games_per_day = "Finished Games Per Day"


def update_mdl_stats(conn):
    fin_date = datetime.now()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT datetime((strftime('%s', f1.FinishDate) / 24/3600 + 1) * 3600 *24, 'unixepoch')
            as cTime1, count(*) AS gc
        FROM Games f1 
        WHERE cTime1 < ?""", (fin_date,))

    tg_tuples = cursor.fetchall()
    tuple_update_time = datetime.strptime(tg_tuples[0][0], '%Y-%m-%d %H:%M:%S')
    insert_stat_history_record(conn, (tuple_update_time, mdl_stat_finished_games, tg_tuples[0][1]))

    prev_date = fin_date + timedelta(days=-1)
    cursor.execute("""SELECT datetime((strftime('%s', f1.FinishDate) / 24/3600 + 1) * 3600 *24, 'unixepoch') as cTime1, count(*) AS gc
                    FROM Games f1 
                    WHERE cTime1 < ? AND cTime1 > ? """, (fin_date, prev_date))

    tg_tuples = cursor.fetchall()
    tuple_update_time = datetime.strptime(tg_tuples[0][0], '%Y-%m-%d %H:%M:%S')
    insert_stat_history_record(conn, (tuple_update_time, mdl_stat_finished_games_per_day, tg_tuples[0][1]))


def find_all_games(conn):
    """ Find all games.
    """
    cursor = conn.cursor()
    cursor.execute(get_all_games_query())

    player_tuples = cursor.fetchall()
    return player_tuples


def get_all_games_query():
    return """SELECT * FROM (SELECT TeamA, sum(gc) AS gc  FROM (SELECT TeamA, count(*) as gc FROM Games 
                           WHERE FinishDate IS NOT NULL 
                           GROUP BY TeamA 
                           UNION ALL
                           SELECT TeamB, count(*) as gc FROM Games 
                           WHERE FinishDate IS NOT NULL
                           GROUP BY TeamB) GROUP BY TeamA
                           ORDER BY gc DESC) WHERE gc >= 20"""


def get_games_won_query():
    return """ SELECT TeamA, sum(gc) AS gc  FROM (SELECT TeamA, count(*) AS gc FROM Games 
                           WHERE Winner = TeamA AND FinishDate IS NOT NULL 
                           GROUP BY TeamA 
                           UNION ALL
                           SELECT TeamB, count(*) AS gc FROM Games 
                           WHERE Winner = TeamB AND FinishDate IS NOT NULL
                           GROUP BY TeamB) GROUP BY TeamA
                           ORDER BY gc DESC """


def find_games_won(conn):
    """ Find win count.
    """
    cursor = conn.cursor()
    cursor.execute(get_games_won_query())
    player_won_games_tuples = cursor.fetchall()
    cursor.execute(get_all_games_query())
    player_all_games_tuples = cursor.fetchall()
    player_tuples = []
    all_games = {}
    for player_all_games_tuple in player_all_games_tuples:
        all_games[player_all_games_tuple[0]] = player_all_games_tuple[1]
    
    for p in player_won_games_tuples:
        # If the player does not exist in all_games(coz < 20 games played), skip this player.
        if p[0] not in all_games:
            continue
        
        player_tuples.append(p)

    return player_tuples


def find_best_rating(conn) -> List[Tuple[int, int]]:
    """Find best rating"""
    cursor = conn.cursor()
    cursor.execute('SELECT PlayerId, BestDisplayedRating FROM Players WHERE BestDisplayedRating IS NOT NULL ORDER BY BestRating DESC')
    player_tuples = cursor.fetchall()
    player_tuples = sorted(player_tuples, key=lambda x: x[1], reverse=True)
    return player_tuples


def find_win_rate(conn) -> List[Tuple[int, float]]:
    """ Find win rate.
    """
    cursor = conn.cursor()
    cursor.execute(get_games_won_query())
    player_won_games_tuples = cursor.fetchall()
    cursor.execute(get_all_games_query())
    player_all_games_tuples = cursor.fetchall()
    player_tuples = []
    won_games = {}
    all_games = {}
    for player_won_games_tuple in player_won_games_tuples:
        won_games[player_won_games_tuple[0]] = player_won_games_tuple[1]

    for player_all_games_tuple in player_all_games_tuples:
        all_games[player_all_games_tuple[0]] = player_all_games_tuple[1]
    
    for p in player_won_games_tuples:
        try:
            # If the player does not exist in all_games(coz < 20 games played), skip this player.
            player_tuples.append((p[0], 100 * won_games[p[0]] / all_games[p[0]]))
        except KeyError:
            pass

    player_tuples = sorted(player_tuples, key=lambda x: x[1], reverse=True)
    return player_tuples


def get_player_ranked_days(conn, rank: int = None) -> List[Tuple[int, str]]:
    """ Find all history records. If a rank is specified, find 
    """
    cursor = conn.cursor()
    if rank is None:
        cursor.execute("""SELECT PlayerId, group_concat(RecordedDate) 
                        FROM History
                        WHERE Rating IS NOT NULL
                        GROUP BY PlayerId""")
    else:
        rank = int(rank)
        cursor.execute("""SELECT PlayerId, group_concat(RecordedDate) 
                        FROM History
                        WHERE Rating IS NOT NULL AND Rank <= :rank
                        GROUP BY PlayerId""", {"rank": rank})
    return cursor.fetchall()


def find_longest_consecutive_days_ranked(conn, rank: int = None) -> List[Tuple[int, int]]:
    player_tuples = get_player_ranked_days(conn, rank)
    result_tuples = []
    for player_tuple in player_tuples:
        player_id = player_tuple[0]
        recorded_dates = player_tuple[1].split(",")

        max_consecutive_days_ranked = 0
        day_counter = 0
        previous_recorded_date = None

        for recorded_date in recorded_dates:
            r_date = datetime.strptime(recorded_date, '%Y-%m-%d')
            if previous_recorded_date is None:
                day_counter += 1
                previous_recorded_date = r_date
            else:
                elapsed = r_date - previous_recorded_date
                if elapsed.days == 1:
                    day_counter += 1
                    previous_recorded_date = r_date
                else:
                    # Change max if bigger and reset counter 
                    max_consecutive_days_ranked = max(max_consecutive_days_ranked, day_counter)
                    day_counter = 0
                    previous_recorded_date = None

        # Check if player was ranked every day!
        max_consecutive_days_ranked = max(max_consecutive_days_ranked, day_counter)

        result_tuple = (player_id, max_consecutive_days_ranked)
        result_tuples.append(result_tuple)

    new_result_tuples = sorted(result_tuples, key=lambda x: x[1], reverse=True)
    return new_result_tuples


def find_total_days_ranked(conn, rank: int = None) -> List[Tuple[int, int]]:
    player_tuples = get_player_ranked_days(conn, rank)

    player_ranks = [(player_tuple[0], len(player_tuple[1].split(","))) for player_tuple in player_tuples]
    player_ranks.sort(key=lambda x: x[1], reverse=True)
    return player_ranks


def find_active_days_ranked(conn, rank: int = None) -> List[Tuple[int, int]]:
    player_tuples = get_player_ranked_days(conn, rank)
    result_tuples = []
    current_date = datetime.now()
    for player_tuple in player_tuples:
        player_id = player_tuple[0]
        recorded_dates = player_tuple[1].split(",")

        day_counter = 0
        previous_recorded_date = None

        for recorded_date in recorded_dates[::-1]:
            r_date = datetime.strptime(recorded_date, '%Y-%m-%d')
            if previous_recorded_date is None:
                if current_date - r_date < timedelta(hours=25):
                    day_counter += 1
                    previous_recorded_date = r_date
                else:
                    break
            else:
                elapsed = previous_recorded_date - r_date
                if elapsed.days == 1:
                    day_counter += 1
                    previous_recorded_date = r_date
                else:
                    break

        result_tuple = (player_id, day_counter)
        result_tuples.append(result_tuple)

    new_result_tuples = sorted(result_tuples, key=lambda x: x[1], reverse=True)
    return new_result_tuples


def find_longest_win_streak(conn):
    cursor = conn.cursor()    
    games_won_query = """
        SELECT TeamA, group_concat(ids)  FROM (
            SELECT TeamA, group_concat(GameId || "_" || FinishDate) as ids
            FROM Games 
            WHERE Winner = TeamA AND FinishDate IS NOT NULL 
            GROUP BY TeamA 
            UNION ALL
            SELECT TeamB, group_concat(GameId || "_" || FinishDate) as ids
            FROM Games 
            WHERE Winner = TeamB AND FinishDate IS NOT NULL
            GROUP BY TeamB)
        GROUP BY TeamA
    """

    all_games_query = """
        SELECT TeamA, group_concat(ids)  FROM (
            SELECT TeamA, group_concat(GameId || "_" || FinishDate) as ids FROM Games 
            WHERE FinishDate IS NOT NULL 
            GROUP BY TeamA 
            UNION ALL
            SELECT TeamB, group_concat(GameId || "_" || FinishDate) as ids FROM Games 
            WHERE FinishDate IS NOT NULL
            GROUP BY TeamB)
        GROUP BY TeamA
    """
    
    cursor.execute(games_won_query)
    player_won_games_tuples = cursor.fetchall()
    cursor.execute(all_games_query)
    player_all_games_tuples = cursor.fetchall()

    won_games = {}
    all_games = {}

    for p_id, won_game_ids in player_won_games_tuples:
        games = [element.split("_") for element in won_game_ids.split(",")]
        sorted_games = sorted(games, key=lambda x: x[1], reverse=True)
        won_games[p_id] = [x[0] for x in sorted_games]

    for p_id, all_game_ids in player_all_games_tuples:
        games = [element.split("_") for element in all_game_ids.split(",")]
        sorted_games = sorted(games, key=lambda x: x[1], reverse=True)
        all_games[p_id] = [x[0] for x in sorted_games]

    player_tuples = []
    for won_player_id in won_games:
        # Player was not captured in all_games as they didn't have 20 games.
        if won_player_id not in all_games:
            continue

        prev_won_game_index = None
        max_win_streak = 0
        current_win_streak = 0
        for won_game_id in won_games[won_player_id]:
            won_game_index = all_games[won_player_id].index(won_game_id)

            if prev_won_game_index is None or prev_won_game_index == won_game_index - 1:
                current_win_streak += 1
            else:
                max_win_streak = max(max_win_streak, current_win_streak)
                current_win_streak = 1

            prev_won_game_index = won_game_index

        max_win_streak = max(max_win_streak, current_win_streak)
    
        # Add player if they have a win streak of 3 games or greater.
        if max_win_streak >= 3:
            player_tuples.append((won_player_id, max_win_streak))

    return sorted(player_tuples, key=lambda x: x[1], reverse=True)


leaderboard_metadata: List[MetricLeaderboardMetadata] = [
    MetricLeaderboardMetadata(METRICS.MOST_GAMES_PLAYED, GAME_COUNT, find_all_games),
    MetricLeaderboardMetadata(METRICS.MOST_WINS, WINS, find_games_won),
    MetricLeaderboardMetadata(METRICS.BEST_WIN_RATE, PERCENTAGE, find_win_rate),
    MetricLeaderboardMetadata(METRICS.LONGEST_WIN_STREAK, WINS, find_longest_win_streak),
    MetricLeaderboardMetadata(METRICS.FIRST_RANK_STREAK, DAYS, find_longest_consecutive_days_ranked, 1),
    MetricLeaderboardMetadata(METRICS.TOP5_STREAK, DAYS, find_longest_consecutive_days_ranked, 5),
    MetricLeaderboardMetadata(METRICS.TOP10_STREAK, DAYS, find_longest_consecutive_days_ranked, 10),
    MetricLeaderboardMetadata(METRICS.LONGEST_RANKED_STREAK, DAYS, find_longest_consecutive_days_ranked),
    MetricLeaderboardMetadata(METRICS.FIRST_RANK_TOTAL, DAYS, find_total_days_ranked, 1),
    MetricLeaderboardMetadata(METRICS.TOP5_TOTAL, DAYS, find_total_days_ranked, 5),
    MetricLeaderboardMetadata(METRICS.TOP10_TOTAL, DAYS, find_total_days_ranked, 10),
    MetricLeaderboardMetadata(METRICS.LONGEST_RANKED_TOTAL, DAYS, find_total_days_ranked),
    MetricLeaderboardMetadata(METRICS.FIRST_RANK_ACTIVE, DAYS, find_active_days_ranked, 1),
    MetricLeaderboardMetadata(METRICS.TOP5_ACTIVE, DAYS, find_active_days_ranked, 5),
    MetricLeaderboardMetadata(METRICS.TOP10_ACTIVE, DAYS, find_active_days_ranked, 10),
    MetricLeaderboardMetadata(METRICS.LONGEST_RANKED_ACTIVE, DAYS, find_active_days_ranked),
    MetricLeaderboardMetadata(METRICS.BEST_RATING, RATING, find_best_rating),
]


def update_leaderboards() -> None:
    conn = sqlite3.connect(ClotConfig.database_location)
    leaderboard_creation_time = datetime.now()

    # Update all leaderboards
    for leaderboard in leaderboard_metadata:
        logger.info("Updating " + leaderboard.metric_name + " leaderboard")
        metric_leaderboard = (leaderboard.build_leaderboard(conn) if not leaderboard.build_arg
                              else leaderboard.build_leaderboard(conn, leaderboard.build_arg))
        for result in metric_leaderboard:
            record = (leaderboard_creation_time, leaderboard.metric_name, result[0], result[1])
            insert_leaderboard(conn, record)

    # Delete all old leaderboards
    logger.info("Delete all old leaderboards")
    delete_leaderboard(conn, leaderboard_creation_time)


def find_metric_leaderboard(metric_name):
    conn = sqlite3.connect(ClotConfig.database_location)
    cursor = conn.cursor()
    cursor.execute("""SELECT group_concat(PlayerId), group_concat(Value), datetime((strftime('%s', CreatedDate) / 7200) * 7200, 'unixepoch') AS createdTime
                         FROM Leaderboard 
                         WHERE Metric=?
                         GROUP BY createdTime
                         ORDER BY createdTime DESC
                         LIMIT 1""", (metric_name,))

    tuples = cursor.fetchall()
    if len(tuples) != 1:
        return None
    
    players = tuples[0][0].split(",")
    metric_values = tuples[0][1].split(",")

    if len(players) != len(metric_values):
        filler = [None] * (len(players) - len(metric_values))
        filler.extend(metric_values)
        metric_values = filler

    result = []
    for i, player in enumerate(players):
        result.append((int(player), metric_values[i]))

    return result


def find_player_leaderboard_by_clan(clan, metric_name):
    conn = sqlite3.connect(ClotConfig.database_location)
    cursor = conn.cursor()
    cursor.execute("""SELECT P.PlayerId, L.Value
                        FROM Leaderboard L 
                        JOIN Players P
                        ON L.PlayerId = P.PlayerId
                        WHERE P.Clan = ? AND L.Metric = ?""", (clan.name, metric_name))

    player_tuples = cursor.fetchall()
    return player_tuples


def find_vetoes_per_template():
    conn = sqlite3.connect(ClotConfig.database_location)
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM (
                        SELECT TemplateId, count(*) AS c
                        FROM Veto LEFT JOIN Players 
                        ON Veto.PlayerId = Players.PlayerId
                        WHERE Players.IsJoined = 1 AND TemplateId!=-1 
                        GROUP BY TemplateId
                        ORDER BY c DESC)
                    WHERE c >=3""")

    template_tuples = cursor.fetchall()
    return template_tuples


def find_mdl_stats_by_metric(metric_name):
    conn = sqlite3.connect(ClotConfig.database_location)
    cursor = conn.cursor()
    cursor.execute("""SELECT RecordedDate,Value 
                        FROM StatHistory
                        WHERE MetricName = ?
                        ORDER BY RecordedDate DESC""", (metric_name,))

    stat_tuples = cursor.fetchall()
    return stat_tuples


def find_number_of_active_players():
    conn = sqlite3.connect(ClotConfig.database_location)
    cursor = conn.cursor()
    cursor.execute("""SELECT count(*)
                        FROM Players
                        WHERE IsJoined = 1""")

    result = cursor.fetchone()
    return result[0]


def find_total_number_of_players():
    conn = sqlite3.connect(ClotConfig.database_location)
    cursor = conn.cursor()
    cursor.execute("""SELECT count(*)
                        FROM Players""")

    result = cursor.fetchone()
    return result[0]


def find_number_of_ongoing_games():
    conn = sqlite3.connect(ClotConfig.database_location)
    cursor = conn.cursor()
    cursor.execute("""SELECT count(*)
                        FROM Games
                        WHERE FinishDate IS NULL""")

    result = cursor.fetchone()
    return result[0]
