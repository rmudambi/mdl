from utilities.SheetHelper import SheetHelper
from setup.Group import Group
from setup import Roster
from vacations import Tracker
#from scheduler.Scheduler import Scheduler

def run():
    docName = "MAL"
    playerSheetName = "Players"

    playerSheet = SheetHelper.get_or_create_sheet(playerSheetName)
    tournaments = Roster.build_tournament_roster(rosterSheet, groups)

    tracker = Tracker.Tracker(rosterSheet, tournaments)
    
    ## ONE TIME OPERATION ONLY. DO NOT RE-RUN
    #tracker.create_vacation_sheet()
    tracker.track_vacations()
    pass

    #for i, groupName in enumerate(groups):
    #    groupSheet = SheetHelper.get_or_create_sheet(groupName)

    #    ## Turn on only once at the beginning
    #    #group = Group(groupSheet, rosterSheet, groupName, groupSize[i])

    #    group_scheduler = Scheduler(groupSheet, tournaments, groupSize[i], groupName)
    #    group_scheduler.run()
    #pass