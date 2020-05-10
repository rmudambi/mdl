from mtl.ladder.config import clot_config


class Player:
    def __init__(self, player_tuple):
        if player_tuple is None or len(player_tuple) != 16:
            raise Exception("Invalid player tuple")

        self.created_date = player_tuple[0]
        self.player_name = player_tuple[1]
        self.player_id = player_tuple[2]
        self.Rating = player_tuple[3]
        self.is_ranked = player_tuple[4]
        self.is_joined = player_tuple[5]
        self.max_games = player_tuple[6]
        self.best_rating = player_tuple[7]      # Field is deprecated
        self.best_rank = player_tuple[8]
        self.clan = player_tuple[9]
        self.activity_bonus = player_tuple[10]
        self.displayed_rating = player_tuple[11]
        self.best_displayed_rating = player_tuple[12]
        self.wait_cycles = player_tuple[13]
        self.rank = player_tuple[14]
        self.on_vacation = player_tuple[15]

    def update_displayed_rating(self):
        """ displayed_rating is the sum of the actual rating + activity_bonus"""
        self.displayed_rating = round(self.Rating + self.get_capped_activity_bonus())

    def increment_activity_bonus(self):
        """ Increment activity bonus by 4 for every game played.(capped at a max of 80)"""
        self.activity_bonus = min(self.activity_bonus + clot_config.ACTIVITY_BONUS_PER_GAME,
                                  clot_config.ACTIVITY_BONUS_MAX_CAP)

    def decay_activity_bonus(self, num_of_days=None):
        """ Decay all players' activity bonus by 2% every day. 
            If num_of_Days is provided, decay exponentially for those many days. """
        if num_of_days is None:
            num_of_days = 1
        self.activity_bonus = self.activity_bonus * (1 - clot_config.ACTIVITY_DECAY_BONUS_PERCENT / 100) ** num_of_days

    def converge_actual_rating(self, num_of_days=None):
        """ Converge players' rating towards 1500. 
                If their current rating > 1500, it decreases by 1 every day if they have no unexpired games
                If their current rating < 1500, it increases by 1 every day if they have no unexpired games
            If num_of_Days is provided, converge for those many days."""
        if num_of_days is None:
            num_of_days = 1

        # If rating is in the interval [1499,1501] then don't converge. This is because we don't want to oscillate
        # about the initial rating.
        if self.Rating > clot_config.INITIAL_RATING + 1:
            self.Rating -= clot_config.INACTIVE_PLAYER_RATING_CONVERGENCE * num_of_days
        elif self.Rating < clot_config.INITIAL_RATING - 1:
            self.Rating += clot_config.INACTIVE_PLAYER_RATING_CONVERGENCE * num_of_days

    def get_capped_activity_bonus(self):
        """ caps the activity bonus at the lower value(80).
        """
        return min(self.activity_bonus, clot_config.ACTIVITY_BONUS_LOWER_CAP)

    def serialize(self, clan=None, is_minified=False):
        serialized_player = {'player_id': self.player_id, 'player_name': self.player_name}
        if clan is not None:
            serialized_player['clan_id'] = clan.id
            serialized_player['clan_icon'] = clan.logo_link
            serialized_player['clan'] = clan.name

        if not is_minified:
            serialized_player['displayed_rating'] = self.displayed_rating
            if self.best_displayed_rating is not None:
                serialized_player['best_displayed_rating'] = self.best_displayed_rating
            if self.rank is not None:
                serialized_player['rank'] = self.rank
            if self.best_rank is not None:
                serialized_player['best_rank'] = self.best_rank

        return serialized_player

    def update_status_on_leave(self, on_vacation: bool = False) -> None:
        """ Update the status of this player if they have left the ladder or are on vacation."""
        self.is_joined = False
        self.unrank_player()
        self.on_vacation = on_vacation

    def unrank_player(self) -> None:
        """ Update the status of this player if they have left the ladder, are on vacation or don't have 20 unexpired
         games in the last 5 months """
        self.is_ranked = False
        self.rank = None

    def return_from_vacation(self) -> None:
        self.on_vacation = False
        self.is_joined = True
