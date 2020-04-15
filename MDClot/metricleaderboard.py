game_count = 'Game Count'
percentage = '%'
wins = 'Wins'
days = 'Days'

most_games_played = "Most Games Played"
best_win_rate = "Best Win Rate"
most_wins = "Most Wins"
first_rank_streak = "First Rank on MDL (Streak)"
top5_streak = "Top 5 Rank on MDL (Streak)"
top10_streak = "Top 10 Rank on MDL (Streak)"
longest_ranked_streak = "Longest Ranked (Streak)"
first_rank_total = "First Rank on MDL (Total)"
top5_total = "Top 5 Rank on MDL (Total)"
top10_total = "Top 10 Rank on MDL (Total)"
longest_ranked_total = "Longest Ranked (Total)"
longest_win_streak = "Longest Win Streak"

class MetricLeaderboardMetadata:
    def __init__(self, metric_name: str, metric_unit: str, build_leaderboard: callable, build_arg: int = None):
        self.metric_name = metric_name
        self.metric_unit = metric_unit
        self.build_leaderboard = build_leaderboard
        self.build_arg = build_arg
