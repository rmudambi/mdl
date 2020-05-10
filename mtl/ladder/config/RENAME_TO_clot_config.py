player_table_name = "Player"
game_table_name = "Game"
tournament_name = "MTL"
email = 'fill this with your warzone email'
token = 'fill this with your warzone token'
profile_id = "fill this with your warzone player id"
max_days_to_join_game = 3
min_days_between_rematch = 5
days_before_game_expiry = 150
initial_rating = 1500
database_location = "/path/to/your/local/db"
template_veto_count = 7
notable_game_count = 5
recent_games = 5   # Neglect all templates used in these 5 games when allotting a new template for a player.
activity_bonus_per_game = 4
activity_bonus_max_cap = 100.0
activity_bonus_lower_cap = 80.0
activity_decay_bonus_percent = 2
inactive_player_rating_convergence = 1
retired_template_names = {
    980608: "Red Dead Redemption",
    1006752: "Gravic Swamp",
    989159: "Sri Lanka",
    940639: "Qina",
    988665: "Eberron World",
    940658: "Gelvien Islands",
    1006746: "Rad Osil",
    988648: "Cosmo Land",
    988652: "Oxfordshire",
}

template_names = {
    1006750: "Tor-ture",
    1006748: "Australia",
    989165: "Saudi Arabia",
    989162: "Greece LD",
    989118: "Atlantis",
    969173: "Malvia",
    944620: "Elitist Africa",
    945791: "Georgia Army Cap",
    942413: "Strat MME",
    940676: "Austria Airports",
    940675: "Baltic Sea",
    940674: "Basileia",
    940673: "Battle for Middle Earth",
    940670: "Battle Islands V",
    940669: "Black Sea",
    940667: "British Raj",
    940666: "Cat Fight",
    940665: "China",
    940664: "Discovery",
    940663: "EA&O",
    940662: "EarthSea",
    940660: "Final Fantasy 7",
    940659: "French Brawl",
    940656: "Greater Middle East III",
    940654: "Guiroma",
    980615: "Hannibal at the Gates",
    940652: "Laketown",
    1006741: "MA Battle Islands V",
    940647: "Macedonia no split",
    940646: "Numenor",
    980613: "Phobia",
    940641: "Post-melt Antarctica",
    940492: "Strat ME",
    940490: "Strategic Greece",
    940487: "The World of Warhammer",
    940486: "Treasure Map",
    940484: "Unicorn Island",
    940479: "Yinyang'zhou",
    940476: "Belarus",
    940478: "Snowy Mountains MA",
    980617: "Volcano Island",
    1000099: "Randomized Strat ME",
    1121183: "Biomes of America",
    1124708: "Fast Earth",
    1124714: "Pangea Ultima",
    1124718: "Turkey LD",
    1124719: "Master Mania",
    1215811: "Blitzkrieg Bork",
    1298206: "Timid Lands",
    1298218: "Landria",
}

template_protips = {
    969173: "tfAiX1yZXuY",
    944620: "JbGPV9Fc628",
    945791: "5NbSsNWx0-8",
    940674: "ru91U2cjBjI",
    940484: "LaFkSScgdWQ",
    940492: "dIl9F5b4zwE",
    940658: "tv_dE_U-FNM",
    980608: "ANQxiOTWAIs",
    940676: "vwWjEECNCko",
    940669: "mCQ3jQMD18o",
    940639: "k3v7LCupnCE",
    940664: "gQ_WrNkGbOU",
    940656: "VivARaNdvfs",
    940660: "C5Q54OuSqaM",
    940641: "lBJDRac7d8Q",
    940479: "WstezmIV-3k",
    940646: "tbYFeafsMD0",
    940652: "zFY_HgVrL-U",
    940673: "OyZXzrF8DQU",
    940654: "jTnh64g0Edo",
    940478: "EqrcjI8Csm8",
    988665: "Do6Ed14WiCM",
    940490: "t4aRR8fIcAA",
    980615: "Z7cv8dy2Hqs",
    989118: "UmjmCLXbdIk",
    940647: "q8A2xJtYGqg",
    940675: "sllN-GlaimU",
    940670: "ZsyT3KXFtUc",
    940476: "qf2xRq2PT_8",
    940666: "ccnMaNz4G8o",
    940667: "MwQKbpBR4iY",
    1000099: "8rpfNJT8JPc",
    989165: "XN_2S9RX-yQ",
    989162: "sLb4T42ybqw",
    940659: "D81z_XozjC8",
    980617: "och5uWSRjnQ",
    1006748: "YkndD6y8nSs",
    940663: "ygxcHyOOBaQ",
    940486: "AgfUszBBhxg",
    942413: "tAUH3zwM13k",
    980613: "0PIzMSeFc0Y",
    1006746: "llrFUgyG_ig",
    940487: "Hh83KWGTUjk",
    1006752: "KmYuJhzxvzs",
    940665: "tcvsgci3Ddk",
    940662: "Tf4Pd6nl4e4",
    989159: "90NNnmUDhKM",
    988652: "5fnwUfd8BQY",
    1006750: "l40UMB8oQ08",
    988648: "o0HkK1--JIY",
}

# Dict of (templateId, exampleGameId)
randomized_templates = {
    1000099: 12995467,
}

BLACKLISTED_PLAYERS = [
    2920026449,
    9336062702,
    9584375174,
    732503825,
    2958204123,
    1840549224,
    2847280410,
    3040482585
]
