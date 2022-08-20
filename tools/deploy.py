import os
import json
import re

import sha3
from web3 import Web3
import solcx

# i'm not really good at python so this code may be a bit dirty

def validatePassword(password: str):
    if not re.search(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{16,}$", password):
        print("magic word and secret must contain at least 16 characters, at least one lowercase, one uppercase and one digit!")
        exit()

def main():
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
    
    if keydb["type"] == "mnemonic":
        web3.eth.account.enable_unaudited_hdwallet_features()
        account = web3.eth.account.from_mnemonic(keydb["value"], account_path="m/44'/60'/0'/0/0")
    elif keydb["type"] == "privatekey":
        account = web3.eth.account.privateKeyToAccount(keydb["value"])
    else:
        print("invalid account type: %s" % keydb["type"])
        return 0
    
    print("your account address: %s" % account.address)
    
    print("enter your magic word. this word will be used to withdraw from contract.\nalso, write it down on a piece of paper. DO NOT SAVE IT ON A DIGITAL STORAGE!")
    magicword = input()
    validatePassword(magicword)
    print("enter your secret. it will be used to restore access to contract in case of loss of private key.\nalso, write it down on a piece of paper. DO NOT SAVE IT ON A DIGITAL STORAGE!\nif you don't want to be able to recover your contract, press enter.")
    secret = input()
    if secret:
        validatePassword(secret)
    if magicword == secret:
        print("magic word and secret can't be the same!")
        return 0

    magicwordhash = sha3.keccak_256(magicword.encode("utf8")).digest()
    if secret:
        secrethash = sha3.keccak_256(secret.encode("utf8")).digest()
    else:
        secrethash = b"\x00" * 32

    del magicword
    del secret

    upper = os.path.split(os.getcwd())[0]
    os.chdir(upper)
    
    print("have you used this tool before? y/n")
    inp = input().lower()
    installed = True if inp == "y" else False

    if not installed:
        print("installing solc...")
        solcx.install_solc("0.8.7")
    
    print("compiling contract...")

    try:
        compiled = solcx.compile_files("smb.sol", solc_version="0.8.7")
    except:
        print("compilation failed! if you answered Y, run this script again with N answer. your funds are safe.")

    print("compilation successful!\ndeploying contract...")

    contract = web3.eth.contract(abi=compiled["smb.sol:safemoneybox"]["abi"], bytecode=compiled["smb.sol:safemoneybox"]["bin"])
    construct = contract.constructor(magicwordhash, secrethash).buildTransaction(
        {
            "from": account.address,
            "nonce": web3.eth.get_transaction_count(account.address)
        }
    )
    
    tx = account.sign_transaction(construct)
    txHash = web3.eth.send_raw_transaction(tx.rawTransaction)
    receipt = web3.eth.wait_for_transaction_receipt(txHash)
    if receipt.status:
        print("contract deployed! gas consumed: {}\naddress: {}\nnow you can use this address to receive safe payments.\nuse withdraw.py script to withdraw funds.".format(receipt.gasUsed, receipt.contractAddress))
    else:
        print("transaction {} was reverted. logs: {}\nif logs are empty, submit an issue on github.com/41rjordan/safemoneybox.".format(receipt.transactionHash, receipt.logs))

main()