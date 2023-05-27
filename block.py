from Crypto.PublicKey import RSA
from hashlib import blake2s
from datetime import datetime
from random import randint
import time
import jwt
import binascii
import json
import base64
import os
import requests

def get_jwt_token(payload_hash):
    jwt_file = {
        "tha":payload_hash,
        "iat":int(time.time()),
        "exp":int(time.time()) + 3600
    }

    own_private_key = open('private_key.pem', "rb").read()
    own_public_key = open('public_key.pem', "rb").read()
    jwt_token = jwt.encode(jwt_file, own_private_key, algorithm="RS256")

    print(jwt.decode(jwt_token, own_public_key, algorithms="RS256"))
    
    return jwt_token

def main():
    f = open("student_data.json")
    data = json.load(f)
    fingerprint = data["fingerprint"]

    config = requests.get("https://gradecoin.xyz/config").json()
    min_block_size = config["block_transaction_count"]
    hash_zeros = config["hash_zeros"]

    transactions = requests.get("https://gradecoin.xyz/transaction").json()


    transaction_list = []
    timestamp = datetime.now().isoformat()

    own_transaction_list = []

    for transaction in transactions:
        if transactions[transaction]["source"] == fingerprint:
            own_transaction_list.append(transaction)
            transaction_list.append(transaction)
    
    for transaction in transactions:
        if len(transaction_list) >= min_block_size:
            break

        if transaction not in own_transaction_list:
            transaction_list.append(transaction)
    
    print(own_transaction_list)
    print(transaction_list)

    if(len(transaction_list) < min_block_size):
        print("Does not satisfy transaction amount.")
        return -1
    
    gfg = blake2s()

    while True:

        nonce = randint(0, 4294967295)

        blake2_json = {
            "transaction_list": transaction_list,
            "nonce": nonce,
            "timestamp": timestamp
        }

        blake2_str = json.dumps(blake2_json).replace(" ", "")
        gfg.update(blake2_str.encode())

        if gfg.hexdigest().startswith("0"*hash_zeros):
            blake2_json["hash"] = gfg.hexdigest()
            break

    print(blake2_json)
    print(gfg.hexdigest())
    print(type(gfg.hexdigest()))

    jwt_token = get_jwt_token(blake2_json["hash"])
    
    """
    headers = {
        'Authorization': 'Bearer ' + jwt_token.decode("utf-8"),
        'Content-Type': 'application/json'
    }

    response = requests.post(
        "https://gradecoin.xyz/block", headers=headers, json=blake2_json)
    

    print(response.headers)
    print(response.text)
    """
    return 0
        

if __name__ == "__main__":
    main()