import requests

CYBER_ARK_URL = ""
# jira specific keys
CYBER_ARK_JIRA_SAFE_ID = ""
CYBER_ARK_JIRA_PASSWORD_NAME = ""
CYBER_ARK_JIRA_APP_ID = ""
# ddl specific keys
CYBER_ARK_DDL_SAFE_ID = ""
CYBER_ARK_DDL_PASSWORD_NAME = ""
CYBER_ARK_DDL_APP_ID = ""


def get_jira_credentials():
    get_credentials_from_cyber_ark(CYBER_ARK_JIRA_SAFE_ID, CYBER_ARK_JIRA_APP_ID,
                                   CYBER_ARK_JIRA_PASSWORD_NAME)


def get_ddl_credentials():
    get_credentials_from_cyber_ark(CYBER_ARK_DDL_SAFE_ID, CYBER_ARK_DDL_APP_ID,
                                   CYBER_ARK_DDL_PASSWORD_NAME)


def get_credentials_from_cyber_ark(safe, appid, password_name):
    headers = {'Content-type': 'application/json'}
    params = {'Safe': safe, 'Password_name': password_name, 'AppID': appid}
    results = requests.get(url=CYBER_ARK_URL, params=params, timeout=10, verify=False, headers=headers)
    response = results.json()
    return response
