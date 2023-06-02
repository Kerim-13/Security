from datetime import datetime
from random import randint
from Crypto.Hash import BLAKE2s
import multiprocessing
import copy
import Register
import Transaction
import Block
import Config
import sys
import argparse
import json
import requests
import time

TRANSACTION_NOT_EXISTS = -1
NUM_THREADS = 8
MAX_NONCE = 4294967295

globalFingerpint = "1c6f23a225f97b9d72ba4f3d9b4da30e2e8a4ec0a223be7386944c419bf24893"
bots = ["f44f83688b33213c639bc16f9c167543568d4173d5f4fc7eb1256f6c7bb23b26", "5dcdedc9a04ea6950153c9279d0f8c1ac9528ee8cdf5cd912bebcf7764b3f9db", 
            "a4d9a38a04d0aa7de7c29fef061a1a539e6a192ef75ea9730aff49f9bb029f99", "4319647f2ad81e83bf602692b32a082a6120c070b6fd4a1dbc589f16d37cbe1d"]

blockQueue = multiprocessing.Queue(maxsize=1)

def findTransaction(source, target):
    transactions = requests.get("https://gradecoin.xyz/transaction").json()
    
    for key in transactions:
        if transactions[key]["source"] == source and transactions[key]["target"] == target:
            return key

    return TRANSACTION_NOT_EXISTS

def mineBlock(idx, transaction_list, begin, end):

    config = requests.get("https://gradecoin.xyz/config").json()
    hash_zeros = config["hash_zeros"]

    timestamp = datetime.now().isoformat()
    for i in range(begin, end+1):

        nonce = i

        blake2_json = {
            "transaction_list": transaction_list,
            "nonce": nonce,
            "timestamp": timestamp
        }

        blake2_str = json.dumps(blake2_json).replace(" ", "")
        gfg = BLAKE2s.new(digest_bits=256)
        gfg.update(blake2_str.encode())

        if gfg.hexdigest().startswith("0"*hash_zeros):
            blake2_json["hash"] = gfg.hexdigest()
            break
    
    print("Solved Hash:", idx)
    blockQueue.put(blake2_json)

def solveBlockMultiThread(transactionBlock):
    processes = []
    interval = (MAX_NONCE // NUM_THREADS) + 1
    print("Starting solvers.")
    for i in range(NUM_THREADS):
        process = multiprocessing.Process(target=mineBlock, args=(i, copy.deepcopy(transactionBlock), i * interval, (i+1)*interval))
        processes.append(process)
        process.start()

    blake2Json = blockQueue.get()

    print("Stopping solvers.")
    for i in range(NUM_THREADS):
        process = processes[i]
        process.terminate()

    return blake2Json

def getBotTransactions(target):
    transactions = requests.get("https://gradecoin.xyz/transaction").json()
    transactionList = []

    for key in transactions:
        if transactions[key]["target"] == target and transactions[key]["source"] in bots:
            transactionList.append(key)

    for key in transactions:
        if transactions[key]["target"] != target and transactions[key]["source"] in bots:
            transactionList.append(key)

    return transactionList

def getOtherTransactions(source):
    transactions = requests.get("https://gradecoin.xyz/transaction").json()
    transactionList = getBotTransactions(source)

    for key in transactions:
        if transactions[key]["source"] != source and transactions[key]["source"] not in bots:
            transactionList.append(key)

    return transactionList

def getSendingTransactions(source):
    transactions = requests.get("https://gradecoin.xyz/transaction").json()
    transactionList = []

    for key in transactions:
        if transactions[key]["source"] == source:
            transactionList.append(key)

    return transactionList

def minerBot(fingerprint):
    
    cnt = 0

    while True:
        config = requests.get("https://gradecoin.xyz/config").json()
        
        otherTransactions = getOtherTransactions(fingerprint)
        sendingTransactions = getSendingTransactions(fingerprint)
        while len(otherTransactions) < (config["block_transaction_count"] - (len(bots) - len(sendingTransactions))):
            time.sleep(60)
            config = requests.get("https://gradecoin.xyz/config").json()
            otherTransactions = getOtherTransactions(fingerprint)
            
        print("Found enough transactions.")

        for bot in bots:
            tId = findTransaction(fingerprint, bot)

            if tId == TRANSACTION_NOT_EXISTS:
                response = Transaction.send_transaction(fingerprint, bot, config["tx_lower_limit"], config)
                print(json.dumps(response.json(), indent=4, sort_keys=True))

        sendingTransactions = getSendingTransactions(fingerprint)
        otherTransactions = getOtherTransactions(fingerprint)


        print(len(sendingTransactions))
        allTransactions = sendingTransactions + otherTransactions
        transactionBlock = []
        for i in range(config["block_transaction_count"]):
            transactionBlock.append(allTransactions[i])

        print("Starting solution process.")
        blake2Json = solveBlockMultiThread(transactionBlock)
        print("Sending block requests.")
        response = Block.send_block_request(blake2Json)

        cnt += 1
        print("Blocks mined:", cnt)
        print(response.status_code)
        print(json.dumps(response.json(), indent=4, sort_keys=True))

    return 0
        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fingerprint")
    args = parser.parse_args()

    fingerprint = args.fingerprint
    ret = minerBot(fingerprint)
    print(ret)
    return 0

if __name__ == "__main__":
    main()