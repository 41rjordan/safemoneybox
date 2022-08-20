import os
import json
import re

import sha3
from web3 import Web3
from web3.gas_strategies.rpc import rpc_gas_price_strategy
import solcx

# i'm not really good at python so this code may be a bit dirty

def validatePassword(password: str):
    if not re.search(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{16,}$".encode("utf8"), password):
        print("magic word and secret must contain at least 16 characters, at least one lowercase, one uppercase and one digit!")
        exit()

def main():
    print("recovery manager | WARNING:\nIT IS HIGHLY RECOMMENDED TO SCAN YOUR PC FOR MALWARES BEFORE USE\nOR TO USE CLEAN PC / ISOLATED VIRTUAL MACHINE.\nMALWARES CAN HIJACK SECRET OF YOUR CONTRACT AND STEAL YOUR FUNDS!\n")
    keydb = json.loads(open("key.json").read())
    networks = json.loads(open("networks.json").read())

    print("your account type: %s\nif it is wrong, change key.json file in this folder." % keydb["type"])
    print("choose network (available: {}):".format(networks.keys()))
    network = input()
    if network not in networks:
        print("there is no such network in networks.json!")
        return 0
    
    web3 = Web3(Web3.HTTPProvider(networks[network]["url"]))
    if not web3.isConnected():
        print("can't connect to web3!")
        return 0
    
    web3.eth.set_gas_price_strategy(rpc_gas_price_strategy)
    
    if keydb["type"] == "mnemonic":
        web3.eth.account.enable_unaudited_hdwallet_features()
        account = web3.eth.account.from_mnemonic(keydb["value"], account_path="m/44'/60'/0'/0/0")
    elif keydb["type"] == "privatekey":
        account = web3.eth.account.privateKeyToAccount(keydb["value"])
    else:
        print("invalid account type: %s" % keydb["type"])
        return 0
    
    print("your account address: %s" % account.address)

    print("enter your money box contract address:")
    contractAddress = Web3.toChecksumAddress(input())

    abi = json.loads(open("abi.json").read())
    contract = web3.eth.contract(address=contractAddress, abi=abi)

    print("enter your current secret:")
    oldsecret = input().encode("utf8")
    print("enter your new secret. also, write it down on a piece of paper. DO NOT SAVE IT ON A DIGITAL STORAGE!")
    newsecret = input().encode("utf8")
    validatePassword(newsecret)
    if oldsecret == newsecret:
        print("magic word and secret can't be the same!")
        return 0

    secrethash = sha3.keccak_256(newsecret).digest()
    del newsecret
    nonce = web3.eth.get_transaction_count(account.address)

    contract.functions.recovery(oldsecret, secrethash).call({
        "gas": 300000,
        "nonce": nonce,
        "from": account.address
    })

    estimated_gas = web3.eth.estimate_gas(contract.functions.recovery(oldsecret, secrethash).buildTransaction({
        "gas": 300000,
        "nonce": nonce,
        "from": account.address
    }))

    tx = contract.functions.recovery(oldsecret, secrethash).buildTransaction({
        "gas": estimated_gas,
        "gasPrice": web3.eth.generate_gas_price(),
        "nonce": nonce,
        "from": account.address
    })

    signed = account.sign_transaction(tx)
    txHash = web3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = web3.eth.wait_for_transaction_receipt(txHash)
    if receipt.status:
        print("recovery successful! gas used: %d\nnow you have full access to your contract." % receipt.gasUsed)
    else:
        print("transaction {} was reverted. logs: {}\nif logs are empty, submit an issue on github.com/41rjordan/safemoneybox.".format(receipt.transactionHash, receipt.logs))

main()