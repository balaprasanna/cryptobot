from flask import Flask, request, make_response, jsonify
import requests

app = Flask(__name__)
log = app.logger


# UTIL FUNCTIONS : BEGIN

import requests

def getjson(url):
    resp =requests.get(url)
    return resp.json()

def getcoindct():
    listing_url = "https://api.coinmarketcap.com/v2/listings/"
    data = getjson(listing_url)
    coins_list_of_dict = data["data"]
    coin_dct = {}

    for coin_info_dct in coins_list_of_dict:
        key = coin_info_dct["name"].lower()
        value = coin_info_dct["id"]

        coin_dct[key] = value
    return coin_dct

def getprice(coinname, coin_dct):
    coin_id = coin_dct[coinname]
    url = f"https://api.coinmarketcap.com/v2/ticker/{coin_id}/"
    data = getjson(url)
    price = data["data"]["quotes"]["USD"]["price"]
    return price

# UTIL FUNCTIONS : ENDS

coin_dct = getcoindct()

@app.route('/', methods=['POST'])
def webhook():
   req = request.get_json(silent=True, force=True)
   intent_name = req["queryResult"]["intent"]["displayName"]

   # Braching starts here
   if intent_name == 'GetPriceIntent':
       respose_text = getPriceHanlder(req)
   else:
       respose_text = "No intent matched"
   # Branching ends here

   # Finally sending this response to Dialogflow.
   return make_response(jsonify({'fulfillmentText': respose_text}))

# UTIL FUNCTIONS STARTS HERE..

def getPriceHanlder(req):
    coinname = req.get("queryResult").get("parameters").get("coinname")

    if not coinname:
        return  "Sorry unable to find the coinname.."

    coinname = coinname.lower()
    # CAN BE CALLED AS MANY TIMES AS U WANT
    price = getprice(coinname, coin_dct)
    return f"The price of {coinname} is {price}"


if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5000)