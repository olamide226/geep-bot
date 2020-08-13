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

class WhatsBot():
    
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
    
    def respond(self):
        return {
        # 'default': self.greet,
        'main': self.main_menu,
        'enquiry': Enquiry,

        }.get(self.current_menu, self.greet)

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

        response = requests.request("POST", url, headers=headers, data = payload)

        return (response.text.encode('utf8'))
    
    def greet(self, args='', args2=''):
        """ args and args2 are just placeholders to give support to underlying Class args """
        #Check For A Greeting to activate interactive bot
        if re.search('(hello|holla|hey|how|hi|yo|what|good)', self.message):

            #SET current menu to main menu for the current user
            self.redis.hset(self.userid, 'menu','main')

            msg = """*Welcome to GEEP*\n
*WHAT WOULD YOU LIKE TO DO* 

1. Enquiry
2. Check your Loan status
3. Repayment Options
4. Request For Next Loan
5. Logout
_To make a selection, reply with the number *ONLY* of your option._\n
*EXAMPLE:* Reply with *1* to check Loan Status
            """

            return self.send_message(msg) #end whatsapp message
        else:
            return self.unknown_response()

    def main_menu(self, args='', args2=''):
        """ globals()['classname-or-functionname']( args )  """
        menus = ['1', '2', '3', '4', '5']
        if self.message not in menus:
            return self.unknown_response()

        menus = dict([('1', 'Enquiry'), ('2', 'LoanStatus'), ('3', 'RepayOptions'),
                ('4', 'NextLoan'), ('5', 'Logout')])

        return globals()[ menus[ self.message ] ]( self.sender, self.message ) 
        
    def logout(self):
        """ This function destroys session data """
        self.redis.unlink(self.userid)
        return self.send_message("Thank you for your time  👏")

    def unknown_response(self, args='', args2=''):
        return self.send_message("Kindly enter a valid response")
        ##End of WhatsBot Class##


class Enquiry(WhatsBot):
    def __init__(self, sender, message):
        super().__init__(sender, message)
        self.redis.hset(self.userid, 'menu','enquiry')
        if self.redis.hget(self.userid, 'sub_menu'):
            self.respond()
        else:
            self.greet()
    
    def __str__(self):
        return 'OK'


    def greet(self):
        self.redis.hset(self.userid, 'sub_menu','main')
        msg = """ *WHAT WOULD YOU LIKE TO DO* 

1. Request For Loan
2. Loan Terms and Conditions
3. Call The Customer Care 

_To make a selection, reply with the number *ONLY* of your option._

Say Hello to return to Main Menu
"""
        return self.send_message(msg)
    
    def respond(self):
        menus = ['1', '2', '3']
        if self.message not in menus:
            return super().greet()
        
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

Say *Hello* to return to Main Menu """

        return self.send_message(msg)

    def call_support(self):
        msg = """The Number to call is *0700 1000 2000* for TraderMoni OR *0700 627 5386* for MarketMoni"""

        return self.send_message(msg)
        

class LoanStatus(WhatsBot):
    def __init__(self, sender, message):
        super().__init__(sender, message)
        self.redis.hset(self.userid, 'menu','main')


class RepayOptions(WhatsBot):
    def __init__(self, sender, message):
        super().__init__(sender, message)
        self.redis.hset(self.userid, 'menu','main')


class NextLoan(WhatsBot):
    def __init__(self, sender, message):
        super().__init__(sender, message)
        self.redis.hset(self.userid, 'menu','main')


class Logout(WhatsBot):
    def __init__(self, sender, message):
        super().__init__(sender, message)
        super().logout()





