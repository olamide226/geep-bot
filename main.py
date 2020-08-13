from flask import Flask, request, jsonify
from WhatsBot.WhatsBot import WhatsBot
app = Flask(__name__)

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
        response = bot.respond()
        return str( response(sender, message) )
    else:
        return jsonify({"status":"Invalid Request"})


if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True)