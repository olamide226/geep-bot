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

            msg = """*Barka da zuwa BOI-GEEP*\n
*Mene ne kake son dubawa?* 

1. Bayanai
2. Duba matsayin bashin ka 
3. Yanda za’a biya bashi
4. Neman bashi na gaba 
5. Magana da wakili 
6. Fita daga tattaunawa

_Don yin zabi, *danna lamba kadai* akan abinda kake so._

*Misali:* zaba lamba ta daya don samun bayanai
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

        msg = "Mun gode da amfani da wannan hanyar don tattaunawa da mu."
        msg += "\nDomin karin bayani, a duba adireshin yanar gizon mu www.geep.ng ko a kira 07006275386."
        msg += "\nDomin farawa a danna *0*"
        return self.send_message(msg)
    
    def unknown_response(self, args='', args2=''):
        if self.welcome(): return 'OK'

        return self.send_message("Ayi ƙoƙari a sa amsa dai dai")
    
    
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

        msg = """{}*Don Allah ka tabbatar da lambar da kayi rijista da shi*

1. {} Itace lambar da nayi rijista da shi
2. Shiga lambar da nayi rijista da it 

_Don yin zabi, *danna lamba kadai* akan abinda kake so._ """.format( type, self.reg_sender)

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
        msg = "Yi haƙuri, lambar wayar ka be cikin ma'ajiyar mu.\n\n_Danna *0* domin komawa shafin tsare-tsare_"

        return self.send_message(msg)

    def get_new_number(self):
        msg = "Don Allah kasa lambar waya ta tsarin *08012345678*"

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

        msg = """ *Me kake son sani?* 

1. Bayani akan Farmermoni
2. Yanda za ayi rijista  

Danna 0 domin komawa shafin tsaretsare

Don yin zabi, *danna lamba kadai* akan abinda kake so.
"""
        return self.send_message(msg)
    
    def respond(self):
        menus = ['1', '2','*']
        if self.message not in menus:
            return self.unknown_response()
        
        sub_menus = dict([('1', self.about), ('2', self.how_to_register), ('*', self.greet) ])
        return sub_menus[ self.message ]()

    def about(self):
        msg = """• FarmerMoni bashi ne mara riba wanda gwamnatin tarayyan najeriya take bama kananan/masakaitan manoma a fadin kasar najeriya
• Bashin ya kama daga *₦300,000 - ₦1,000,000*.
• Lokacin biya cikin *wata 9* ne
• 7.5 % ne kudin aiki akan bashin
• Misali, idan aka am ₦3000,000, za’a biya ₦322,500. 
• Bayan an gama biyan ₦322,500 cikin watanni 9, zaka samu cancantar samun bashin ₦1,000,000..

Danna 0 domin komawa shafin tsaretsare

Danna * domin komawa shafin baya
"""

        return self.send_message(msg)
    
    def how_to_register(self):
        msg = """➣ Akwai bukatan kana cikin kungiyar yan kasuwa/masu aikin hannu wanda aka ma rijista da gwamnati.
➣ Ayi rijista ta hannun shugabannin kungiyar ka ta hanyar
    • Bukatar wakilin GEEP ya zo yayi ma kungiyar ku rijista
    • Rijista ta www.apply.marketmoney.com.ng. Ka/ki cika takardar rijista se ka/ki tura.

*A sani*: Rijista *kyauta ne*, kar ka biya ko sisi zuwa ga wani akan ko menene!

Danna 0 domin komawa shafin tsaretsare

Danna * domin komawa shafin baya
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



            msg = """matsayin bashin ka/ki shine *{}*
*Takaitancen bayani akai*
Yawan bashi: {}
Kudin da ya kamata an riga an biya: {}
Kudin da aka biya: {}
Kudin da ya rage za’a biya: {}
Ranar da aka baka kudi: {}

Danna 0 domin komawa shafin tsaretsare
""".format( status[0], loan_amount, amount_due, amount_paid, amount_default, date_disbursed)
        else:
            msg = "Matsayin bashin ka shine *{}*".format(status[0])
            msg += "\n\nDanna 0 domin komawa shafin tsaretsare"

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
            msg = 'Your loan has been disbursed successfully'
        elif status[0] in ['PendingApproval', 'PendingCustomerConfirmation', 'PendingFIreConfirmation', 'PendingICUConfirmation']:
            msg = "Your loan application is being processed"
        elif status[0] == 'DueForDisbursement':
            msg = 'Your loan application is due for disbursement'
        else:
            msg = "Your loan application was unsuccessful"

        msg = msg + "\n\n_Reply *0* to return to Main Menu_"

        return self.send_message(msg)


class RepayOptions(WhatsBot):
    def __init__(self, sender, message):
        super().__init__(sender, message)
        # self.redis.hset(self.userid, 'menu','repay_options')
        if self.message == 'init':
            self.greet()

    
    def greet(self):
        msg="""
*➣*     *Biyan bashin a banki:*
 
• Kaje ko wani banki.

• Ka cika takardar biyan kudi.

• A fadawa me amsan kudi a banki cewa
   kana son biyan bashin BOI-GEEP
   MarketMoni akan tsarin PAYDIRECT.

• A bawa me amsan kudi a banki LAMBAR
   WAYAN DA AKA YI DA SHI AMFANI
   LOKACIN DA AKAYI RIJISTAN bashin
   Farmermoni.

• Amsa takardar shedan an biya kudin.

*➣*     *BIYAN BASHI TA TSARIN AMFANI DA KATIN*
A siya katin MarketMoni daga wakilin OneCard a kusa da kai, a duba bayani akan yanda ake biyan bashin akan katin.

Danna 0 domin komawa shafin tsaretsare

Don yin zabi, danna *lamba daya kadai* akan abinda kake so.

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
                msg = "Mun samu bukatun ka/ki. \n. Za muyi aiki akan bashin ka/ki kuma bayan hakan, za’a biya ka kudin a cikin asusun ka."
                msg += "\n\nDanna 0 domin komawa shafin tsaretsare"
            else:
                msg = "Ka/ki na da sauran bashin da za ka/ki biya {}. Ayi kokari a biya sauran bashin kafin bukata bashi na gaba".format(amount_owed)
                msg += "\n\nDanna 0 domin komawa shafin tsaretsare"
        else:
            msg = "Matsayin bashin ka shine *{}*".format(status[0])
            msg += "\n\nDanna 0 domin komawa shafin tsaretsare"

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
        msg= "Kira lambar nan *0700 627 5386* domin FarmerMoni"
        msg += "\n\nDanna 0 domin komawa shafin tsaretsare"

        return self.send_message(msg)


class Logout(WhatsBot):
    def __init__(self, sender, message):
        super().__init__(sender, message)
        super().logout()





