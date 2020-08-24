"""
This is a class that interfaces with the database

"""
from dotenv import load_dotenv
load_dotenv()
import os
import mysql.connector as mysql

class GeepNerve(object):
    HOST = os.getenv('DB_HOST')
    USERNAME = os.getenv("USERNAME")
    PASSWORD = os.getenv("PASSWORD")
    PORT = os.getenv("PORT")
    DATABASE = os.getenv("DATABASE")

    def __init__(self, phone):
        self.phone = '0' + phone.lstrip('234') #change 234813xx to 0813xx
        self.connection = mysql.connect(
        host= self.HOST,
        user= self.USERNAME,
        password= self.PASSWORD,
        database= self.DATABASE
        )
    
    def check_loan_status(self):
        cursor = self.connection.cursor(buffered=True)
        sql = "SELECT status FROM cmdc.cbr WHERE phone = %s"
        param = (self.phone, )

        cursor.execute(sql, param)
        result = cursor.fetchone()

        return result



        