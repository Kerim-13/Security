from Crypto.PublicKey import RSA
from Crypto.Hash import MD5
from datetime import datetime
import jwt
import json
import time
import requests

def get_jwt_token(payload_hash):
    jwt_file = {
        "tha":payload_hash,
        "iat":int(time.time()),
        "exp":int(time.time()) + 3600
    }

    own_private_key = open('private_key.pem', "rb").read()
    jwt_token = jwt.encode(jwt_file, own_private_key, algorithm="RS256")

    return jwt_token

def get_md5_hash(data):
    md5 = MD5.new()
    md5.update(data.encode())

    return md5.hexdigest()

def send_transaction(source, target, amount, config):

    if amount < config["tx_lower_limit"] or amount > config["tx_upper_limit"]:
        print("amount exceeds transaction limit.")
        return -1

    payload_json = {
        "source":source,
        "target":target,
        "amount":amount,
        "timestamp":datetime.now().isoformat()
    }

    payload_str = json.dumps(payload_json).replace(" ", "")
    payload_hash = get_md5_hash(payload_str)
    jwt_token = get_jwt_token(payload_hash)


    headers = {
        'Authorization': 'Bearer ' + jwt_token.decode("utf-8"),
        'Content-Type': 'application/json'
    }

    response = requests.post(
        "https://gradecoin.xyz/transaction", headers=headers, json=payload_json)
    print(response.text)
    
    return 0

def get_transaction():
    response = requests.get("https://gradecoin.xyz/transaction")
    print_transactions(response.json())
    return 0

def print_transactions(response_json):
    for transaction in response_json:
        print("Transaction_id: ", transaction)
        print("source: ", response_json[transaction]['source'])
        print("target: ",response_json[transaction]['target'])
        print("amount: ",response_json[transaction]['amount'])
        print("timestamp: ",response_json[transaction]['timestamp'])
        print()

def main():
    f = open("student_data.json")
    data = json.load(f)
    fingerprint = data["fingerprint"]
    config = requests.get("https://gradecoin.xyz/config").json()
    
    get_transaction()
    
    temp_target = "4319647f2ad81e83bf602692b32a082a6120c070b6fd4a1dbc589f16d37cbe1d"
    source = fingerprint
    send_transaction(source, temp_target, 1, config)
    
if __name__ == "__main__":
    main()