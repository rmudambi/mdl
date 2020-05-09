class Clan:
    def __init__(self, **props):
        self.id = props.get("Id")
        self.name = props.get("Name")
        self.logo_link = props.get("LogoLink")

    def __init__(self, clan_tuple):
        if clan_tuple is None or len(clan_tuple) != 3:
            raise Exception("Invalid clan tuple")

        self.id = clan_tuple[0]
        self.name = clan_tuple[1]
        self.logo_link = clan_tuple[2]