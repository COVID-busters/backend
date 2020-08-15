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
# to get web3js contract employing code: https://remix.ethereum.org/ (CAUSION: need to setting evm version as "byzantium")
# put employ code to geth console & start mining => then we will get contract address
CONTRACTADDR = Web3.toChecksumAddress("0xe66840E9821D06Ea7ca1aA8328DbA56883543f8A")
# to get ABI of contract: https://remix.ethereum.org/
# to remove endline of abi: https://www.textfixer.com/tools/remove-line-breaks.php
abiString = '[ { "inputs": [], "payable": false, "stateMutability": "nonpayable", "type": "constructor" }, { "constant": false, "inputs": [ { "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "addDeposit", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "addWashCount", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [], "name": "balanceSum", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "greet", "outputs": [ { "internalType": "string", "name": "", "type": "string" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "greeting", "outputs": [ { "internalType": "string", "name": "", "type": "string" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "interestRate", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "lottoEpoch", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [], "name": "selectWinner", "outputs": [ { "internalType": "address", "name": "", "type": "address" }, { "internalType": "address", "name": "", "type": "address" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "string", "name": "newGreeting", "type": "string" } ], "name": "setGreeting", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "name": "users", "outputs": [ { "internalType": "address", "name": "", "type": "address" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "address", "name": "", "type": "address" } ], "name": "usersBalance", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "address", "name": "", "type": "address" } ], "name": "usersWashCount", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "washCountSum", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "withdrawDeposit", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" } ]'
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
    elif functionName == "addDeposit":
        amount = param['amount']
        try:
            tx_hash = sgbjContract.functions.addDeposit(amount).transact()
            tx_receipt = fullnode.eth.waitForTransactionReceipt(tx_hash)
        except:
            response = {"result" : "failed"}
            return jsonify(response)
        usersBalance[userName] = usersBalance[userName] + amount
        response = {"result" : "success"}
        return jsonify(response)
    elif functionName == "subBalance":
        amount = param['amount']
        try:
            tx_hash = sgbjContract.functions.withdrawDeposit(amount).transact()
            tx_receipt = fullnode.eth.waitForTransactionReceipt(tx_hash)
        except:
            response = {"result" : "failed"}
            return jsonify(response)
        usersBalance[userName] = usersBalance[userName] - amount
        response = {"result" : "success"}
        return jsonify(response)
    elif functionName == "addWashCount":
        amount = param['amount']
        try:
            tx_hash = sgbjContract.functions.addWashCount(amount).transact()
            tx_receipt = fullnode.eth.waitForTransactionReceipt(tx_hash)
        except:
            response = {"result" : "failed"}
            return jsonify(response)
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
    
    # function call & wait for the tx to be mined (with enough gas)
    # https://web3py.readthedocs.io/en/latest/contracts.html#web3.contract.ContractFunction.call
    tx_hash = sgbjContract.functions.addWashCount(10).transact({'gas':1000000})
    tx_receipt = fullnode.eth.waitForTransactionReceipt(tx_hash)
    print (tx_receipt)
    
    # getter function call
    getGreet = sgbjContract.functions.greet().call()
    print(getGreet)

    # getter function call
    getWashCount = sgbjContract.functions.usersWashCount(fullnode.eth.coinbase).call()
    print(getWashCount)

    # sys.exit()

    try:
        print("current blocknumber:", fullnode.eth.blockNumber)
        print("coinbase:", fullnode.eth.coinbase)
    except:
        print("ERROR: cannot connect to Ethereum node. Start ethereum node first")
        sys.exit()
    
    app.run(host=HOST, port=PORT)
