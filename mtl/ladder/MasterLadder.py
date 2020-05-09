from time import sleep, clock
import datetime
from mtl.ladder.scheduler.scheduler import Scheduler
from mtl.ladder.utilities.clan_league_logging import get_logger


logger = get_logger()
if __name__ == "__main__":
    while True:
        start_time = clock()
        Scheduler.run()
        logger.info("Time Taken - %s seconds", round(clock() - start_time, 2))
        sleep(2 * 60 * 60)   # run every 15 minutes
