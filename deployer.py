import re
import os
import time
from web3 import Web3
from solcx import compile_source, install_solc, set_solc_version

install_solc("0.8.21")
set_solc_version("0.8.21")

RPC_URL = "https://testnet-rpc.monad.xyz"
CHAIN_ID = 10143

def read_private_keys():
    private_keys = []
    private_key = input("Please enter your private key: ")  
    private_keys.append(private_key)
    return private_keys

def deploy_contract(web3, private_key, greeting_text):
    account = web3.eth.account.from_key(private_key)
    
    if not web3.is_connected():
        print("❌ Failed to connect to blockchain")
        return
    
    print(f"🔑 Using Account: {account.address}")
    print(f"✅ Connected to {RPC_URL}")
    
    contract_source_code = '''
    // SPDX-License-Identifier: MIT
    pragma solidity >=0.8.0 <=0.8.24;
    contract Gmonad { 
        string public greeting;
        constructor(string memory _greeting) {
            greeting = _greeting;
        }
        function setGreeting(string calldata _greeting) external {
            greeting = _greeting;
        }
    }
    '''

    compiled_sol = compile_source(contract_source_code)
    contract_id, contract_interface = compiled_sol.popitem()

    Gmonad = web3.eth.contract(abi=contract_interface["abi"], bytecode=contract_interface["bin"])
    tx = Gmonad.constructor(greeting_text).build_transaction({
        'from': account.address,
        'nonce': web3.eth.get_transaction_count(account.address),
        'gas': 3000000,
        'maxFeePerGas': web3.to_wei('60', 'gwei'),
        'maxPriorityFeePerGas': web3.to_wei('2', 'gwei'),
        'chainId': CHAIN_ID
    })

    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"🎉 Contract deployed at {tx_receipt.contractAddress}")
    return tx_receipt.contractAddress

web3 = Web3(Web3.HTTPProvider(RPC_URL))
private_keys = read_private_keys()

greeting_text = "Hello, Gmonad!"

deploy_interval_minutes = int(input("Please enter the deployment interval in minutes: "))
deploy_interval = deploy_interval_minutes * 60  

while True:
    for private_key in private_keys:
        deploy_contract(web3, private_key, greeting_text)
        time.sleep(deploy_interval) 
