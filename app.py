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

import map_ddl_to_jira
import map_jira_to_ddl
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
        compare_and_update_jira_to_ddl(last_job_run_time)
        ddl_records = get_ddl_response(last_job_run_time)
        file_checkpoint.update_checkpoint_time()
    except:
        logging.error("Unexpected error:", sys.exc_info()[0])
        raise


def get_ddl_json(param, param1):
    pass


def compare_and_update_jira_to_ddl(last_job_run_time):
    try:
        cyberark_response = cyberark.get_jira_credentials()
        date_time_in_file = datetime.fromisoformat(last_job_run_time)
        jira_server = JIRA(basic_auth=(cyberark_response["UserName"], cyberark_response["Password"]), options={'server': JIRA_URL})
        issues = jira_server.search_issues(
            'project=' + JIRA_PROJECT_NAME + ' And updated > "' + str(date_time_in_file.date()) + " " + str(
                date_time_in_file.time())[0:5] + '"')
        logging.info('got jira issues')
        for issue in issues:
            jira_issue = jira_server.issue(issue.id, fields="comment", expand='changelog')
            db_response = db.get_ddl_record_id_for_a_given_jira_id(issue.id)
            get_ddl_json(db_response["targetId"], db_response["plural"])
            map_jira_to_ddl.check_and_update_description_field(jira_issue, None)
            map_jira_to_ddl.check_and_update_status_field(jira_issue, None)
            map_jira_to_ddl.check_and_update_jira_comment_to_ddl(jira_issue, None)
    except:
        logging.error("Unexpected error:", sys.exc_info()[0])
        raise


def get_ddl_response(last_job_run_time):
    try:
        url = DDL_URL + "/sso/updates/" + str(last_job_run_time)
        response = requests.request("GET", url, headers={}, data={})
        return response.json()
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
