from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from config.ClotConfig import ClotConfig
import logging


def backup_database():
    logging.getLogger("googleapiclient").setLevel(logging.ERROR)
    gauth = GoogleAuth()

    # Try to load saved client credentials
    gauth.LoadCredentialsFile("C:\\src\\MasterLadder\\MasterLadder\\config\\mycreds.txt")
    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()

    # Save the current credentials to a file
    gauth.SaveCredentialsFile("mycreds.txt")

    drive = GoogleDrive(gauth)

    file5 = drive.CreateFile({'title': 'MDL_database.db'})
    file5.SetContentFile(ClotConfig.database_location)
    file5.Upload() # Upload the file.
