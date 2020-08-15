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
# to get web3js contract employing code: https://remix.ethereum.org/ (CAUSION: need to setting evm version as "byzantium")
# put employ code to geth console & start mining => then we will get contract address
CONTRACTADDR = Web3.toChecksumAddress("0xb3c2a5B7c3297D3f08A8e22Dd2cE6D61E2d6C697")
# to get ABI of contract: https://remix.ethereum.org/
# to remove endline of abi: https://www.textfixer.com/tools/remove-line-breaks.php
abiString = '[ { "inputs": [], "payable": false, "stateMutability": "nonpayable", "type": "constructor" }, { "constant": false, "inputs": [ { "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "addDeposit", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "addWashCount", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [], "name": "balanceSum", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "name": "depositWinners", "outputs": [ { "internalType": "address", "name": "", "type": "address" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "greet", "outputs": [ { "internalType": "string", "name": "", "type": "string" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "greeting", "outputs": [ { "internalType": "string", "name": "", "type": "string" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "interestRate", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "lottoEpoch", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "roundNumber", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [], "name": "selectWinner", "outputs": [ { "internalType": "address", "name": "", "type": "address" }, { "internalType": "address", "name": "", "type": "address" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "uint256", "name": "newLottoEpoch", "type": "uint256" } ], "name": "setEpoch", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "string", "name": "newGreeting", "type": "string" } ], "name": "setGreeting", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "name": "users", "outputs": [ { "internalType": "address", "name": "", "type": "address" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "address", "name": "", "type": "address" } ], "name": "usersBalance", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "address", "name": "", "type": "address" } ], "name": "usersWashCount", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "washCountSum", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "name": "washCountWinners", "outputs": [ { "internalType": "address", "name": "", "type": "address" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "name": "winningsAmount", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "withdrawDeposit", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" } ]'
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
        
    elif functionName == "addDeposit":
        amount = param['amount']
        try:
            tx_hash = sgbjContract.functions.addDeposit(amount).transact({'gas':GAS})
            tx_receipt = fullnode.eth.waitForTransactionReceipt(tx_hash)
            response = {"result" : "success"}
            return jsonify(response)
        except:
            response = {"result" : "fail"}
            return jsonify(response)
            
    elif functionName == "subBalance":
        amount = param['amount']
        try:
            tx_hash = sgbjContract.functions.withdrawDeposit(amount).transact({'gas':GAS})
            tx_receipt = fullnode.eth.waitForTransactionReceipt(tx_hash)
            response = {"result" : "success"}
            return jsonify(response)
        except:
            response = {"result" : "fail"}
            return jsonify(response)
            
    elif functionName == "addWashCount":
        amount = param['amount']
        try:
            tx_hash = sgbjContract.functions.addWashCount(amount).transact({'gas':GAS})
            tx_receipt = fullnode.eth.waitForTransactionReceipt(tx_hash)
            response = {"result" : "success"}
            return jsonify(response)
        except:
            response = {"result" : "fail"}
            return jsonify(response)
    
    elif functionName == "selectWinner":
        try:
            tx_hash = sgbjContract.functions.selectWinner().transact({'gas':GAS})
            tx_receipt = fullnode.eth.waitForTransactionReceipt(tx_hash)
            response = {"result" : "success"}
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

    # test codes
    # function call & wait for the tx to be mined (with enough gas)
    # https://web3py.readthedocs.io/en/latest/contracts.html#web3.contract.ContractFunction.call

    # transact(): send transaction
    # call(): get contract state = not send transaction (ex. call getter function)

    # addWashCount()
    tx_hash = sgbjContract.functions.addWashCount(10).transact({'gas':GAS})
    tx_receipt = fullnode.eth.waitForTransactionReceipt(tx_hash)
    print(tx_receipt)

    # addDeposit()
    tx_hash = sgbjContract.functions.addDeposit(100).transact({'gas':GAS})
    tx_receipt = fullnode.eth.waitForTransactionReceipt(tx_hash)
    print(tx_receipt)

    # get the users washCount (getter function call)
    getWashCount = sgbjContract.functions.usersWashCount(fullnode.eth.coinbase).call()
    print(getWashCount)

    # selectWinner()
    tx_hash = sgbjContract.functions.selectWinner().transact({'gas':GAS})
    tx_receipt = fullnode.eth.waitForTransactionReceipt(tx_hash)
    print(tx_receipt)

    # get current round number (getter function call)
    roundNumber = sgbjContract.functions.roundNumber().call()
    print("current round:", roundNumber)

    # get the last rounds result
    depositWinner = sgbjContract.functions.depositWinners(roundNumber-1).call()
    washCountWinner = sgbjContract.functions.washCountWinners(roundNumber-1).call()
    winningPrizeAmount = sgbjContract.functions.winningsAmount(roundNumber-1).call()
    print("deposit winner:", depositWinner, "/ washCount winner:", washCountWinner, "/ winnings:", winningPrizeAmount, "ETH")

    # sys.exit()



    # run backend server
    try:
        print("current blocknumber:", fullnode.eth.blockNumber)
        print("coinbase:", fullnode.eth.coinbase)
    except:
        print("ERROR: cannot connect to Ethereum node. Start ethereum node first")
        sys.exit()
    
    app.run(host=HOST, port=PORT)
