"""
This is a class that interfaces with the database

"""
from dotenv import load_dotenv
load_dotenv()
import os
import mysql.connector as mysql

class GeepNerve:
    HOST = os.getenv('DB_HOST')
    USERNAME = os.getenv("USERNAME")
    PASSWORD = os.getenv("PASSWORD")
    PORT = os.getenv("PORT")
    DATABASE = os.getenv("DATABASE")

    def __init__(self, phone, product):
        self.phone = '0' + phone.lstrip('0234') #change 234813xx to 0813xx
        self.product = 'product'
        self.connection = mysql.connect(
        host= self.HOST,
        user= self.USERNAME,
        password= self.PASSWORD,
        database= self.DATABASE
        )
    
    def check_loan_status(self):
        cursor = self.connection.cursor(buffered=True)
        sql = "SELECT status FROM cmdc.gcc_cbr_tmp WHERE phone = %s "
        param = (self.phone, )

        cursor.execute(sql, param)
        result = cursor.fetchone()

        return result
    
    def check_amount_owed(self):
        cursor = self.connection.cursor(buffered=True)
        sql = "SELECT amount_due from geep_nerve.boi_nerve_master where phone = %s"
        param = (self.phone, )

        cursor.execute(sql, param)
        result = cursor.fetchone()

        return result
    
    def check_date_disbursed(self):
        cursor = self.connection.cursor(buffered=True)
        sql = "SELECT loan_disburse_date from cmdc.gcc_cbr_tmp where phone = %s "
        param = (self.phone, )

        cursor.execute(sql, param)
        result = cursor.fetchone()

        return result




        