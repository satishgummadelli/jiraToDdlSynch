from jira import JIRA
from datetime import datetime, timedelta


def check_and_update_description_field(jira_issue, ddl_record):
    latest_updated_message = ""
    last_updated_time = None
    for history in jira_issue.changelog.histories:
        item_updated_time = datetime.strptime(history.created, "%Y-%m-%dT%H:%M:%S.%f%z")
        if last_updated_time is None or last_updated_time <= item_updated_time:
            last_updated_time = item_updated_time
            for item in history.items:
                if item.field == 'description':
                    latest_updated_message = item.toString
    print(latest_updated_message)
    print(last_updated_time)


def check_and_update_jira_comment_to_ddl(jira_issue, ddl_record):
    latest_updated_comment = ""
    last_updated_time = None
    comment = jira_server.comments(jira_issue.id)
    a = int(0)
    for i in comment:
        if int(i.id) > a:
            a = int(i.id)
    print(jira_server.comment(jira_issue.id, a).body)


def update_ddl_to_jira_comment():
    pass


def get_ddl_status1_update_time(ddl_record):
    return datetime.strptime("2020-10-07T15:29:08.303000+00:00", "%Y-%m-%dT%H:%M:%S.%f%z")


def update_ddl_status(param):
    pass


def check_and_update_status_field(jira_issue, ddl_record):
    jira_latest_updated_status = ""
    jira_last_updated_time = None
    for history in jira_issue.changelog.histories:
        item_updated_time = datetime.strptime(history.created, "%Y-%m-%dT%H:%M:%S.%f%z")
        if jira_last_updated_time is None or jira_last_updated_time <= item_updated_time:
            jira_last_updated_time = item_updated_time
            for item in history.items:
                if item.field == 'status':
                    if item.toString == "Validation" or item.toString == "Consumption":
                        jira_latest_updated_status = item.toString
    # get status field last modified time in ddl and check which is latest
    ddl_last_updated_time = get_ddl_status1_update_time(ddl_record)

    if ddl_last_updated_time > jira_last_updated_time:
        jira_server.transition_issue(jira_issue.id, get_jira_status(ddl_record["status"]), None)
    else:
        update_ddl_status(get_ddl_status(jira_latest_updated_status))
    # ddl status to
    print(jira_latest_updated_status)
    print(jira_last_updated_time)


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


def get_ddl_status(jira_status):
    if jira_status == "Validation":
        return "pending"
    elif jira_status == "Consumption":
        return "active"




jira_server = JIRA(basic_auth=("satishgummadelli", "JiraPassword"), options={'server': 'http://localhost:8080'})
issues_Jql = jira_server.search_issues('project=ltest AND assignee=satishgummadelli And updated > "2020-10-07 01:45"')

for issue in issues_Jql:
    jira_issue = jira_server.issue(issue.id, fields="comment",expand='changelog')
    #check_and_update_description_field(jira_issue, None)
    #check_and_update_status_field(jira_issue, None)
    check_and_update_jira_comment_to_ddl(jira_issue, None)
    # for history in changelog.histories:
    #     print("history")
    #     print(history)
    #     for item in history.items:
    #         print(item.toString)
    #         if item.field == 'status':
    #             print('Date:' + history.created + ' From:' + item.fromString + ' To:' + item.toString)
    #         if item.field == 'description':
    #             print('Date:' + history.created + ' From:' + item.fromString + ' To:' + item.toString)


