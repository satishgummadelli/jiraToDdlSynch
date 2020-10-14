from jira import JIRA
from datetime import datetime, timedelta
import json
import requests
import logging
import cyberark
import update_from_ddl_to_jira
from app import JIRA_PROJECT_NAME, JIRA_URL
import sys
import db
import app


ISO_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"

DESCRIPTION = 'description'
JIRA_ID = "jira_id"
DDL_ID = "id"
STATUS = "status"
TYPE = "type"
FIELDS = 'fields'
FIELD = "field"
VALUE = "value"
OUTPUTS = "outputs"
NAME = "name"
INDEX = "index"
SOURCE_TYPE = "sourcetype"


DDL_SSO_UPDATE_URL = "/sso/update-fields/"


def check_and_update_description_field(target, jira_server, jira_issue, ddl_record):
    latest_updated_message = ""
    last_updated_time = None
    get_latest_field_value(jira_issue, DESCRIPTION, latest_updated_message, last_updated_time)
    if ddl_record[DESCRIPTION] != latest_updated_message:
        if last_updated_time > get_ddl_status_update_time:
            description_field = "\"" + FIELD + "\": \"" + DESCRIPTION + "\", \"" + VALUE + "\": \"" + latest_updated_message + "\""
            fields = "{" + description_field + "}"
            target[FIELDS].append(json.loads(fields))
            target[TYPE] = DESCRIPTION
    print(latest_updated_message)
    print(last_updated_time)


def check_and_update_id_field(target, jira_server, jira_issue, ddl_record):
    latest_updated_message = ""
    last_updated_time = None
    get_latest_field_value(jira_issue, JIRA_ID, latest_updated_message, last_updated_time)
    if ddl_record[DDL_ID] != latest_updated_message:
        if last_updated_time > get_ddl_status_update_time():
            id_field = "\"" + FIELD + "\": \"" + DDL_ID + "\", \"" + VALUE + "\": \"" + latest_updated_message + "\""
            fields = "{" + id_field + "}"
            target[FIELDS].append(json.loads(fields))
            target[TYPE] = JIRA_ID



def check_and_update_jira_comment_to_ddl(target, jira_server, jira_issue, ddl_record):
    comment = jira_server.comments(jira_issue.id)
    a = int(0)
    for i in comment:
        if int(i.id) > a:
            a = int(i.id)
    print(jira_server.comment(jira_issue.id, a).body)
    jira_latest_comment = jira_server.comment(jira_issue.id, a).body
    # is the ddl has this comment in its records, if not update it
    comment_field = "\"" + NAME + "\": \"splunk\", \"" + INDEX + "\": \"" + "0" + "\", \"" + VALUE + "\": \"" + jira_latest_comment + "\""
    outputs = "{" + comment_field + "}"
    target[OUTPUTS].append(json.loads(outputs))
    target[TYPE] = "comment"


def check_and_update_status_field(target, jira_server, jira_issue, ddl_record):
    jira_latest_updated_status = ""
    jira_last_updated_time = None
    get_latest_field_value(jira_issue, STATUS, jira_latest_updated_status, jira_last_updated_time)

    # get status field last modified time in ddl and check which is latest
    ddl_last_updated_time = get_ddl_status_update_time(ddl_record)
    if jira_latest_updated_status != update_from_ddl_to_jira.get_jira_status(ddl_record[STATUS]):
        if jira_last_updated_time > ddl_last_updated_time:
            target[STATUS] = update_from_ddl_to_jira.get_ddl_status(jira_latest_updated_status)
            target[TYPE] = STATUS



def update_ddl_to_jira_comment():
    pass


def get_ddl_status_update_time(ddl_record):
    return datetime.strptime("2020-10-07T15:29:08.303000+00:00", "%Y-%m-%dT%H:%M:%S.%f%z")


def is_valid_jira_status(item):
    if item.field == STATUS:
        if item.toString == "Validation" or item.toString == "Consumption":
            return True
    return False


def is_description_field(item):
    if item.field == DESCRIPTION:
        return True
    return False

def is_jira_id_field(item):
    if item.field == JIRA_ID:
        return True
    return False

def get_latest_field_value(jira_issue, field_to_check, latest_updated_message, last_updated_time):
    for history in jira_issue.changelog.histories:
        item_updated_time = datetime.strptime(history.created, ISO_DATE_FORMAT)
        if last_updated_time is None or last_updated_time <= item_updated_time:
            last_updated_time = item_updated_time
            for item in history.items:
                if field_to_check == STATUS:
                    if is_valid_jira_status(item):
                        latest_updated_message = item.toString
                elif field_to_check == DESCRIPTION:
                    if is_description_field(item):
                        latest_updated_message = item.toString
                elif field_to_check == JIRA_ID:
                    if is_jira_id_field(item):
                        latest_updated_message = item.toString


def get_ddl_status(jira_status):
    if jira_status == "Validation":
        return "pending"
    elif jira_status == "Consumption":
        return "active"


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
            target = {}
            target[FIELDS] = []
            target[OUTPUTS] = []
            jira_issue = jira_server.issue(issue.id, fields="comment", expand='changelog')
            db_response = db.get_ddl_record_id_for_a_given_jira_id(issue.id)
            #TO-DO how to get the specific ddl record
            update_from_ddl_to_jira.get_ddl_json(db_response["targetId"], db_response["plural"])

            update_from_ddl_to_jira.check_and_update_description_field(target, jira_server,jira_issue, None)
            update_from_ddl_to_jira.check_and_update_id_field(target, jira_server, jira_issue, None)
            update_from_ddl_to_jira.check_and_update_jira_comment_to_ddl(target, jira_server, jira_issue, None)
            update_from_ddl_to_jira.check_and_update_status_field(target, jira_server, jira_issue, None)
            #now check is the target field and update
            if target[TYPE] is not None or target[TYPE] != "":
                requests.post(app.DDL_URL+DDL_SSO_UPDATE_URL, data=target)
    except:
        logging.error("Unexpected error:", sys.exc_info()[0])
        raise