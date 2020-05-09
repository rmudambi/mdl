class Game:
    def __init__(self, **props):
        if "GameTuple" in props:
            game_tuple = props.get("GameTuple")
            if game_tuple is None or len(game_tuple) < 9:
                raise Exception("Invalid game tuple")

            self.created_date = game_tuple[0]
            self.finish_date = game_tuple[1]
            self.game_id = game_tuple[2]
            self.game_link = game_tuple[3]
            self.team_a = game_tuple[4]
            self.team_b = game_tuple[5]
            self.winner = game_tuple[6]
            self.is_rating_updated = game_tuple[7]
            self.is_game_deleted = game_tuple[8]
            self.template = game_tuple[9]
        else:
            self.created_date = props.get("CreatedDate")
            self.finish_date = None
            self.game_id = props.get("GameId")
            self.game_link = 'https://www.warlight.net/MultiPlayer?GameID={0}'.format(self.game_id)
            self.team_a = props.get("TeamA")
            self.team_b = props.get("TeamB")
            self.winner = None
            self.is_rating_updated = False
            self.is_game_deleted = False
            self.template = props.get("Template")

    def serialize(self, players):
        serialized_game = {}
        serialized_game['game_id'] = self.game_id
        serialized_game['created_date'] = self.created_date
        serialized_game['finish_date'] = self.finish_date
        serialized_game['template'] = self.template
        serialized_game['players'] = players
        if self.winner is not None:
            serialized_game['winner_id'] = self.winner
        if self.is_game_deleted:
            serialized_game['is_game_deleted'] = True

        return serialized_game