from flask import Flask, request, jsonify
# https://flask-restful.readthedocs.io/en/latest/quickstart.html
from flask_restful import Resource, Api
from whatsbot import WhatsBot

app = Flask(__name__)
api = Api(app)

@app.route('/api', methods=['GET', 'POST'])
def main():
    if request.method != 'POST':
        return jsonify({"status":"Invalid Method"}), 405

    content = request.json

    if not content:
        return jsonify({"status":"Invalid Request"})
    # print content['mytext']
    if content['type'] == 'message' and content['app'] == 'GEEPNG':
        sender = content['payload']['sender']['phone']
        message = content['payload']['payload']['text']
        bot = WhatsBot(sender, message)
        response = bot.reply()
        try:
            return jsonify(response(sender, message))
        except TypeError:
            return response(sender, message).__str__()
    else:
        return jsonify({"status":"Invalid Request"})

class HelloWorld(Resource):
    def post(self):
        print("starting")
        content = request.json

        if not content:
            return {"status":"Invalid Request"}
        # print content['mytext']
        if content['type'] == 'message' and content['app'] == 'GEEPNG':
            sender = content['payload']['sender']['phone']
            message = content['payload']['payload']['text']
            bot = WhatsBot(sender, message)
            print("Reply gotten")
            response = bot.reply()
            
            try:
                r =response(sender, message).__str__()
                # print(dir(r))
                print(r)
                # print("Try Block")
                return
            except :
                # print(response(sender, message).__dict__())
                # print("Except block")
                return "error occured"
                
        # return {'hello': 'world'}

api.add_resource(HelloWorld, '/flask/api')

if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True)