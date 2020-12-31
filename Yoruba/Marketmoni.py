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

            msg = """*Káàbọ̀ sí BOI- GEEP*\n
*Kíni o nífẹ̀ẹ́ sí láti ṣe?* 

1. Ìbéèrè
2. Ṣe àyẹ̀wò ipò 
3. Bí o ṣe lè dá owó padà
4. Bèèrè fún àfikún
5. Bá aṣojú sọ̀rọ̀
6. Jáde

_Láti ṣe àsàyàn , dáhùn pẹ̀lú nọ́mbà tí o fẹ́._

*Fún àpẹẹrẹ:* Dáhùn pẹ̀lú óókan (1) láti ṣe ìbéérè  
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

        msg = "Eṣé tí ẹ lo ìlànà yí láti kàn sí wa."
        msg += "\nFún ẹ̀kúnrẹ́rẹ́ àlàyé, ẹ jọ̀wọ́ ẹ kàn sí èrọ ayélujára www.geep.ng tàbí pé 070010002000."
        msg += "\nláti bèrè, te *0*"
        return self.send_message(msg)
    
    def unknown_response(self, args='', args2=''):
        if self.welcome(): return 'OK'

        return self.send_message("Jọ̀wọ́ fi ìdáhùn tó péye sí lẹ̀")
    
    
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

        msg = """{}*Jọ̀wọ́ ṣàyẹ̀wò nọ́mbà rẹ tí o fi sílẹ̀*

1. {} N jé mo ti se ìforúkọ sílè nọ́mbà mi
2. Tẹ nọ́mbà rẹ

_Láti ṣe àṣàyàn, dáhùn pẹ̀lú nọ́mbà  tí o fẹ́_ """.format( type, self.reg_sender)

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
        msg = "Má bìnu a kòrí nómbà yìí nínú àkosílè wa, \n_tẹ òdo (0) láti padà sí àsàyàn wa_"

        return self.send_message(msg)

    def get_new_number(self):
        msg = "Jọ̀wọ́ tẹ nọ́mbà rẹ gẹ́gẹ́bí ìlànà yìí *08012345678*" 

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

        msg = """ *Kíni  o fẹ́ láti mọ̀?* 

1. Nípa Marketmoni
2. Láti ṣe ìforúkọ sílẹ̀ 
0. Padà

Láti ṣe àsàyàn, dáhùn pẹ̀lú nọ́mbà tí o fẹ́.

"""
        return self.send_message(msg)
    
    def respond(self):
        menus = ['1', '2','*']
        if self.message not in menus:
            return self.unknown_response()
        
        sub_menus = dict([('1', self.about), ('2', self.how_to_register), ('*', self.greet) ])
        return sub_menus[ self.message ]()

    def about(self):
        msg = """• Marketmoni jẹ lóònù tí kò ní èle láti ọ̀dọ̀ ìjọba àpapọ̀ orílẹ̀ èdè Nàìj́iríà fún àwọn oníṣòwò, olùtajà àti àwọn tí ó ní ilé iṣé kékèké káàkiri ìlú.
• Loan range from *₦50,000 - ₦250,000*.
• Lóònù náà wà láti N50, 000 - N250, 000.
• Owó ìṣàkóso jẹ́ 5%.
• Fún àpẹẹrẹ, tí o bá gbà ₦50,000, wàá san ₦52,500 padà pẹ̀lú ìṣirò *₦2,187.5* lọ́sọ̀sẹ̀. 
• Lẹ́yìn tí o bá san ₦50,000 tí o kókó gbà láàrín oṣù mẹ́fà, o ní àǹfàní láti yá ₦100,000. nígbànáà lo le tẹ̀síwájú sí ₦250,000.

Tẹ 0 láti padà sí àṣànyà

Tẹ * láti padà sẹ́yìn
"""

        return self.send_message(msg)
    
    def how_to_register(self):
        msg = """➣  O Gbọdọ jẹ́ ará ọjà/onísòwò/ẹgbẹ́ àwọn ọlọ́jà tí ó ti ṣe ìforúkọsílẹ̀ lábẹ́ Ìjọba..
➣ Ṣe ìforúkọsílẹ̀ lábẹ́ ẹgbẹ́ àwọn ọlọ́jà rẹ
    • Bèèrè fún aṣojú GEEP láti wá fi orúkọ egbé yín sílẹ̀
    • Ṣe ìforúkọ sílẹ lórí www.apply.marketmoney.com.ng. Dáhun àwọn ìbéèrè lórí fóòmu náà kí o fi ránṣẹ́.

*Mo wípé:* Ọ̀fé ní ìforúkosílẹ. Máṣe fún enikẹ́ni ní owó fún ìforúkọsílè.

Tẹ 0 láti padà sí àṣànyà

Tẹ * láti padà sẹ́yìn
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



            msg = """Lóònù rẹ jẹ́ *{}*
*Àkọ́lé lápaapọ̀*
Iye lóònù: {}
Iye tó ye kó o san: {}
Iye tí o ti san: {}
Iye tó kù láti san: {}
Ìsanwó (ìgbowó jáde) déètì: {}

Tẹ ódo láti padá sí àsàyàn
""".format( status[0], loan_amount, amount_due, amount_paid, amount_default, date_disbursed)
        else:
            msg = "Lóònù rẹ jẹ́ *{}*".format(status[0])
            msg += "\n\nTẹ ódo láti padá sí àsàyàn"
 
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
            msg = 'Ati san lóònù rẹ'
        elif status[0] in ['PendingApproval', 'PendingCustomerConfirmation', 'PendingFIreConfirmation', 'PendingICUConfirmation']:
            msg = "Ìbẹ̀wẹ̀ lóònù rẹ ti ń ní ìlosíwájú"
        elif status[0] == 'DueForDisbursement':
            msg = 'Ó ti tó àsìkò láti san lóònu rẹ'
        else:
            msg = "O kò yege nínú Ìbẹ̀wẹ̀ lóònù rẹ"

        msg = msg + "\n\n_Tẹ ódo láti padá sí àsàyàn_" 

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
 
• Lo sí èyíkèyí ilé ìfowópamó.

• Dáhùn àwon ìbéérè orí ìwé pélébé ní ilé ìfowópamó

• So fún òsìsé ilé ìfowópamó 
   pé o fẹ́ san lóònù BOI-GEEP 
   MarketMoni lórí PAYDIRECT.

• Fún òṣìṣé ilé ìfowópamó 
   ní nọ́mbà fóònù tí o fi ṣe 
   ìforúkosílẹ fún lóónù Marketmoni.

• Gba ìwé ẹ̀rí ìfowópawó.

*➣*     *PAYMENT THROUGH SCRATCH CARD*
Ra káàdì Marketmoni láti ọwọ́ èyíkèyí aṣojú Onecard ní agbègbè rẹ, wo ara káàdì na fún ìlànà nípa sísan lóònù rẹ.

Tẹ òòdo (0) láti padà sí àsàyàn

Láti ṣe àsàyàn, dáhùn pẹ̀lú nọ́mbà tí ó fẹ́

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
                msg = "Tí ó bá jẹ́ bẹ̀, dáhùn pẹ̀lú ati gba ìbéère rẹ. \nA máa ṣisẹ́ lórí lóònù rẹ, o ó sì gba owó nàá sínú àpò owó rẹ."
                msg += "\n\nTẹ òòdo (0) láti padà sí àsàyàn"
            else:
                msg = "dáhùn pẹ̀lú Ó ní iye lóònù báyi  {}. Jọ̀wọ́ san owó tí ó kù, kí o tó lẹ́tọ làti gba èyí tí ó kàn.".format(amount_owed)
                msg += "\n\nTẹ òòdo (0) láti padà sí àsàyàn"
        else:
            msg = "Your loan status is *{}*".format(status[0])
            msg += "\n\nTẹ òòdo (0) láti padà sí àsàyàn"

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
        msg= " Nọ́mbà láti pè ni *0700 1000 200* fun MarketMoni"
        msg += "\n\nTẹ òòdo (0) láti padà sí àsàyàn"

        return self.send_message(msg)


class Logout(WhatsBot):
    def __init__(self, sender, message):
        super().__init__(sender, message)
        super().logout()





