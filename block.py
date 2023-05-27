from Crypto.PublicKey import RSA
from hashlib import blake2s
from datetime import datetime
import jwt
import binascii
import json
import base64
import os
import requests

min_block_size = ""
hash_zeros = ""

def main():
    f = open("student_data.json")
    data = json.load(f)
    fingerprint = data["fingerprint"]

    config = requests.get("https://gradecoin.xyz/config").json()
    min_block_size = config["block_transaction_count"]
    hash_zeros = config["hash_zeros"]

    transactions = requests.get("https://gradecoin.xyz/transaction").json()


    transaction_list = []
    nonce = randint(0, 4294967295)
    timestamp = datetime.now().isoformat()

    own_transaction = ""

    for transaction in transactions:
        if transactions[transaction]["source"] == fingerprint:
            own_transaction = transaction
            transaction_list.append(transaction)
    
    for transaction in transactions:
        if len(transaction_list) >= min_block_size:
            break

        if transaction != own_transaction:
            transaction_list.append(transaction)

    blake2_json = {
        "transaction_list": transaction_list,
        "nonce": nonce,
        "timestamp": timestamp
    }

    if __name__ == "__main__":
    main()