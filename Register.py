from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from hashlib import sha256
import argparse
import sys
import jwt
import binascii
import json
import base64
import os
import requests

class AESCipher():
    def __init__(self, key, IV, mode=AES.MODE_CBC):
        self.encryptor = AES.new(key, mode, IV=IV)

    def pad(self, m):
        return m+chr(16-len(m) % 16)*(16-len(m) % 16)

    def encrypt(self, raw):
        raw = self.pad(raw)
        cipher = base64.b64encode(self.encryptor.encrypt(raw))

        return cipher

    def encrypt_json(self, json_raw):
        str_raw = json.dumps(json_raw)
        bytes_raw = self.pad(str_raw).encode()
        cipher = base64.b64encode(self.encryptor.encrypt(bytes_raw))

        return cipher


class OAEP():
    def __init__(self, key, hashAlgo=SHA256):
        self.encryptor = PKCS1_OAEP.new(key=key, hashAlgo=hashAlgo)

    def encrypt(self, raw):
        cipher = base64.b64encode(self.encryptor.encrypt(raw))

        return cipher


def register_student(student_id, one_time_password):

    if not os.path.isfile("private_key.pem") and not os.path.isfile("public_key.pem"):
        print("Files don't exist.")

        new_key = RSA.generate(2048)

        own_private_key = new_key.exportKey("PEM", pcks=8)
        own_public_key = new_key.publickey().exportKey("PEM")
        gradecoin_public_key = RSA.import_key(open('gradecoin.pub').read())
        own_public_key_str = open('public_key.pem', "r").read()
        own_private_key_str = open('private_key.pem', "r").read()

        fd = open("private_key.pem", "wb")
        fd.write(own_private_key)
        fd.close()

        fd = open("public_key.pem", "wb")
        fd.write(own_public_key)
        fd.close()

    else:
        print("Files exist.")

        own_private_key = RSA.import_key(open('private_key.pem', "rb").read())
        own_public_key = RSA.import_key(open('public_key.pem', "rb").read())
        own_public_key_str = open('public_key.pem', "r").read()
        own_private_key_str = open('private_key.pem', "r").read()
        gradecoin_public_key = RSA.import_key(
            open('gradecoin.pub', "rb").read())

    register_json = {
        "student_id": student_id,
        "passwd": one_time_password,
        "public_key": own_public_key_str
    }

    if not os.path.isfile("register.json"):
        with open("register.json", "w") as write:
            json.dump(register_json, write)

    key = os.urandom(16)
    iv = os.urandom(16)

    print("Key:\n", base64.b64encode((key)).decode('ascii'))
    print("IV:\n", base64.b64encode((iv)).decode('ascii'))

    """
    with open("register.json", "rb") as read:
        print(read.read().decode('ascii'))
    """

    aes = AESCipher(key, iv, AES.MODE_CBC)
    register_cipher = aes.encrypt_json(register_json)

    oaep = OAEP(gradecoin_public_key, SHA256)
    key_ciphertext = oaep.encrypt(key)

    IV_b64 = base64.b64encode(iv)

    print("register_cipher:\n", register_cipher.decode('ascii'))
    print("key_ciphertext:\n", key_ciphertext.decode('ascii'))
    print("IV_b64:\n", IV_b64.decode('ascii'))

    json_payload = {
        "c": register_cipher.decode('utf-8'),
        "iv": IV_b64.decode('utf-8'),
        "key": key_ciphertext.decode('utf-8'),
    }

    response = requests.post(
        "https://gradecoin.xyz/register", json=json_payload)

    print(response.status_code)
    print(response.text)
    print(response.headers)

    if not os.path.isfile("response.json"):
        with open("response.json", "w") as write:
            json.dump(response.json(), write)

    print(response.json())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--number")
    parser.add_argument("-p", "--password")
    args = parser.parse_args()
    """
    f = open("student_data.json")
    data = json.load(f)
    """

    student_id = args.number
    one_time_password = args.password

    print(student_id, type(student_id))
    print(one_time_password, type(one_time_password))
    
    register_student(student_id, one_time_password)

if __name__ == "__main__":
    main()
