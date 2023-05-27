from hashlib import sha256
import jwt
import binascii
import json
import base64
import os
import requests

r = requests.get('https://httpbin.org/basic-auth/user/pass',
                 auth=('user', 'pass'))

print(r.json())
