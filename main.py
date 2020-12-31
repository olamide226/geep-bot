from flask import Flask, request
from urllib.parse import quote_plus
# https://flask-restful.readthedocs.io/en/latest/quickstart.html
from flask_restful import Resource, Api
# from whatsbot import WhatsBot
import redis
import requests
from importlib import import_module
from nerve import GeepNerve
import os
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
api = Api(app)


class HelloWorld(Resource):
    def post(self):

        content = request.json
        GeepNerve('','').save_request(str(content))

        if not content:
            return {"status":"Invalid Request"}
        
        # Check If user just opted in and send intro message
        if content['type'] == 'user-event' and content['app'] == os.getenv("APP_NAME") and content['payload']['type'] == 'opted-in':
            sender = content['payload']['phone']
            message = 'Reply *0* to get started'
            return self.send_message(sender, message)
        # Check If user sends message and process
        if content['type'] == 'message' and content['app'] == os.getenv("APP_NAME"):
            sender = content['payload']['sender']['phone']
            message = content['payload']['payload']['text'].strip()

            # language_selected = self.get_language(sender)
            #language_selected = 'English'
            language_selected = self.get_language(sender)

            if language_selected == 'English':
                product_select = self.get_product(sender)
                if  product_select == 'Tradermoni':

                    from English.Tradermoni import WhatsBot
                    # The import_module allows to import as string
                    # WhatsBot = import_module('English.Tradermoni')
                    # WhatsBot = WhatsBot.WhatsBot
                elif product_select == 'Marketmoni':
                    # return self.send_message(sender, 'Coming soon...')
                    from English.Marketmoni import WhatsBot
                elif product_select == 'Farmermoni':
                    # return self.send_message(sender, 'Coming soon...')
                    from English.Farmermoni import WhatsBot
                else:
                    prod = self.set_product(sender, message)
                    if prod in ['Tradermoni', 'Marketmoni', 'Farmermoni']:
                        WhatsBot = import_module('English.{}'.format(prod)).WhatsBot
                        message = '0' #switch to Main menu
                    else:
                        return

            elif language_selected == 'Pidgin':
                product_select = self.get_product(sender)
                if  product_select == 'Tradermoni':

                    from Pidgin.Tradermoni import WhatsBot
                    # The import_module allows to import as string
                    # WhatsBot = import_module('English.Tradermoni')
                    # WhatsBot = WhatsBot.WhatsBot
                elif product_select == 'Marketmoni':
                    # return self.send_message(sender, 'Coming soon...')
                    from Pidgin.Marketmoni import WhatsBot
                elif product_select == 'Farmermoni':
                    # return self.send_message(sender, 'Coming soon...')
                    from Pidgin.Farmermoni import WhatsBot
                else:
                    prod = self.set_product(sender, message)
                    if prod in ['Tradermoni', 'Marketmoni', 'Farmermoni']:
                        WhatsBot = import_module('Pidgin.{}'.format(prod)).WhatsBot
                        message = '0' #switch to Main menu
                    else:
                        return

            elif language_selected == 'Igbo':
                product_select = self.get_product(sender)
                if  product_select == 'Tradermoni':

                    from Igbo.Tradermoni import WhatsBot
                    # The import_module allows to import as string
                    # WhatsBot = import_module('English.Tradermoni')
                    # WhatsBot = WhatsBot.WhatsBot
                elif product_select == 'Marketmoni':
                    # return self.send_message(sender, 'Coming soon...')
                    from Igbo.Marketmoni import WhatsBot
                elif product_select == 'Farmermoni':
                    # return self.send_message(sender, 'Coming soon...')
                    from Igbo.Farmermoni import WhatsBot
                else:
                    prod = self.set_product(sender, message)
                    if prod in ['Tradermoni', 'Marketmoni', 'Farmermoni']:
                        WhatsBot = import_module('Igbo.{}'.format(prod)).WhatsBot
                        message = '0' #switch to Main menu
                    else:
                        return


            elif language_selected == 'Yoruba':
                product_select = self.get_product(sender)
                if  product_select == 'Tradermoni':

                    from Yoruba.Tradermoni import WhatsBot
                    # The import_module allows to import as string
                    # WhatsBot = import_module('English.Tradermoni')
                    # WhatsBot = WhatsBot.WhatsBot
                elif product_select == 'Marketmoni':
                    # return self.send_message(sender, 'Coming soon...')
                    from Yoruba.Marketmoni import WhatsBot
                elif product_select == 'Farmermoni':
                    # return self.send_message(sender, 'Coming soon...')
                    from Yoruba.Farmermoni import WhatsBot
                else:
                    prod = self.set_product(sender, message)
                    if prod in ['Tradermoni', 'Marketmoni', 'Farmermoni']:
                        WhatsBot = import_module('Yoruba.{}'.format(prod)).WhatsBot
                        message = '0' #switch to Main menu
                    else:
                        return

            elif language_selected == 'Hausa':
                product_select = self.get_product(sender)
                if  product_select == 'Tradermoni':

                    from Hausa.Tradermoni import WhatsBot
                    # The import_module allows to import as string
                    # WhatsBot = import_module('English.Tradermoni')
                    # WhatsBot = WhatsBot.WhatsBot
                elif product_select == 'Marketmoni':
                    # return self.send_message(sender, 'Coming soon...')
                    from Hausa.Marketmoni import WhatsBot
                elif product_select == 'Farmermoni':
                    # return self.send_message(sender, 'Coming soon...')
                    from Hausa.Farmermoni import WhatsBot
                else:
                    prod = self.set_product(sender, message)
                    if prod in ['Tradermoni', 'Marketmoni', 'Farmermoni']:
                        WhatsBot = import_module('Hausa.{}'.format(prod)).WhatsBot
                        message = '0' #switch to Main menu
                    else:
                        return

             

            else:
                self.set_language(sender, message)
                return


            bot = WhatsBot(sender, message)

            response = bot.reply()

            response(sender, message).__str__()
            # print(dir(r))

            return
                
        # return {'hello': 'world'}

    def get_language(self, sender):
        connection = redis.Redis(decode_responses=True)
        lang = connection.hget("user:{}".format(sender), 'lang')
        return lang
    
    def set_language(self, sender, message):
        connection = redis.Redis(decode_responses=True)
        lang = connection.hget("user:{}".format(sender), 'lang')
        msg = "Please select a language\n\n"
        msg += "1. English\n"
        msg += "2. Hausa\n"
        msg += "3. Igbo\n"
        msg += "4. Pidgin\n"
        msg += "5. Yoruba\n"
        msg += "\n_To make a selection, reply with the *NUMBER ONLY* of your option._"

        if not lang:
            connection.hset("user:{}".format(sender), 'lang', 'none')
            return self.send_message(sender, msg)

        if message not in ['1','2','3','4','5']:
            connection.hdel("user:{}".format(sender), 'lang')
            return self.send_message(sender, msg)
        
        # Set language to selected number
        languages = dict([('1', 'English'), ('2', 'Hausa'), ('3', 'Igbo'), ('4', 'Pidgin'), ('5', 'Yoruba') ])
        connection.hset("user:{}".format(sender), 'lang', languages[message])
            #return self.set_hausa_product(sender, message) 
        # Next step after setting langiage will always be to set product
        return self.set_product(sender, message)

    def get_product(self, sender):
        connection = redis.Redis(decode_responses=True)
        product = connection.hget("user:{}".format(sender), 'product')

        return product

    
    def set_product(self, sender, message):
        connection = redis.Redis(decode_responses=True)
        product = connection.hget("user:{}".format(sender), 'product')
        msg = "Welcome to *BOI-GEEP* \n\n"
        msg += "What product would you like to choose? \n"
        msg += "1.	Tradermoni \n"
        msg += "2.	Marketmoni \n"
        msg += "3.	Farmermoni \n"
        msg += "\n_To make a selection, reply with the *NUMBER ONLY* of your option._"

        if not product:
            connection.hset("user:{}".format(sender), 'product', 'none')
            return self.send_message(sender, msg)
        
        if message not in ['1', '2', '3']:
            connection.hdel("user:{}".format(sender), 'product')
            return self.send_message(sender, msg)

        #Set Product to selected number
        products = {'1': 'Tradermoni', '2': 'Marketmoni', '3': 'Farmermoni'}
        connection.hset("user:{}".format(sender), 'product', products[message])
        self.complete = True
        return products[message]


    def setup(self ,sender, message, language_selected):
        pass
        
        
    def send_message(self, sender, message):
        url = "https://api.gupshup.io/sm/api/v1/msg"
        source = os.getenv("SOURCE")
        msg = quote_plus(message)
        destination=sender
        app_name = os.getenv("APP_NAME")
        payload = 'source={}&channel=whatsapp&destination={}&src.name={}&message={}'. \
        format(source, destination, app_name, msg)
        headers = {
        'apikey': os.getenv("API_KEY"),
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded'
        }
        # self.msg = msg

        response = requests.request("POST", url, headers=headers, data = payload)
        # print(msg)
        return response.json()

    

api.add_resource(HelloWorld, '/flask/api')

if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True)
