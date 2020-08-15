from flask import Flask, request, jsonify
from web3 import Web3
import sys
# from web3.auto import w3 # https://github.com/ethereum/web3.py/blob/master/docs/web3.eth.account.rst#sign-a-contract-transaction
import json
import binascii, os

# backend address
HOST = "0.0.0.0"
PORT = 7223

# Ethereum node address
NODEIP = "http://localhost:"
NODEPORT = "7224"
fullnode = Web3(Web3.HTTPProvider(NODEIP + NODEPORT))

# Ethereum coinbase account
PASSWORD = "1234"
fullnode.geth.personal.unlockAccount(fullnode.eth.coinbase, PASSWORD, 0)
fullnode.eth.defaultAccount = fullnode.eth.coinbase

# SGBJ smart contract
CONTRACTADDR = Web3.toChecksumAddress("0xc085d414945f120b696c5bf3f72f715d7ca2f20f")
# to get ABI of contract: https://remix.ethereum.org/
# to remove endline of abi: https://www.textfixer.com/tools/remove-line-breaks.php
abiString = '[ { "inputs": [], "payable": false, "stateMutability": "nonpayable", "type": "constructor" }, { "constant": false, "inputs": [ { "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "addDeposit", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "addWashCount", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [], "name": "greet", "outputs": [ { "internalType": "string", "name": "", "type": "string" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "greeting", "outputs": [ { "internalType": "string", "name": "", "type": "string" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "string", "name": "newGreeting", "type": "string" } ], "name": "setGreeting", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "address", "name": "", "type": "address" } ], "name": "usersBalance", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "address", "name": "", "type": "address" } ], "name": "usersWashCount", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "withdrawDeposit", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" } ]'
CONTRACTABI = json.loads(abiString)
sgbjContract = fullnode.eth.contract(address=CONTRACTADDR, abi=CONTRACTABI)

# dictionaries
usersBalance = dict()
usersWashCount = dict()



def sendTransaction(to):
    while True:
        try:
            fullnode.eth.sendTransaction(
                {'to': to, 'from': fullnode.eth.coinbase, 'value': '1', 'gas': '21000', 'data': ""})
            break
        except:
            continue

def generateRandomAddress():
	randHex = binascii.b2a_hex(os.urandom(20))
	return Web3.toChecksumAddress("0x" + randHex.decode('utf-8'))

app = Flask(__name__)
@app.route("/")
def hello():                           
    return "<h1>SGBJ backend</h1>"

@app.route('/json_test')
def hello_json():
    data = {'name' : 'Aaron', 'family' : 'Byun'}
    return jsonify(data)

@app.route('/post', methods=['POST'])
def post():
    param = request.get_json()
    print(param)  # dictionary

@app.route('/user', methods=['POST'])
def user():
    param = request.get_json()
    print(param)
    functionName = param['functionName']
    userName = param['userName']
    if functionName == "getUserInfo":
        response = {"balance" : usersBalance[userName], "washCount" : usersWashCount[userName]}
        return jsonify(response)
    elif functionName == "addBalance":
        amount = param['amount']
        usersBalance[userName] = usersBalance[userName] + amount
        response = {"result" : "success"}
        return jsonify(response)
    elif functionName == "subBalance":
        amount = param['amount']
        usersBalance[userName] = usersBalance[userName] - amount
        response = {"result" : "success"}
        return jsonify(response)
    elif functionName == "addWashCount":
        amount = param['amount']
        usersWashCount[userName] = usersWashCount[userName] + amount
        response = {"result" : "success"}
        return jsonify(response)
    else:
        response = {"error" : "wrong function name"}
        return jsonify(response)

@app.route('/blockchain', methods=['POST'])
def blockchain():
    param = request.get_json()
    print(param)
    functionName = param['functionName']
    if functionName == "getBlockNumber":
        response = {"blockNumber" : fullnode.eth.blockNumber}
        return jsonify(response)
    elif functionName == "addBalance":
        amount = param['amount']
        usersBalance[userName] = usersBalance[userName] + amount
        response = {"result" : "success"}
        return jsonify(response)
    else:
        response = {"error" : "wrong function name"}
        return jsonify(response)

if __name__ == "__main__":
    # print(sgbjContract.address)
    # print(sgbjContract.functions.getOwner().call())
    # tx_hash = sgbjContract.functions.setGreeting("nihao").transact()
    # # tx_receipt = fullnode.eth.waitForTransactionReceipt(tx_hash)
    # # print("tx receipt:", tx_receipt)
    # print(sgbjContract.functions.greet().transact())
    # sys.exit()

    # tx_hash = sgbjContract.functions.addDeposit(10).transact()
    # tx_receipt = fullnode.eth.waitForTransactionReceipt(tx_hash)
    # print("txreceipt:", tx_receipt)
    # print(sgbjContract.functions.getOwner().transact())
    # print(sgbjContract.functions.usersBalance(fullnode.eth.coinbase))

    print("usersBalance:", sgbjContract.functions.getOwner().call())
    try:
        print("current blocknumber:", fullnode.eth.blockNumber)
        print("coinbase:", fullnode.eth.coinbase)
    except:
        print("ERROR: cannot connect to Ethereum node. Start ethereum node first")
        sys.exit()
    
    app.run(host=HOST, port=PORT)
