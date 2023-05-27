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
    config = requests.get("https://gradecoin.xyz/config").json()
    min_block_size = config["block_transaction_count"]
    hash_zeros = config["hash_zeros"]

    transaction_list = []
    nonce = randint(0, 4294967295)
    timestamp = datetime.now().isoformat()
if __name__ == "__main__":
    main()