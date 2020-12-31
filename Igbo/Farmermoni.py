#####!/usr/bin/env python3
"""
Farmermoni.py

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

            msg = """*Nnoo na BOI-GEEP*\n
*Gini kai choro ime?* 

1. Maka ime nchoputa
2. Maka imara onudu ego mbinye gi
3. Maka etu iga esi kwugachi ego gi
4. Icho inweta ego nkwalite
5. Ichoro ka gi na onye Agent kwuo
6. Maka ipu

_Maka ihoro akara obula, pia *number no* na nke ichoro._

*Igi maa atu:* pia otu maka ime nchoputa
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

        msg = "Imela maka iji usoro a rute anyi."
        msg += "\nMaka imara ozi ndi ozo bia na akara nwa uzuzo anyi bu www.geep.ng ma obu ipoo anyi na 070010002000."
        msg += "\nMaka ibido pia efu"
        return self.send_message(msg)
    
    def unknown_response(self, args='', args2=''):
        if self.welcome(): return 'OK'

        return self.send_message("Biko tinye ihe kwesiri ekwesi")
    
    
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

        msg = """{}*Biko choputa ma obukwa akara ekwenti ijiri debanye aha*

1. {} Obu akara ekwenti m jiri debanye aha
2. Tinye akara ekwenti m jiri debanye aha

_Maka ihoro akara obula, pia number no na nke ichoro._ """.format( type, self.reg_sender)

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
        msg = " Ewela Iwe, akara ekwenti ijiri debanye aha anaghi egosi n'akwukwo anyi.\n\n_pia efu maka ilagachi azu n'ebe ibidoro_"

        return self.send_message(msg)

    def get_new_number(self):
        msg = "Biko tinye akara ekwenti gi etu esi tuziere gi aka *08012345678*"

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

        msg = """ *Gini ka iga acho imata?* 

1. Imara maka Farmermoni
2. Imara etu iga esi debanye aha
0. Maka ilagachi azu

Maka ime nhoro, jiri akara nke ichoro zagachi. 
"""
        return self.send_message(msg)
    
    def respond(self):
        menus = ['1', '2','*']
        if self.message not in menus:
            return self.unknown_response()
        
        sub_menus = dict([('1', self.about), ('2', self.how_to_register), ('*', self.greet) ])
        return sub_menus[ self.message ]()

    def about(self):
        msg = """• Farmermoni bu ego mbinye na nweghi omurunwa Government Nigeria na-enye ndi na azu  ahia na ndi nwere obere ulo oru na gwurugwuru ala anyi.
• Ego mbinye a sitere na *₦300,000 - ₦1,000,000*.
• Oge eji akwugachi ego a bu onwa isii.
• Ego nhazi bu 7.5%.
• Iji maa atu, oburu na inata ₦300,000, iga akwugachi ₦322,500. 
• Mgbe ikwugachiri 300,000 na onwa isii, iga etozu oke inata ₦1,000,000. 

Pia efu maka ilagachi ebe ibidoro

Pia * maka ilagachi azu ebe ino mbu
"""

        return self.send_message(msg)
    
    def how_to_register(self):
        msg = """➣ Iga aburiri onye debanyere aha na otu ndi na azu ahia ma obu otu ndi oru aka.
➣ Iga esi na aka ndi isi otu unu debanye aha, site na
    • Irio ka onye agent GEEP bia debanye aha ndi otu unu
    • Iga na onya nwa izizo anyi bu www.apply.marketmoney.com.ng. debanye ihe nile kwesiri ka idenye ma zigachikwara anyi ya na akaka onya nwa izizo anyi.

*Marakwa*: Anaghi eji ego edebanye aha

Pia efu maka ilagachi ebe ibidoro

Pia * maka ilagachi azu ebe ino mbu
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
        status = GeepNerve(self.reg_sender, 'Farmermoni')
        status = status.check_loan_status()
        if not status:
            unknown = UnknownNumber
            unknown(self.sender, 'init', 'loan_status', self.message) 
            return
        if status[0].lower() in ('disbursed', 'cashedout'):
            customer = GeepNerve(self.reg_sender, 'Farmermoni')
            loan_details = customer.check_loan_details()
            loan_amount = '{:,}'.format(loan_details[0])
            amount_due = '{:,}'.format(loan_details[1])
            amount_paid = '{:,}'.format(loan_details[2])
            amount_default = '{:,}'.format(loan_details[3])
            # Show date disbursed only when cashout date is empty
            date_disbursed = loan_details[4].strftime("%d-%b-%Y") if loan_details[5] == None else loan_details[5].strftime("%d-%b-%Y")



            msg = """Onodu ego mbinye gi bu *{}*
*Nchikota Account*
Ego inara: {}
Ego ikwesiri ikwu: {}
Ego ikwurula: {}
Ego foduru: {}
Ubochi Ekwesiri ikwu gi ugwo: {}

Pia efu maka ilagachi azu na ebe ibidoro
""".format( status[0], loan_amount, amount_due, amount_paid, amount_default, date_disbursed)
        else:
            msg = "Onudu ego mbinye gi bu *{}*".format(status[0])
            msg += "\n\nPia efu maka ilagachi azu na ebe ibidoro"

        return self.send_message(msg)
    
    # def respond(self):
    #     menus = ['']
    #     if self.message not in menus:
    #         return self.unknown_response()
        
    #     sub_menus = dict([ ('1', self.check_loan_status) ])
    #     return sub_menus[ self.message ]()

    

    def check_loan_status(self):
        self.redis.hset(self.userid, 'sub_menu','loan_status_check')

        status = GeepNerve(self.reg_sender, 'Farmermoni')
        status = status.check_loan_status()
        if not status:
            unknown = UnknownNumber
            unknown(self.sender, 'init', 'loan_status', self.message) 
            return

        if status[0] == 'LoanDisbursedSuccessfully':
            msg = 'Akwunyerela gi ego mbinye gi'
        elif status[0] in ['PendingApproval', 'PendingCustomerConfirmation', 'PendingFIreConfirmation', 'PendingICUConfirmation']:
            msg = "Akana ahazi ego mbinye idebanye aha gi"
        elif status[0] == 'DueForDisbursement':
            msg = 'Ego mbinye idenyere aha gi eruola mgbe aga akwunyere gi ya'
        else:
            msg = "Ego mbinye idebanyere aha gi agaghi nke oma"

        msg = msg + "\n\n_Pia efu maka ilagachi azu na ebe ibidoro_"


        return self.send_message(msg)


class RepayOptions(WhatsBot):
    def __init__(self, sender, message):
        super().__init__(sender, message)
        # self.redis.hset(self.userid, 'menu','repay_options')
        if self.message == 'init':
            self.greet()

    
    def greet(self):
        msg="""
*➣*     *MAKA IJI BANK AKWUGACHI UGWO:*
 
• Gaa na Bank obula.

• Denye aha na akwukwo eji akwunye ego.

• Gwa onye ana akwu ego na ichoro 
   iji PAYDIRECT kwuo ugwo
   BOI-GEEP Farmermoni.

• Nye onye okwu ugwo AKARA
   EKWE NTI ijiri debanye aha 
   na ego mbinye Farmermoni.

• Nara akwukwo na egosi na ikwuru ugwo.

*➣*     *IJI SCRATCH CARD AKWU UGWO*
Gaa zuta Farmermoni scratch card site na aka onye OneCard agent obula no gi nso, Lee anya ofuma na ebe atuziri aka etu iga esi akwu ugwo gi

Pia efu maka ilagachi azu na ebe ibidoro

Maka ime nhoro, jiri akara nke ichoro zagachi

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
        customer = GeepNerve(self.reg_sender, 'Farmermoni')
        status = customer.check_loan_status()
        if not status:
            unknown = UnknownNumber
            unknown(self.sender, 'init', 'loan_upgrade', self.message) 
            return
        if status[0].lower() in ('disbursed', 'cashedout'):
            amount_owed = customer.check_amount_owed()[0]
            if amount_owed == 0:
                msg = "anabatala aririo gi.\nAnyi ga ahazi ego mbinye gi ma zitere gi ego gi na account gi"
                msg += "\n\nPia efu maka ilagachi azu na ebe ibidoro"
            else:
                msg = "enwere ego ina akwubeghi {}. Jisie ike kwuo ugwo gi tupu inata ego nkwalite".format(amount_owed)
                msg += "\n\nPia efu maka ilagachi azu na ebe ibidoro"
        else:
            msg = "Onudu ego mbinye gi bu *{}*".format(status[0])
            msg += "\n\nPia efu maka ilagachi azu na ebe ibidoro"

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
        msg= "Akara ekwe nti Farmermoni bu *07006275386*"
        msg += "\n\nPia efu maka ilagachi azu na ebe ibidoro"

        return self.send_message(msg)


class Logout(WhatsBot):
    def __init__(self, sender, message):
        super().__init__(sender, message)
        super().logout()





