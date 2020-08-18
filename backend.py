from flask import Flask, request, jsonify
from flask_cors import CORS
from web3 import Web3
import sys
# from web3.auto import w3 # https://github.com/ethereum/web3.py/blob/master/docs/web3.eth.account.rst#sign-a-contract-transaction
import json
import binascii, os
import random

# backend address
HOST = "0.0.0.0"
PORT = 7223

# Ethereum node address
# Geth version: Geth/v1.9.0-unstable-3a92ba4c-20200706/linux-amd64/go1.10.4
# web3 version: 5.12.0 (how to know -> $ pip3 freeze | grep web3)
NODEIP = "http://localhost:"
NODEPORT = "7224"
fullnode = Web3(Web3.HTTPProvider(NODEIP + NODEPORT))

# Ethereum coinbase account
PASSWORD = "1234"
fullnode.geth.personal.unlockAccount(fullnode.eth.coinbase, PASSWORD, 0)
fullnode.eth.defaultAccount = fullnode.eth.coinbase

# SGBJ smart contract
# remix settings: https://remix.ethereum.org/#optimize=false&evmVersion=byzantium&version=soljson-v0.5.17+commit.d19bba13.js
# to get web3js contract employing code: https://remix.ethereum.org/ (CAUSION: need to setting evm version as "byzantium")
# put employ code to geth console & start mining => then we will get contract address
CONTRACTADDR = Web3.toChecksumAddress("0xB201a0e33f7c0c672629be21bF027701A39D0F4B")
# to get ABI of contract: https://remix.ethereum.org/
# to remove endline of abi: https://www.textfixer.com/tools/remove-line-breaks.php
abiString = '[ { "inputs": [], "payable": false, "stateMutability": "nonpayable", "type": "constructor" }, { "constant": false, "inputs": [ { "internalType": "uint256", "name": "amount", "type": "uint256" }, { "internalType": "address", "name": "userAddr", "type": "address" } ], "name": "addDeposit", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "uint256", "name": "amount", "type": "uint256" }, { "internalType": "address", "name": "userAddr", "type": "address" } ], "name": "addWashCount", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [], "name": "balanceSum", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "name": "depositWinners", "outputs": [ { "internalType": "address", "name": "", "type": "address" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "greet", "outputs": [ { "internalType": "string", "name": "", "type": "string" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "greeting", "outputs": [ { "internalType": "string", "name": "", "type": "string" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "interestRate", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "lottoEpoch", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "roundNumber", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [], "name": "selectWinner", "outputs": [ { "internalType": "address", "name": "", "type": "address" }, { "internalType": "address", "name": "", "type": "address" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "uint256", "name": "newLottoEpoch", "type": "uint256" } ], "name": "setEpoch", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "string", "name": "newGreeting", "type": "string" } ], "name": "setGreeting", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [], "name": "userCount", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "name": "users", "outputs": [ { "internalType": "address", "name": "", "type": "address" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "address", "name": "", "type": "address" } ], "name": "usersBalance", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "address", "name": "", "type": "address" } ], "name": "usersWashCount", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "washCountSum", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "name": "washCountWinners", "outputs": [ { "internalType": "address", "name": "", "type": "address" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "name": "winningsAmount", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "uint256", "name": "amount", "type": "uint256" }, { "internalType": "address", "name": "userAddr", "type": "address" } ], "name": "withdrawDeposit", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" } ]'
CONTRACTABI = json.loads(abiString)
sgbjContract = fullnode.eth.contract(address=CONTRACTADDR, abi=CONTRACTABI)

# gas amount for transaction (should be large enough)
GAS = 1000000

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
CORS(app)
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

    if functionName == "getUserInfo":
        userAddr = param['userAddr']
        try:
            balance = sgbjContract.functions.usersBalance(userAddr).call()
            washCount = sgbjContract.functions.usersWashCount(userAddr).call()
            response = {"balance" : balance, "washCount" : washCount, "result" : "success"}
            return jsonify(response)
        except:
            response = {"result" : "fail"}
            return jsonify(response)
    
    elif functionName == "getUserCount":
        try:
            userCount = sgbjContract.functions.userCount().call()
            response = {"userCount": userCount, "result" : "success"}
            return jsonify(response)
        except:
            response = {"result" : "fail"}
            return jsonify(response)

    elif functionName == "getLottoEpoch":
        try:
            lottoEpoch = sgbjContract.functions.lottoEpoch().call()
            response = {"lottoEpoch": lottoEpoch, "result" : "success"}
            return jsonify(response)
        except:
            response = {"result" : "fail"}
            return jsonify(response)

    elif functionName == "addDeposit":
        amount = param['amount']
        userAddr = param['userAddr']
        try:
            tx_hash = sgbjContract.functions.addDeposit(amount, userAddr).transact({'gas':GAS})
            tx_receipt = fullnode.eth.waitForTransactionReceipt(tx_hash)
            response = {"result" : "success"}
            return jsonify(response)
        except:
            response = {"result" : "fail"}
            return jsonify(response)
            
    elif functionName == "withdrawDeposit":
        amount = param['amount']
        userAddr = param['userAddr']
        try:
            tx_hash = sgbjContract.functions.withdrawDeposit(amount, userAddr).transact({'gas':GAS})
            tx_receipt = fullnode.eth.waitForTransactionReceipt(tx_hash)
            response = {"result" : "success"}
            return jsonify(response)
        except:
            response = {"result" : "fail"}
            return jsonify(response)
            
    elif functionName == "addWashCount":
        amount = param['amount']
        userAddr = param['userAddr']
        try:
            tx_hash = sgbjContract.functions.addWashCount(amount, userAddr).transact({'gas':GAS})
            tx_receipt = fullnode.eth.waitForTransactionReceipt(tx_hash)
            response = {"result" : "success"}
            return jsonify(response)
        except:
            response = {"result" : "fail"}
            return jsonify(response)
    
    elif functionName == "getTotalDeposit":
        try:
            totalDeposit = sgbjContract.functions.balanceSum().call()
            response = {"totalDeposit": totalDeposit, "result" : "success"}
            return jsonify(response)
        except:
            response = {"result" : "fail"}
            return jsonify(response)

    elif functionName == "getTotalWashCount":
        try:
            totalWashCount = sgbjContract.functions.washCountSum().call()
            response = {"totalWashCount": totalWashCount, "result" : "success"}
            return jsonify(response)
        except:
            response = {"result" : "fail"}
            return jsonify(response)

    elif functionName == "selectWinner":
        try:
            tx_hash = sgbjContract.functions.selectWinner().transact({'gas':GAS})
            tx_receipt = fullnode.eth.waitForTransactionReceipt(tx_hash)
            
            # temp code for demo: insert random user1, user2 at every round

            # insert random user1
            user1Addr = generateRandomAddress()
            depositAmount = random.randint(1,300)
            washCountAmount = random.randint(1,3)
            tx_hash = sgbjContract.functions.addDeposit(depositAmount, user1Addr).transact({'gas':GAS})
            tx_receipt = fullnode.eth.waitForTransactionReceipt(tx_hash)
            tx_hash = sgbjContract.functions.addWashCount(washCountAmount, user1Addr).transact({'gas':GAS})
            tx_receipt = fullnode.eth.waitForTransactionReceipt(tx_hash)

            # insert random user2
            user2Addr = generateRandomAddress()
            depositAmount = random.randint(1,300)
            washCountAmount = random.randint(1,3)
            tx_hash = sgbjContract.functions.addDeposit(depositAmount, user2Addr).transact({'gas':GAS})
            tx_receipt = fullnode.eth.waitForTransactionReceipt(tx_hash)
            tx_hash = sgbjContract.functions.addWashCount(washCountAmount, user2Addr).transact({'gas':GAS})
            tx_receipt = fullnode.eth.waitForTransactionReceipt(tx_hash)

            response = {"result" : "success"}
            return jsonify(response)
        except:
            response = {"result" : "fail"}
            return jsonify(response)
    
    elif functionName == "getRoundNumber":
        try:
            roundNumber = sgbjContract.functions.roundNumber().call()
            response = {"roundNumber": roundNumber, "result" : "success"}
            return jsonify(response)
        except:
            response = {"result" : "fail"}
            return jsonify(response)

    elif functionName == "getWinningProbability":
        userAddr = param['userAddr']
        try:
            deposit = sgbjContract.functions.usersBalance(userAddr).call()
            washCount = sgbjContract.functions.usersWashCount(userAddr).call()

            totalDeposit = sgbjContract.functions.balanceSum().call()
            totalWashCount = sgbjContract.functions.washCountSum().call()

            depositWinProb = 0
            washCountWinProb = 0

            if deposit != 0:
                depositWinProb = float(deposit) / float(totalDeposit) * float(100)
            if washCount != 0:
                washCountWinProb = float(washCount) / float(totalWashCount) * float(100)

            response = {"depositWinProb": depositWinProb, "washCountWinProb": washCountWinProb, "result" : "success"}
            return jsonify(response)
        except:
            response = {"result" : "fail"}
            return jsonify(response)

    elif functionName == "getWinnersInfo":
        roundNumber = param['roundNumber']
        try:
            depositWinner = sgbjContract.functions.depositWinners(roundNumber).call()
            washCountWinner = sgbjContract.functions.washCountWinners(roundNumber).call()
            winningPrizeAmount = sgbjContract.functions.winningsAmount(roundNumber).call()
            response = {"depositWinner": depositWinner, "washCountWinner": washCountWinner, "winningPrizeAmount": winningPrizeAmount, "result" : "success"}
            return jsonify(response)
        except:
            response = {"result" : "fail"}
            return jsonify(response)

    elif functionName == "sendRawTransaction":
        rawTx = param['rawTransaction']
        try:
            fullnode.eth.sendRawTransaction(rawTx)
            response = {"result" : "success"}
            return jsonify(response)
        except:
            response = {"result" : "fail"}
            return jsonify(response)

    elif functionName == "getRandomAddress":
        try:
            response = {"randomAddr": generateRandomAddress(), "result" : "success"}
            return jsonify(response)
        except:
            response = {"result" : "fail"}
            return jsonify(response)

    else:
        response = {"result" : "fail", "error" : "wrong function name"}
        return jsonify(response)

@app.route('/blockchain', methods=['POST'])
def blockchain():
    param = request.get_json()
    print(param)
    functionName = param['functionName']
    if functionName == "getBlockNumber":
        response = {"blockNumber" : fullnode.eth.blockNumber}
        return jsonify(response)
    elif functionName == "startMining":
        fullnode.geth.miner.start(1)
        response = {"result" : "success"}
        return jsonify(response)
    elif functionName == "stopMining":
        fullnode.geth.miner.stop()
        response = {"result" : "success"}
        return jsonify(response)
    else:
        response = {"error" : "wrong function name"}
        return jsonify(response)

if __name__ == "__main__":

    # function call & wait for the tx to be mined (with enough gas)
    # https://web3py.readthedocs.io/en/latest/contracts.html#web3.contract.ContractFunction.call

    # transact(): send transaction
    # call(): get contract state = not send transaction (ex. call getter function)

    # check connection with Ethereum node
    try:
        print("current blocknumber:", fullnode.eth.blockNumber)
        print("coinbase:", fullnode.eth.coinbase)
        fullnode.geth.miner.start(1)

        # temp code for demo
        # insert random user
        userAddr = generateRandomAddress()
        depositAmount = random.randint(1,300)
        washCountAmount = random.randint(1,3)
        tx_hash = sgbjContract.functions.addDeposit(depositAmount, userAddr).transact({'gas':GAS})
        tx_receipt = fullnode.eth.waitForTransactionReceipt(tx_hash)
        tx_hash = sgbjContract.functions.addWashCount(washCountAmount, userAddr).transact({'gas':GAS})
        tx_receipt = fullnode.eth.waitForTransactionReceipt(tx_hash)
    except:
        print("ERROR: cannot connect to Ethereum node. Start ethereum node first")
        sys.exit()
    
    # run backend server
    app.run(host=HOST, port=PORT)
