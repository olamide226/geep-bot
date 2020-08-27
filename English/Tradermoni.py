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
        if not self.redis.hget(self.userid, 'id'):
            self.redis.hset(self.userid, 'id', sender)
            # self.redis.expire(self.userid, 21600) #keep user session data for 6 hrs
        
        # Reg_sender is the registered no used to fetch from the database
        self.reg_sender = self.redis.hget(self.userid, 'id')
        #set cuurent menu
        self.current_menu = self.redis.hget(self.userid, 'menu')
        self.sub_menu = self.redis.hget(self.userid, 'sub_menu')



            
    def __str__(self):
        try:
            return self.response.text.encode('utf8')
        except AttributeError:
            return 'ok'


    
    def reply(self):
        """ Add Top level menus here if it has sub menus else leave to main_menu() to handle """
        
        return {
        # 'default': self.greet,
        'main': self.main_menu,
        'enquiry': Enquiry,
        'loan_status': LoanStatus,
        'unknown_number': UnknownNumber

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
        if '#' == self.message:

            #SET current menu to main menu for the current user
            self.redis.hmset(self.userid, {'menu': 'main', 'sub_menu': ''})

            msg = """*Welcome to GEEP*\n
*WHAT WOULD YOU LIKE TO DO* 

1. Enquiry
2. Check your Loan status
3. Repayment Options
4. Request For Upgrade
5. Logout

_To make a selection, reply with the number *ONLY* of your option._

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

        msg = "Thank you for using this medium to stay in touch with us."
        msg += "\nFor more information kindly visit our website www.geep.ng or call 070010002000"
        
        return self.send_message(msg)
    
    def unknown_response(self, args='', args2=''):
        if self.welcome(): return 'OK'

        return self.send_message("Kindly enter a valid response")
    
    
        ##End of WhatsBot Class##

class UnknownNumber(WhatsBot):
    def __init__(self, sender, message, prev_menu=None, last_msg=None):
        print(1)
        super().__init__(sender, message)
        print(2)
        if self.message == 'init':
            print(3)
            # Set the menus if it is the first time
            self.redis.hmset( self.userid, 
            { 'menu': 'unknown_number', 'prev_menu': prev_menu, 'last_message': last_msg}
        )
            self.greet()
        else:
            self.respond()
    

    def greet(self):

        msg = """ *Please confirm your registered phone number*

1. {} is my registered phone number
2. Enter my registered phone number  

_To make a selection, reply with the number ONLY of your option._ """.format(self.reg_sender)

        return self.send_message(msg)

    def respond(self):

        if re.findall(r"\d{13}", self.message):
            return self.set_new_number(self.message)

        menus = ['1', '2']
        if self.message not in menus:
            return self.unknown_response()
        
        func = dict([('1', self.not_found), ('2', self.get_new_number) ])
        return func[ self.message ]()

    def not_found(self):
        msg = "Sorry, Your phone number does not exist in our records"

        return self.send_message(msg)

    def get_new_number(self):
        msg = "Please enter your number in the format *2348012345678*"

        return self.send_message(msg)

    def set_new_number(self, new_number):

        self.redis.hset(self.userid, 'id', new_number)
        self.current_menu = self.redis.hget(self.userid, 'prev_menu')
        last_message = self.redis.hget(self.userid, 'last_message')
        next_menu = self.reply()

        next_menu(self.sender, last_message).__str__()
        return



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

        msg = """ *What would you like to know?* 

1. About Tradermoni
2. How to Register 
#. Return To Main Menu

_To make a selection, reply with the number *ONLY* of your option._
"""
        return self.send_message(msg)
    
    def respond(self):
        menus = ['1', '2']
        if self.message not in menus:
            return self.unknown_response()
        
        sub_menus = dict([('1', self.about), ('2', self.how_to_register), ('3', self.call_support) ])
        return sub_menus[ self.message ]()

    def about(self):
        msg = """GEEP TraderMoni is an interest-free loan from the *Federal Government* for *petty traders* across Nigeria, starting from *N10,000.* 
You have *6 months* to pay back your N10,000 TraderMoni loan with 2.5% admin charge. So, if you take N10,000, you will pay back only N10,250. 
If you pay your first #10,000 within 6months, you will qualify to borrow #15,000.
After repayment of #15000 within 6 months, you will qualify to borrow #20,000.
After repayment of #20,000 within 6 months, you will qualify to borrow #25000.

_Reply *#* to return to Main Menu_"""

        return self.send_message(msg)
    
    def how_to_register(self):
        msg = """Kindly locate a Tradermoni agent close to you in order to capture your biodata and biometrics (information). They will require information on what and where you sell etc.
*Note*: Tradermoni registration is FREE.

_Reply *#* to return to Main Menu_"""

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

        msg = """*What would you like to do?* 

1. Loan Status
2. Date of loan disbursement
3. Check how much you are owing
#. Return To Main Menu

_To make a selection, reply with the number ONLY of your option._
        """
        return self.send_message(msg)
    
    def respond(self):
        menus = ['1', '2', '3']
        if self.message not in menus:
            return self.unknown_response()
        
        sub_menus = dict([ ('1', self.check_loan_status), ('2', self.check_date_disbursed),('3', self.check_amount_owed) ])
        return sub_menus[ self.message ]()

    

    def check_loan_status(self):
        self.redis.hset(self.userid, 'sub_menu','loan_status_check')

        status = GeepNerve(self.reg_sender, 'Tradermoni')
        status = status.check_loan_status()
        if not status:

            UnknownNumber(self.reg_sender, 'init', 'loan_status', self.message) 
            return 

        if status[0] == 'LoanDisbursedSuccessfully':
            msg = 'Your loan has been disbursed successfully'
        elif status[0] in ['PendingApproval', 'PendingCustomerConfirmation', 'PendingFIreConfirmation', 'PendingICUConfirmation']:
            msg = "Your loan application is being processed"
        elif status[0] == 'DueForDisbursement':
            msg = 'Your loan application is due for disbursement'
        else:
            msg = "Your loan application was unsuccessful"

        msg = msg + "\n\n_Reply *#* to return to Main Menu_"

        return self.send_message(msg)

    def check_amount_owed(self):
        self.redis.hset(self.userid, 'sub_menu','loan_status_amount_owed2')
        amount_owed = GeepNerve(self.reg_sender, 'Tradermoni')
        amount_owed = amount_owed.check_amount_owed()

        if not amount_owed: 
            UnknownNumber(self.reg_sender, 'init', 'loan_status', self.message) 
            return
        
        msg = """Your are owing *₦{:,}*

_Reply *#* to return to Main Menu_""".format(amount_owed[0])

        return self.send_message(msg)

    def check_date_disbursed(self, parameter_list):
        date_disbursed = GeepNerve(self.reg_sender, 'Tradermoni')
        date_disbursed = date_disbursed.check_date_disbursed

        if not date_disbursed:
            UnknownNumber(self.reg_sender, 'init', 'loan_status', self.message)
            return
        
        msg = "coming soon..."
        return self.send_message(msg)


class RepayOptions(WhatsBot):
    def __init__(self, sender, message):
        super().__init__(sender, message)
        # self.redis.hset(self.userid, 'menu','repay_options')
        if self.message == 'init':
            self.greet()

    
    def greet(self):
        msg="""*•* Using Tradermoni scratch card from any Tradermoni one-card agent around you.

*•* Kindly visit any Bank using Interswitch Paydirect for BOI Marketmoni/Tradermoni. You will be asked to provide the phone number you registered with as the reference code.

_Reply *#* to return to Main Menu_"""

        return self.send_message(msg)


class NextLoan(WhatsBot):
    def __init__(self, sender, message):
        super().__init__(sender, message)
        # self.redis.hset(self.userid, 'menu','')
        if self.message == 'init':
            self.greet()

    def greet(self):
        msg= "Once your payment has been completed and validated on the system, you will be sent an upgrade message for the second level of loan."
        msg += "\n\n_Reply *#* to return to Main Menu_"

        return self.send_message(msg)

class Logout(WhatsBot):
    def __init__(self, sender, message):
        super().__init__(sender, message)
        super().logout()





