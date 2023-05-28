import json
import os
import requests

response = requests.get("https://gradecoin.xyz/config")

def main():
    for key in response.json():
        print(key, ":", response.json()[key], type(response.json()[key]))

if __name__ == "__main__":
    main()
