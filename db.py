import pyodbc

DATABASE_SERVER_IP = ""
DATABASE_NAME = ""
DATABASE_USER_ID = ""
DATABASE_PASSWORD = ""
DATABASE_DRIVER = "{ODBC Driver 17 for SQL Server}"
DATABASE_CONNECTION_STRING = 'DRIVER=' + DATABASE_DRIVER + ';SERVER=' + DATABASE_SERVER_IP + ';DATABASE=' + DATABASE_NAME + ';UID=' + DATABASE_USER_ID + ';PWD=' + DATABASE_PASSWORD
DATABASE_TABLE_NAME = "ddl_sso"
DATABASE_QUERY_STRING="SELECT s.ddl_id, p.pattern_crd_plural inner join pattern p on s.pattern_id= p.pattern_id where"


def get_ddl_record_id_for_a_given_jira_id(jira_id):
    return get_records_from_database(DATABASE_QUERY_STRING+"jira_id='" + jira_id + "'")


def get_jira_record_id_for_a_given_ddl_id(ddl_id):
    return get_records_from_database(DATABASE_QUERY_STRING + "ddl_id='" + ddl_id + "'")


def get_records_from_database(query):
    conn = pyodbc.connect(DATABASE_CONNECTION_STRING)
    cursor = conn.cursor()
    cursor.execute(query)
    row = cursor.fetchone()
    ddl_response = dict(
        targetId=row[1],
        plural=row[2])
    conn.close()
    del cursor
    return ddl_response

