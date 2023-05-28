import Register
import Transaction
import Block
import Config
import sys
import argparse
import json
import requests

def transaction_pair_exists(source, target):
    transactions = requests.get("https://gradecoin.xyz/transaction").json()

    for transaction in transactions:
        if transactions[transaction]["source"] == source and transactions[transaction]["target"] == target:
            return True

    return False

def find_transaction_pair(source, target):
    transactions = requests.get("https://gradecoin.xyz/transaction").json()

    for transaction in transactions:
        if transactions[transaction]["source"] == source and transactions[transaction]["target"] == target:
            return transaction

    return -1

def get_users():
    f = open("users.json")
    data = json.load(f)

    return data["users"], data["bots"]

def get_other_transactions(fingerprint):
    transactions = requests.get("https://gradecoin.xyz/transaction").json()
    other_transactions = []
    
    for transaction in transactions:
        if transactions[transaction]["source"] != fingerprint:
            other_transactions.append(transaction)

    return other_transactions

def get_my_transactions(fingerprint):
    transactions = requests.get("https://gradecoin.xyz/transaction").json()
    my_transactions = []

    for transaction in transactions:
        if transactions[transaction]["source"] == fingerprint:
            my_transactions.append(transaction)
    
    return my_transactions

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fingerprint")
    args = parser.parse_args()

    config = requests.get("https://gradecoin.xyz/config").json()
    min_block_size = config["block_transaction_count"]

    fingerprint = args.fingerprint
    my_transactions = get_my_transactions(fingerprint)
    other_transactions = get_other_transactions(fingerprint)
    users, bots = get_users()
    
    while True:
        if len(my_transactions) == 0:
            target = bots[0]
            amount = config["tx_lower_limit"]
            Transaction.send_transaction(fingerprint, target, amount, config)
            transaction = find_transaction_pair(fingerprint, target)

            if(transaction != -1):
                my_transactions.append(transaction)
            else:
                print("Couldn't find such a pair.")
                return -1

        transaction_sum = len(my_transactions) + len(other_transactions)

        for target in bots:
            if transaction_sum >= min_block_size:
                break

            if not transaction_pair_exists(fingerprint, target):
                amount = config["tx_lower_limit"]
                Transaction.send_transaction(fingerprint, target, amount, config)
                transaction = find_transaction_pair(fingerprint, target)

                if(transaction != -1):
                    my_transactions.append(transaction)
                    transaction_sum += 1
                else:
                    print("Couldn't find such a pair.")
                    return -1

        for target in users:
            if transaction_sum >= min_block_size:
                break

            if not transaction_pair_exists(fingerprint, target):
                amount = config["tx_lower_limit"]
                Transaction.send_transaction(fingerprint, target, amount, config)
                transaction = find_transaction_pair(fingerprint, target)

                if(transaction != -1):
                    my_transactions.append(transaction)
                    transaction_sum += 1
                else:
                    print("Couldn't find such a pair.")
                    return -1

        ret = Block.send_block(fingerprint)

    return 0

if __name__ == "__main__":
    main()