import requests
import string
import random


class APIError(Exception):
    """
    Error class that should simply output errors
    raised by the Warlight API itself
    """
    pass

class ServerGameKeyNotFound(Exception):
    """
    Error clas for nonexistent games
    """

def makePlayers(teams):
    """
    Given teams, returns a list
    containing player dictionaries
    PARAMETERS:
    teams: list of teams as tuples of player IDs
    """    
    players = list()
    for team in teams:
        if (type(team) == tuple):
            for member in team[1:]:
                player = dict()
                player['token'] = str(member)
                player['team'] = str(team[0])
                players.append(player)
    return players

def overrideBonuses(email, token, example_game_id):
    """
    Given an example game, extract the bonus values and alter them.
    Generate a new list containing tuples with bonus name and new values,
    in dictionary form
    """
    overridenBonuses = list()
    resp = queryGame(email, token, example_game_id, True)
    bonuses = [];
    for bonus in resp["map"]["bonuses"]:
        original_val = int(bonus["value"])
        if original_val !=0:
            # set the bonus value to (original-1, original+1)
            new_val = random.randint(original_val - 1, original_val + 1)
            bonusData = dict()
            bonusData['bonusName'] = bonus["name"]
            bonusData['value'] = new_val
            overridenBonuses.append(bonusData)
    return overridenBonuses

def getAPIToken(email, password):
    """
    Gets API token using email and password
    """
    site = "https://www.warlight.net/API/GetAPIToken"
    data = dict()
    data['Email'] = email
    data['Password'] = password
    r = requests.post(url=site, params=data)
    jsonOutput = r.json()
    if 'error' in jsonOutput:
        raise APIError(jsonOutput['error'])
    return jsonOutput['APIToken']

def queryGame(email, token, gameID, getHistory=False):
    """
    Queries a game given gameID
    using credentials (email+token)
    returns JSON output
    """
    getHistory = str(getHistory).lower()
    site = "https://www.warlight.net/API/GameFeed"
    data = dict()
    data['Email'] = email
    data['APIToken'] = token
    data['GameID'] = str(gameID)
    data['GetHistory'] = getHistory
    r = requests.post(url=site, params=data)
    jsonOutput = r.json()
    if 'error' in jsonOutput:
        if ("ServerGameKeyNotFound" in jsonOutput['error']):
            raise ServerGameKeyNotFound(jsonOutput['error'])
        raise APIError(jsonOutput['error'])
    return jsonOutput

def createGame(email, token, **settings):
    """
    Creates a game given settings
    using credentials (email+token)
    returns game ID
    """
    site = "https://www.warlight.net/API/CreateGame"
    data = dict()
    data['hostEmail'] = email
    data['hostAPIToken'] = str(token)
    data['templateID'] = settings.get('template')
    data['gameName'] = settings.get('gameName')
    data['personalMessage'] = settings.get('message', "")
    teams = settings.get('teams')
    data['players'] = makePlayers(teams)
    if 'overriddenBonuses' in settings and settings.get('overriddenBonuses'):
        if 'exampleGame' in settings:
            example_game_id = settings.get('exampleGame')
            data['overriddenBonuses'] = overrideBonuses(email, token, example_game_id)
    r = requests.post(url=site, json=data)
    jsonOutput = r.json()
    if 'error' in jsonOutput:
        raise APIError(jsonOutput['error'])
    
    return jsonOutput['gameID']

def deleteGame(email, token, gameID):
    """
    Deletes a game
    using credentials (email+token)
    does not return anything
    """
    site = "https://www.warlight.net/API/DeleteLobbyGame"
    data = dict()
    data['Email'] = email
    data['APIToken'] = str(token)
    data['gameID'] = int(gameID)
    r = requests.post(url=site, json=data)
    jsonOutput = r.json()
    if 'error' in jsonOutput:
        raise APIError(jsonOutput['error'])
    if 'success' not in jsonOutput:
        raise APIError("Unknown error!")


def validate_token(email, token, player, *templates):
    """
    Validates an inviteToken
    using credentials (email+token)
    returns response
    """
    site = "https://www.warlight.net/API/ValidateInviteToken"
    data = dict()
    data['Email'] = email
    data['APIToken'] = token
    data['Token'] = player
    data['TemplateIDs'] = templates
    r = requests.post(url=site, params=data)
    json_output = r.json()
    if 'error' in json_output:
        raise APIError(json_output['error'])
    return json_output

def grantTrophy(email, token, player):
    """
    Grants a trophy for #1 on MDL
    using credentials (email+token)
    returns response
    """
    site = "https://www.warlight.net/API/GrantAward"
    data = dict()
    data['email'] = email
    data['APIToken'] = token
    data['Player'] = player
    data['Award'] = "MotdLadderTrophy"
    r = requests.post(url=site, json=data)
    jsonOutput = r.json()
    if 'error' in jsonOutput:
        raise APIError(jsonOutput['error'])
    return jsonOutput
