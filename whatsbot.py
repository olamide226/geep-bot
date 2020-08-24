#####!/usr/bin/env python3
"""
whatsbot.py

 * Copyright © 2020 EBIS LTD <olamideadebayo2001@gmail.com>
 * 
 * 
 * All Rights Reserved. 
 * This program/software is a protected software and 
 * cannot be copied, modified, reproduced, stored or 
 * translated in any form without EBIS LIMITED express 
 * written agreement and permission.
 * 
 * 
 * Date:                        2020-07-09
 * Title:                      Whatsapp Chat Bot 
 * Version:             1.0
 * Description:  This is an interactive bot that offers an interactive support
 * to current beneficiaries 
 * .
 * .
 * Dependencies:
"""
import requests
import redis
from urllib.parse import quote_plus
import re
from nerve import GeepNerve
# import inspect

class WhatsBot:
    
    def __init__(self, sender, message):

        self.redis = redis.Redis(decode_responses=True)
        self.sender = sender
        self.message = message.strip().lower()
        self.userid = 'user:' + sender
        
        #check if user exist before else initialize
        if not self.redis.exists(self.userid):
            self.redis.hmset(self.userid, {'id': sender, 'menu': 'default'})
            self.redis.expire(self.userid, 21600) #keep user session data for 6 hrs
        
        # Reg_sender is the registered no used to fetch from the database
        self.reg_sender = self.redis.hget(self.userid, 'id')
        #set cuurent menu
        self.current_menu = self.redis.hget(self.userid, 'menu')
        self.sub_menu = self.redis.hget(self.userid, 'sub_menu')



            
    def __str__(self):
        return self.response.text.encode('utf8')
    
    def reply(self):
        """ Add Top level menus here if it has sub menus else leave to main_menu() to handle """
        
        return {
        # 'default': self.greet,
        'main': self.main_menu,
        'enquiry': Enquiry,
        'loan_status': LoanStatus,

        }.get(self.current_menu, self.unknown_response)

    def send_message(self, msg):
        url = "https://api.gupshup.io/sm/api/v1/msg"
        source = '917834811114'
        msg = quote_plus(msg)
        destination=self.sender
        app_name = 'GEEPNG'
        payload = 'source={}&channel=whatsapp&destination={}&src.name={}&message={}'. \
        format(source, destination, app_name, msg)
        headers = {
        'apikey': 'a549c98c3076406cc051e51a751fc96c',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded'
        }
        # self.msg = msg

        self.response = requests.request("POST", url, headers=headers, data = payload)
        # print(msg)
        return self.response.json()
        # return {'message': self.msg}
        # return (response.text.encode('utf8'))
    
    def welcome(self):
        
        #Check For A Greeting to activate interactive bot
        if re.search('(hello|holla|hey|how|hi|yo|what|good)', self.message):

            #SET current menu to main menu for the current user
            self.redis.hmset(self.userid, {'menu': 'main', 'sub_menu': ''})

            msg = """*Welcome to GEEP*\n
*WHAT WOULD YOU LIKE TO DO* 

1. Enquiry
2. Check your Loan status
3. Repayment Options
4. Request For Next Loan
5. Logout
_To make a selection, reply with the number *ONLY* of your option._\n
*EXAMPLE:* Reply with *1* to make Enquiry
            """

            return self.send_message(msg) #end whatsapp message
        else:
            return False

    def main_menu(self, args='', args2=''):
        """ globals()['classname-or-functionname']( args )  """

        menus = ['1', '2', '3', '4', '5']
        if self.message not in menus:
            return self.unknown_response()

        menus = dict([('1', 'Enquiry'), ('2', 'LoanStatus'), ('3', 'RepayOptions'),
                ('4', 'NextLoan'), ('5', 'Logout')])

        return globals()[ menus[ self.message ] ]( self.sender, 'init' ) 
        
    def logout(self):
        """ This function destroys session data """
        self.redis.unlink(self.userid)
        return self.send_message("Thank you for your time  👏")
    
    def unknown_response(self, args='', args2=''):
        if self.welcome(): return 'OK'

        return self.send_message("Kindly enter a valid response")
        ##End of WhatsBot Class##


class Enquiry(WhatsBot):
    def __init__(self, sender, message):
        super().__init__(sender, message)
        self.redis.hset(self.userid, 'menu','enquiry')
        if self.message == 'init':
            self.greet()
        else:
            self.respond() 

    def greet(self):
        self.redis.hset(self.userid, 'sub_menu','enquiry_main')

        msg = """ *WHAT WOULD YOU LIKE TO DO* 

1. Request For Loan
2. Loan Terms and Conditions
3. Call The Customer Care 

_To make a selection, reply with the number *ONLY* of your option._

Type Hi to return to Main Menu
"""
        return self.send_message(msg)
    
    def respond(self):
        menus = ['1', '2', '3']
        if self.message not in menus:
            return self.unknown_response()
        
        func = dict([('1', self.request_loan), ('2', self.loan_terms), ('3', self.call_support) ])
        return func[ self.message ]()

    def request_loan(self):
        msg = """Kindly locate a Tradermoni agent close to you in order to capture your biodata and biometrics. 
They will require information on what and where you sell e.t.c.

Say *Hello* to return to Main Menu """

        return self.send_message(msg)
    
    def loan_terms(self):
        msg = """The Loan Products are:
- ₦10,000
- ₦15,000
- ₦20.000
- ₦25,000

If you pay your first ₦10,000 within 6 months, you will qualify to borrow ₦15,000.
After repayment of ₦15,000 within 6 months, you will qualify to borrow ₦20,000.
After repayment of ₦20,000 within 6 months, you will qualify to borrow ₦25,000.

When you payback the first loan given within 6 months you will be given another loan within 2 days of repayment

Type *Hi* to return to Main Menu """

        return self.send_message(msg)

    def call_support(self):
        msg = """The Number to call is *0700 1000 2000* for TraderMoni OR *0700 627 5386* for MarketMoni"""

        return self.send_message(msg)
        

class LoanStatus(WhatsBot):
    def __init__(self, sender, message):
        # curframe = inspect.currentframe()
        # calframe = inspect.getouterframes(curframe, 2)
        # print('LoanStatus init caller name:', calframe[1][3])
        super().__init__(sender, message)
        self.redis.hset(self.userid, 'menu','loan_status')
        if self.message == 'init':
            self.greet()
        else:
            self.respond()
    
    def greet(self):
        # curframe = inspect.currentframe()
        # calframe = inspect.getouterframes(curframe, 2)
        # print('LoanStatus caller name:', calframe[1][3])

        self.redis.hset(self.userid, 'sub_menu','loan_status_main')
        print('loan status greet function')
        msg = """*WHAT WOULD YOU LIKE TO DO*

1. Check Status Of Your Loan Application
2. Check How Much You Are Owing

_To make a selection, reply with the number ONLY of your option._

Type *Hi* to return to Main Menu
        """
        return self.send_message(msg)
    
    def respond(self):
        menus = ['1', '2']
        if self.message not in menus:
            return self.unknown_response()
        
        func = dict([ ('1', self.check_loan_status), ('2', self.check_amount_owed) ])
        return func[ self.message ]()

    def unknown_number(self, phone):
        self.redis.hset(self.userid, 'last_message', self.message)
        self.redis.hset(self.userid, 'sub_menu','loan_status_main')

        msg = """*Please confirm your registered phone number*

1. {} is my registered phone number
2. Enter my registered phone number  

_To make a selection, reply with the number ONLY of your option._ """

        return self.send_message(msg)

    def check_loan_status(self):
        status = GeepNerve(self.reg_sender)
        status = status.check_loan_status()
        if not status: return self.unknown_number(self.reg_sender)

        if status[0] == 'LoanDisbursedSuccessfully':
            msg = 'Your loan has been disbursed successfully'
        elif status[0] in ['PendingApproval', 'PendingCustomerConfirmation', 'PendingFIreConfirmation', 'PendingICUConfirmation']:
            msg = "Your loan application is being processed"
        elif status[0] == 'DueForDisbursement':
            msg = 'Your loan application is due for disbursement'
        else:
            msg = 'Your loan application was unsuccessful'

        return self.send_message(msg)

    def check_amount_owed(self):
        msg = "coming soon..."

        return self.send_message(msg)


class RepayOptions(WhatsBot):
    def __init__(self, sender, message):
        super().__init__(sender, message)
        # self.redis.hset(self.userid, 'menu','repay_options')
        if self.message == 'init':
            self.greet()

    
    def greet(self):
        msg="""Locate any bank close to you - Meet a bank cashier and tell them you want to use interswitch paydirect 
to pay for BOI Marketmoni/Tradermoni loan. They will ask you for a reference code or the phone number you registered with.
*OR* 
You can buy the Tradermoni scratch card from any Tradermoni onecard agent where you are and you will be guided how to use it.

Type *Hi* to return to Main Menu """

        return self.send_message(msg)


class NextLoan(WhatsBot):
    def __init__(self, sender, message):
        super().__init__(sender, message)
        # self.redis.hset(self.userid, 'menu','')
        if self.message == 'init':
            self.greet()

    def greet(self):
        msg= "coming soon..."

        return self.send_message(msg)

class Logout(WhatsBot):
    def __init__(self, sender, message):
        super().__init__(sender, message)
        super().logout()





