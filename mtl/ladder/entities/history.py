class History:
    def __init__(self, **props):
        if "HistoryTuple" in props:
            history_tuple = props.get("HistoryTuple")
            if history_tuple is None or len(history_tuple) < 4:
                raise Exception("Invalid history tuple")
            
            self.recorded_date = history_tuple[0]
            self.player_id = history_tuple[1]
            self.rank = history_tuple[2]
            self.rating = history_tuple[3]
        else:
            self.recorded_date = props.get("RecordedDate")
            self.player_id = props.get("PlayerId")
            self.rank = props.get("Rank")
            self.rating = props.get("Rating")
