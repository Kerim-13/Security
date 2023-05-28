import json
import requests

response = requests.get("https://gradecoin.xyz/user")
print(response.text)