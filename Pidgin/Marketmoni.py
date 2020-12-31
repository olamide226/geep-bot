#####!/usr/bin/env python3
"""
Marketmoni.py

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
 * Version:             2.0
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
import os
from dotenv import load_dotenv
load_dotenv()
from nerve import GeepNerve
# import inspect

class WhatsBot:
    
    def __init__(self, sender, message):

        self.redis = redis.Redis(decode_responses=True)
        self.sender = sender
        self.message = message.strip().lower()
        self.userid = 'user:' + sender
        self.redis.expire(self.userid, 1800) #keep user session data for 30mins
        
        #check if user exist before else initialize
        if not self.redis.hget(self.userid, 'id'):
            self.redis.hset(self.userid, 'id', sender)
            
        
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
        'unknown_number': UnknownNumber,
        'loan_upgrade': LoanUpgrade

        }.get(self.current_menu, self.unknown_response)

    def send_message(self, msg):
        url = "https://api.gupshup.io/sm/api/v1/msg"
        source = os.getenv("SOURCE")
        msg = quote_plus(msg)
        destination=self.sender
        app_name = os.getenv("APP_NAME")
        payload = 'source={}&channel=whatsapp&destination={}&src.name={}&message={}'. \
        format(source, destination, app_name, msg)
        headers = {
        'apikey': os.getenv("API_KEY"),
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
        if self.message.lower() in ['0', 'hello', 'helo']:

            #SET current menu to main menu for the current user
            self.redis.hmset(self.userid, {'menu': 'main', 'sub_menu': ''})

            msg = """*Welcome to BOI-GEEP*\n
*Wetin you go like do* 

1. Enquiry
2. Sabi your Loan status
3. How you go take pay back the loan
4. Request For Loan Upgrade
5. Follow Agent talk
6. Logout

_Make you reply with the number wey you want._

*EXAMPLE:* Reply with *1* for Enquiry
            """

            return self.send_message(msg) #end whatsapp message
        else:
            return False

    def main_menu(self, args='', args2=''):
        """ globals()['classname-or-functionname']( args )  """

        menus = ['1', '2', '3', '4', '5', '6']
        if self.message not in menus:
            return self.unknown_response()

        menus = dict([('1', 'Enquiry'), ('2', 'LoanStatus'), ('3', 'RepayOptions'),
                ('4', 'LoanUpgrade'), ('5', 'SpeakToAgent'), ('6', 'Logout')])

        return globals()[ menus[ self.message ] ]( self.sender, 'init' ) 
        
    def logout(self):
        """ This function destroys session data """
        self.redis.unlink(self.userid)

        msg = "You do well say you use this way take reach us."
        msg += "\nfor more Ogbonge tori make you go our website www.geep.ng or call 070010002000."
        msg += "\nTo start, make you press 0"
        return self.send_message(msg)
    
    def unknown_response(self, args='', args2=''):
        if self.welcome(): return 'OK'

        return self.send_message("Abeg make you enter correct option")
    
    
        ##End of WhatsBot Class##

class UnknownNumber(WhatsBot):
    def __init__(self, sender, message, prev_menu=None, last_msg=None):
        super().__init__(sender, message)

        if self.message == 'init':
            # Set the menus if it is the first time
            print( self.redis.hmset( self.userid, 
            { 'menu': 'unknown_number', 'prev_menu': prev_menu, 'last_message': last_msg}
        ) )
            self.greet()
        else:
            self.respond()
    

    def greet(self, type=''):

        msg = """{}*Abeg, se na your phone number wey you register be this?*

1. {} Na my register phone number be this
2. Enter the phone number wey you take register

_Make you reply with the number wey you want._ """.format( type, self.reg_sender)

        return self.send_message(msg)

    def respond(self):

        if re.findall(r"\d{11}", self.message) and len(self.message) == 11:
            return self.set_new_number(self.message)

        menus = ['1', '2']
        if self.message not in menus:
            return self.unknown_response()
        
        func = dict([('1', self.not_found), ('2', self.get_new_number) ])
        return func[ self.message ]()

    def not_found(self):
        msg = "Sorry, your phone number no dey for our record. \n_make you press 0 to go back to the main menu_"

        return self.send_message(msg)

    def get_new_number(self):
        msg = "Abeg make you enter your number like this" 

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

        msg = """ *Wetin you go like know?* 

1. About Marketmoni
2. How to Register 
0. Return To Main Menu

Make you reply with the number wey you want.


"""
        return self.send_message(msg)
    
    def respond(self):
        menus = ['1', '2','*']
        if self.message not in menus:
            return self.unknown_response()
        
        sub_menus = dict([('1', self.about), ('2', self.how_to_register), ('*', self.greet) ])
        return sub_menus[ self.message ]()

    def about(self):
        msg = """• MarketMoni na loan from the Federal Government of Nigeria to help traders, Small and Medium Scale Enterprises (SMEs) for inside our country.
• Loan range na from *₦50,000 - ₦250,000*.
• Na inside 3-6 months you go take pay back the loan.
• Administration fee na *5%*.
• For example, if you take ₦50,000, you go pay back only ₦52,500 with weekly fee of *₦2,187.5*. 
• When you payback your first ₦50,000 inside 6months, you go  qualify to borrow ₦100,000. After repayment of ₦100,000 inside 6 months, you go qualify to borrow ₦250,000.

Make you Press 0 to go back to Menu

Make you press * to go back to previous menu
"""

        return self.send_message(msg)
    
    def how_to_register(self):
        msg = """➣ You must be member of any market/artisan/Trade cooperative wey dey registered.
➣ You fit register through the executives wey dey your cooperative through:
    • Our GEEP Agent make them come register your cooperative or
    • You fit register on www.apply.marketmoney.com.ng. You go fill the registration form and submit am.

*Note*: REGISTRATION dey *FREE*. Make you no not pay anybody for anything!

Make you Press 0 to go back to Menu

Make you press * to go back to previous menu
"""
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
            self.unknown_response()

    def greet(self):
        # curframe = inspect.currentframe()
        # calframe = inspect.getouterframes(curframe, 2)
        # print('LoanStatus caller name:', calframe[1][3])

        self.redis.hset(self.userid, 'sub_menu','loan_status_main')
        status = GeepNerve(self.reg_sender, 'Marketmoni')
        status = status.check_loan_status()
        if not status:
            unknown = UnknownNumber
            unknown(self.sender, 'init', 'loan_status', self.message) 
            return
        if status[0].lower() in ('disbursed', 'cashedout'):
            customer = GeepNerve(self.reg_sender, 'Marketmoni')
            loan_details = customer.check_loan_details()
            loan_amount = '{:,}'.format(loan_details[0])
            amount_due = '{:,}'.format(loan_details[1])
            amount_paid = '{:,}'.format(loan_details[2])
            amount_default = '{:,}'.format(loan_details[3])
            # Show date disbursed only when cashout date is empty
            date_disbursed = loan_details[4].strftime("%d-%b-%Y") if loan_details[5] == None else loan_details[5].strftime("%d-%b-%Y")



            msg = """Your Loan Status na  *{}*
*Account Summary*
Loan Amount: {}
Amount wey you suppose don pa: {}
Amount wey you don pay: {}
Amount wey you dey owe: {}
The day you collect the money: {}

Make you Press 0 to go back to Menu
""".format( status[0], loan_amount, amount_due, amount_paid, amount_default, date_disbursed)
        else:
            msg = "Your Loan Status na *{}*".format(status[0])
            msg += "\n\nMake you Press 0 to go back to Menu"

        return self.send_message(msg)
    
    # def respond(self):
    #     menus = ['']
    #     if self.message not in menus:
    #         return self.unknown_response()
        
    #     sub_menus = dict([ ('1', self.check_loan_status) ])
    #     return sub_menus[ self.message ]()

    

    def check_loan_status(self):
        self.redis.hset(self.userid, 'sub_menu','loan_status_check')

        status = GeepNerve(self.reg_sender, 'Marketmoni')
        status = status.check_loan_status()
        if not status:
            unknown = UnknownNumber
            unknown(self.sender, 'init', 'loan_status', self.message) 
            return

        if status[0] == 'LoanDisbursedSuccessfully':
            msg = 'Your loan don ready '
        elif status[0] in ['PendingApproval', 'PendingCustomerConfirmation', 'PendingFIreConfirmation', 'PendingICUConfirmation']:
            msg = "We still dey work on your loan"
        elif status[0] == 'DueForDisbursement':
            msg = 'Your loan go soon ready '
        else:
            msg = "We no accept your loan application"

        msg = msg + "\n\n_Make you Press *0* to go back to Menu_"

        return self.send_message(msg)


class RepayOptions(WhatsBot):
    def __init__(self, sender, message):
        super().__init__(sender, message)
        # self.redis.hset(self.userid, 'menu','repay_options')
        if self.message == 'init':
            self.greet()

    
    def greet(self):
        msg="""
*➣*     *PAYMENT THROUGH BANK:*
 
• Go ANY Bank.

• Fill Teller form.

• Tell The Bank Cashier say you want pay
   your BOI-GEEP Marketmoni
   Loan for PAYDIRECT.

• Give The Bank Cashier PHONE
   NUMBER YOU TAKE REGISTER
   your MarketMoni Loan.

• Collect your payment receipt.

*➣*     *PAYMENT THROUGH SCRATCH CARD*
Buy Marketmoni scratch card from any OneCard agent wey dey near you, check the card for guide on how you go repay your loan.

Make you Press *0* to go back to Menu

Make you reply with the number wey you want
 

"""

        return self.send_message(msg)


class LoanUpgrade(WhatsBot):
    def __init__(self, sender, message):
        super().__init__(sender, message)
        self.redis.hset(self.userid, 'menu','loan_upgrade')
        if self.message == 'init':
            self.greet()
        else:
            self.unknown_response()

    def greet(self):
        customer = GeepNerve(self.reg_sender, 'Marketmoni')
        status = customer.check_loan_status()
        if not status:
            unknown = UnknownNumber
            unknown(self.sender, 'init', 'loan_upgrade', self.message) 
            return
        if status[0].lower() in ('disbursed', 'cashedout'):
            amount_owed = customer.check_amount_owed()[0]
            if amount_owed == 0:
                msg = "We don receive your request. We go process your loan and you go get your money inside your wallet account"
                msg += "\n\nMake you Press *0* to go back to Menu"
            else:
                msg = "You dey owe  {}. Make you pay your current loan before You go fit request for Upgrade".format(amount_owed)
                msg += "\n\nPress 0 to go back to main menu"
        else:
            msg = "Your loan status na *{}*".format(status[0])
            msg += "\n\nMake you Press *0* to go back to Menu"

        return self.send_message(msg)


class SpeakToAgent(WhatsBot):
    """
    As the name suggests..The Returns the Call Centre number to Call
    """
    def __init__(self, sender, message):
        super().__init__(sender, message)
        # self.redis.hset(self.userid, 'menu','')
        if self.message == 'init':
            self.greet()

    def greet(self):
        msg= "The Number to call na *0700 627 5386* for MarketMoni"
        msg += "\n\nMake you Press *0* to go back to Menu"

        return self.send_message(msg)


class Logout(WhatsBot):
    def __init__(self, sender, message):
        super().__init__(sender, message)
        super().logout()





