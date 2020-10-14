import logging
import sys

import requests
from jira import JIRA
from datetime import datetime, timedelta

import cyberark
import db
from update_from_jira_to_ddl import DESCRIPTION, STATUS, get_latest_field_value, JIRA_ID, DDL_ID
from app import JIRA_URL, DDL_URL


def check_and_update_description_field(jira_server, jira_issue, ddl_record):
    latest_updated_message = ""
    last_updated_time = None
    get_latest_field_value(jira_issue, DESCRIPTION, latest_updated_message, last_updated_time)
    if ddl_record[DESCRIPTION] != latest_updated_message:
        if ddl_record["lastModifiedDescriptionFieldTime"] > last_updated_time:
            # update jira
            print()


def check_and_update_id_field(jira_server, jira_issue, ddl_record):
    latest_updated_message = ""
    last_updated_time = None
    get_latest_field_value(jira_issue, JIRA_ID, latest_updated_message, last_updated_time)
    if ddl_record[DDL_ID] != latest_updated_message:
        if ddl_record["lastModifiedIdFieldTime"] > last_updated_time:
            print()


def check_and_update_jira_comment_to_ddl(jira_server, jira_issue, ddl_record):
    comment = jira_server.comments(jira_issue.id)
    a = int(0)
    for i in comment:
        if int(i.id) > a:
            a = int(i.id)
    print(jira_server.comment(jira_issue.id, a).body)
    jira_latest_comment = jira_server.comment(jira_issue.id, a).body
    # is the ddl has this comment in its records, if not update it


def check_and_update_status_field(target, jira_server, jira_issue, ddl_record):
    jira_latest_updated_status = ""
    jira_last_updated_time = None
    get_latest_field_value(jira_issue, STATUS, jira_latest_updated_status, jira_last_updated_time)

    # get status field last modified time in ddl and check which is latest
    if jira_latest_updated_status != get_jira_status(ddl_record[STATUS]):
        if ddl_record["lastModifiedStatusTime"] > jira_last_updated_time:
            print()


def compare_and_update_jira_to_ddl(last_job_run_time):
    try:
        cyberark_response = cyberark.get_jira_credentials()
        date_time_in_file = datetime.fromisoformat(last_job_run_time)
        jira_server = JIRA(basic_auth=(cyberark_response["UserName"], cyberark_response["Password"]),
                           options={'server': JIRA_URL})

        for ddl_record in get_ddl_response(last_job_run_time):
            jira_issu_id = db.get_jira_record_id_for_a_given_ddl_id(ddl_record.id)
            jira_issue = jira_server.issue(jira_issu_id, fields="comment", expand='changelog')
            check_and_update_description_field(jira_server, jira_issue, ddl_record)
            check_and_update_id_field(jira_server, jira_issue, ddl_record)
            check_and_update_jira_comment_to_ddl(jira_server, jira_issue, ddl_record)
            check_and_update_status_field(jira_server, jira_issue, ddl_record)
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


# ddl status to jira
# pending to validation
# testFailed to validation + comment
# testPassed to TechReview
# active to  Consumption
def get_jira_status(ddl_status):
    if ddl_status == "pending":
        return "Validation"
    elif ddl_status == "testFailed":
        return "Validation"
    elif ddl_status == "testPassed":
        return "Tech Review"
    elif ddl_status == "active":
        return "Consumption"


def get_ddl_json(param, param1):
    pass


