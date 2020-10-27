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

    def __init__(self, phone, product=''):
        self.phone = '0' + phone.lstrip('0234') #change 234813xx OR 0813x to 0813xx
        self.product = product
        self.connection = mysql.connect(
        host= self.HOST,
        user= self.USERNAME,
        password= self.PASSWORD,
        database= self.DATABASE
        )
    
    def check_loan_status(self):
        cursor = self.connection.cursor(buffered=True)
        sql = "SELECT status FROM cmdc.gcc_whtl WHERE phone = %s "
        param = (self.phone, )

        cursor.execute(sql, param)
        result = cursor.fetchone()

        return result
    
    def check_amount_owed(self):
        cursor = self.connection.cursor(buffered=True)
        sql = "SELECT amount_default from boi_nerve.boi_nerve_master where phone = %s"
        param = (self.phone, )

        cursor.execute(sql, param)
        result = cursor.fetchone()

        return result
    
    def check_loan_details(self):
        cursor = self.connection.cursor(buffered=True)
        sql = "SELECT disbursement, amount_due, total_payments_made, amount_default, date_disbursement, date_cashout from boi_nerve.boi_nerve_master where phone = %s"
        param = (self.phone, )

        cursor.execute(sql, param)
        result = cursor.fetchone()

        return result

    def check_amount_paid(self):
        cursor = self.connection.cursor(buffered=True)
        sql = "SELECT total_payments_made from boi_nerve.boi_nerve_master where phone = %s"
        param = (self.phone, )

        cursor.execute(sql, param)
        result = cursor.fetchone()

        return result
    
    def check_date_disbursed(self):
        cursor = self.connection.cursor(buffered=True)
        sql = "SELECT DATE_FORMAT(loan_disburse_date, '%d-%b-%Y') as ddate from cmdc.gcc_cbr_tmp where phone = %s "
        param = (self.phone, )

        cursor.execute(sql, param)
        result = cursor.fetchone()

        return result

    def save_request(self, request):
        cursor = self.connection.cursor(buffered=True)
        sql = "INSERT INTO cmdc.bot_requests (request) VALUES ( %s)"
        param = (request, )
        cursor.execute(sql, param)
        self.connection.commit()

        # print(cursor.rowcount, "record inserted.")
        pass




        