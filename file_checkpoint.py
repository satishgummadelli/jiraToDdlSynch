
import re
from datetime import datetime,timedelta

CHECK_POINT_FILE_PATH = ""
CHECK_POINT_FILE_NAME = "samplecheckoint"


def get_checkpoint_time():
    last_updated_time=""
    with open(CHECK_POINT_FILE_PATH+CHECK_POINT_FILE_NAME, "r+") as file:
        print("reading it")
        last_updated_time = file.read()
    print(last_updated_time)
    if last_updated_time=="":
        last_updated_time = datetime.now() - timedelta(days=1)
    return last_updated_time


def update_checkpoint_time():
    with open(CHECK_POINT_FILE_PATH+CHECK_POINT_FILE_NAME, 'w+') as file:
        file.write(datetime.now().isoformat())
