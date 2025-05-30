import datetime
import pyodbc
from app.settings import env
from sentry_sdk import capture_exception

class SQLHandler:

    def __init__(self, user=None):
        self.cursor = None
        try:
            server = env.str("SQL_SERVER")
            db = env.str("SQL_DB")
            user = env.str("SQL_USER")
            password = env.str("SQL_PASSWORD")
            driver = "DRIVER={" + env.str("SQL_DRIVER", default="ODBC Driver 18 for SQL Server") + "};"
            connect_to = f"SERVER={server};DATABASE={db};ENCRYPT=no;UID={user};PWD={password}"
            self.conn = pyodbc.connect(driver + connect_to)
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(e)
            capture_exception(e)

        self.user = user

    # Customer Validation

    def validate_customer_number(self, customer_number):
        self.cursor.execute(f"SELECT CUSTNMBR, CUSTNAME FROM RM00101 WHERE CUSTNMBR = {customer_number}")
        result = self.cursor.fetchone()
        if result:
            return {
                'company_name': result.CUSTNAME.strip(),
                'customer_number': result.CUSTNMBR.strip()
            }

