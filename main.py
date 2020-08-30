from flask import Flask, request
from urllib.parse import quote_plus
# https://flask-restful.readthedocs.io/en/latest/quickstart.html
from flask_restful import Resource, Api
# from whatsbot import WhatsBot
import redis
import requests
from importlib import import_module
from nerve import GeepNerve
app = Flask(__name__)
api = Api(app)


class HelloWorld(Resource):
    def post(self):

        content = request.json
        GeepNerve('','').save_request(str(content))

        if not content:
            return {"status":"Invalid Request"}

        if content['type'] == 'message' and content['app'] == 'GEEPNG':
            sender = content['payload']['sender']['phone']
            message = content['payload']['payload']['text'].strip()

            # language_selected = self.get_language(sender)
            language_selected = 'English'

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
                    message = '#'
                else:
                    prod = self.set_product(sender, message)
                    if prod in ['Tradermoni', 'Marketmoni']:
                        WhatsBot = import_module('English.{}'.format(prod)).WhatsBot
                        message = '#' #switch to Main menu
                    else:
                        return

            elif language_selected == 'Yoruba':
                pass
            elif language_selected == 'Hausa':
                pass
            else:
                return self.set_language(sender, message)


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
        msg += "2. Yoruba\n"
        msg += "3. Hausa\n"

        if not lang:
            connection.hset("user:{}".format(sender), 'lang', 'none')
            return self.send_message(sender, msg)

        if message not in ['1','2','3']:
            connection.hdel("user:{}".format(sender), 'lang')
            return self.send_message(sender, msg)
        
        # Set language to selected number
        languages = dict([('1', 'English'), ('2', 'Yoruba'), ('3', 'Hausa') ])
        connection.hset("user:{}".format(sender), 'lang', languages[message])
        
        # Next step after setting langiage will always be to set product
        return self.set_product(sender, message)

    def get_product(self, sender):
        connection = redis.Redis(decode_responses=True)
        product = connection.hget("user:{}".format(sender), 'product')

        return product
    
    def set_product(self, sender, message):
        connection = redis.Redis(decode_responses=True)
        product = connection.hget("user:{}".format(sender), 'product')
        msg = "Welcome to *GEEP* \n\n"
        msg += "What product would you like to choose? \n"
        msg += "1.	Tradermoni \n"
        msg += "2.	Marketmoni \n"
        msg += "\n_To make a selection, reply with the number *ONLY* of your option._"

        if not product:
            connection.hset("user:{}".format(sender), 'product', 'none')
            return self.send_message(sender, msg)
        
        if message not in ['1', '2']:
            connection.hdel("user:{}".format(sender), 'product')
            return self.send_message(sender, message)

        #Set Product to selected number
        products = {'1': 'Tradermoni', '2': 'Marketmoni'}
        connection.hset("user:{}".format(sender), 'product', products[message])
        self.complete = True
        return products[message]

    def setup(self ,sender, message, language_selected='English'):
        pass
        
        
    def send_message(self, sender, message):
        url = "https://api.gupshup.io/sm/api/v1/msg"
        source = '917834811114'
        msg = quote_plus(message)
        destination=sender
        app_name = 'GEEPNG'
        payload = 'source={}&channel=whatsapp&destination={}&src.name={}&message={}'. \
        format(source, destination, app_name, msg)
        headers = {
        'apikey': 'a549c98c3076406cc051e51a751fc96c',
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