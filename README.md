# safemoneybox
Ethereum smart contract money box secured by password

## What is it?
Safemoneybox (smb) - smart contract that acts like a money box, linked to one account (owner), but secured by one-time password.  
Contract stores keccak256 hash of magic word (password for withdrawal) and secret (password for recovery, can be removed on deployment). To withdraw, you should reveal magic word and upload new magic word hash. The same mechanism is in recovery. Recovery is a function that allows to move rights to contract to other account in case of loss of your private key.  
Smb is light & cheap, it consumes ~1kk gas on deployment (7-20$ at the time of writing) and 30-50k gas on withdrawal (<1$ at the time of writing).  
Supports storage of Ethereum and ERC20 tokens.

## Use cases
The simplest - if someone steals your pc, or phone, or hardware wallet, they won't be able to withdraw funds without magic word.  
Meanwhile, you'll still be able to recover your contract with secret (however, I wouldn't recommend to do it, if you have no access to a miner/staker that will include your recovery transaction directly in block).

## How to use

### Installation and configuration
1. Install python 3 and packages. There are shell scripts in tools/install_packages. You can use them to install packages.  
2. Enter your account key to tools/key.json. If you have a seed phrase, enter it in the `value` field, and enter `mnemonic` in the `type` field. If you have a private key, enter it in hex encoding in the `value` field, and enter `privatekey` in the `type` field.
3. If you have a custom RPC or want to add custom network, add it in networks.json file.

### Deployment
1. Top up your ethereum account with approximately 0.02 ETH - this is the approximate deployment cost at 20 gwei gas price. Most likely, network gas price will be lower (rn it is only 7 gwei :P), you can top up ETH in the proportion to [network gas price](https://etherscan.io/gastracker).
2. Run tools/deploy.py. Do everything as it says. If it fails on connection to RPC, change RPC in the networks.json file. **I strongly recommend that you do not use a password that you have ever used on any services. Also I recommend to remove your key from key.json and enter it again only when you will withdraw funds from contract.**
3. Done! Write your magic word and secret **on a piece of paper** and save contract address anywhere. Now you can use this address as recipient address (that is, give it to anyone who wants to send you money).

### Withdrawal
1. Top up your ethereum account with approximately 0.001 ETH - this is the approximate ERC20 withdrawal cost at 20 gwei gas price. Ether withdrawal is cheaper.
2. If you deleted your key after deployment, enter it again in key.json file.
3. Run tools/withdraw.py. Do everything as it says. Most of the errors are already handled, so if it fails - check issues, and search for your error. If there is no such error, submit an issue by yourself.
4. **Remove your key from key.json file.**

## License and contribution
There is no license, do whatever you want, but I would like you to mention me. Feel free to contribute and offer your ideas!

#### Version info
Version 1: Tested on goerli testnet (post-merge), works as it should. There should be no problems on post-merge ethereum either
