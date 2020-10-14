from datetime import datetime, timedelta
import time
import os
import re
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from jira import JIRA
import logging
import sys
import pyodbc

import update_from_jira_to_ddl
import update_from_ddl_to_jira
import file_checkpoint
import cyberark
import db

JIRA_URL = "http://localhost:80808"
JIRA_USER_NAME = ""
JIRA_PROJECT_NAME = "ltest"

DDL_URL = "http://ddl-api2.gdn.network/"

SYNCH_JOB_TIME_INTERVAL_IN_SECONDS = 120


def compare_and_update_ddl_to_jira(jira_issues, ddl_records):
    pass



def run_scheduler_jobs():
    try:
        last_job_run_time = file_checkpoint.get_checkpoint_time()

        update_from_jira_to_ddl.compare_and_update_jira_to_ddl(last_job_run_time)
        ddl_records = get_ddl_response(last_job_run_time)

        file_checkpoint.update_checkpoint_time()
    except:
        logging.error("Unexpected error:", sys.exc_info()[0])
        raise




if __name__ == '__main__':
    logging.basicConfig(filename='apps.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)
    logging.info('This will get logged to a file')
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_scheduler_jobs, 'interval', seconds=SYNCH_JOB_TIME_INTERVAL_IN_SECONDS)
    scheduler.start()
    logging.info('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except:
        scheduler.shutdown()
        logging.error('shutting down with exception')
