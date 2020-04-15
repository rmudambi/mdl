from time import sleep
import datetime
from run import run
from utilities.clan_league_logging import get_logger


logger = get_logger()
if __name__ == "__main__":
    while True:
        try:
            run()
            logger.info("Last run time - %s", datetime.datetime.now().strftime('%m/%d/%Y - %H:%M:%S'))
        except Exception as ex:
            logger.error("Failed with - %s", ex)

        sleep(3 * 60 * 60)   # run every 3 hours
