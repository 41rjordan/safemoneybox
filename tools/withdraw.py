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

    balance = web3.eth.get_balance(contractAddress)/(10**18)
    print("contract balance: {} ETH".format(balance))

    print("what do you want to withdraw? eth/erc20")
    withdrawType = input().lower()

    if withdrawType == "eth":
        print("enter withdraw amount in ether:")
        amount = float(input())
        if amount > balance:
            print("insufficient funds!")
            return 0
        
        print("enter your current magic word:")
        oldmagicword = input().encode("utf8")
        print("enter your new magic word. also, write it down on a piece of paper. DO NOT SAVE IT ON A DIGITAL STORAGE!")
        newmagicword = input().encode("utf8")
        validatePassword(newmagicword)
        if oldmagicword == newmagicword:
            print("magic word and secret can't be the same!")
            return 0

        magicwordhash = sha3.keccak_256(newmagicword).digest()
        del newmagicword

        contract.functions.withdrawETH(int(amount * (10**18)), oldmagicword, magicwordhash).call({
            "gas": 300000,
            "nonce": web3.eth.get_transaction_count(account.address),
            "from": account.address
        })

        estimated_gas = web3.eth.estimate_gas(contract.functions.withdrawETH(int(amount * (10**18)), oldmagicword, magicwordhash).buildTransaction({
            "gas": 300000,
            "nonce": web3.eth.get_transaction_count(account.address),
            "from": account.address
        }))

        tx = contract.functions.withdrawETH(int(amount * (10**18)), oldmagicword, magicwordhash).buildTransaction({
            "gas": estimated_gas,
            "gasPrice": web3.eth.generate_gas_price(),
            "nonce": web3.eth.get_transaction_count(account.address),
            "from": account.address
        })

        signed = account.sign_transaction(tx)
        txHash = web3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = web3.eth.wait_for_transaction_receipt(txHash)
        if receipt.status:
            print("withdrawal successful! gas used: %d" % receipt.gasUsed)
        else:
            print("transaction {} was reverted. logs: {}\nif logs are empty, submit an issue on github.com/41rjordan/safemoneybox.".format(receipt.transactionHash, receipt.logs))
    
    elif withdrawType == "erc20":
        print("enter token contract address:")
        tokenContract = Web3.toChecksumAddress(input())

        print("enter withdraw amount in the smallest unit:")
        amount = int(input())
        
        print("enter your current magic word:")
        oldmagicword = input().encode("utf8")
        print("enter your new magic word. also, write it down on a piece of paper. DO NOT SAVE IT ON A DIGITAL STORAGE!")
        newmagicword = input().encode("utf8")
        validatePassword(newmagicword)
        if oldmagicword == newmagicword:
            print("magic word and secret can't be the same!")
            return 0

        magicwordhash = sha3.keccak_256(newmagicword).digest()
        del newmagicword
        nonce = web3.eth.get_transaction_count(account.address)

        contract.functions.withdrawERC20(tokenContract, amount, oldmagicword, magicwordhash).call({
            "gas": 300000,
            "nonce": nonce,
            "from": account.address
        })

        estimated_gas = web3.eth.estimate_gas(contract.functions.withdrawERC20(tokenContract, amount, oldmagicword, magicwordhash).buildTransaction({
            "gas": 300000,
            "nonce": nonce,
            "from": account.address
        }))

        tx = contract.functions.withdrawERC20(tokenContract, amount, oldmagicword, magicwordhash).buildTransaction({
            "gas": estimated_gas,
            "gasPrice": web3.eth.generate_gas_price(),
            "nonce": nonce,
            "from": account.address
        })

        signed = account.sign_transaction(tx)
        txHash = web3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = web3.eth.wait_for_transaction_receipt(txHash)
        if receipt.status:
            print("withdrawal successful! gas used: %d" % receipt.gasUsed)
        else:
            print("transaction {} was reverted. logs: {}\nif logs are empty, submit an issue on github.com/41rjordan/safemoneybox.".format(receipt.transactionHash, receipt.logs))
    
    else:
        print("unknown withdraw type!")

main()
