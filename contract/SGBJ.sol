pragma solidity ^0.5.1;
// EVM VERSION = byzantium

contract SGBJ {
    address [] public users;
    mapping (address => uint256) public usersBalance;
    mapping (address => uint256) public usersWashCount;
    
    uint256 public userCount;
    uint256 public balanceSum;
    uint256 public washCountSum;
    uint256 public lottoEpoch;
    uint256 public interestRate;
    uint256 public roundNumber;
    
    // last round's
    address [] public depositWinners;
    address [] public washCountWinners;
    uint256 [] public winningsAmount;   // winning prize amount
    
    constructor() public {
        lottoEpoch = 3;
        interestRate = 10; // 10%
        
        greeting = "hello";
    }
    
    function setEpoch(uint256 newLottoEpoch) public {
        lottoEpoch = newLottoEpoch;
    }
    
    function addDeposit(uint256 amount, address userAddr) public {
        usersBalance[userAddr] += amount;
        balanceSum += amount;
        
        // add user to the list
        for (uint i=0; i<users.length; i++){
            if (users[i] == userAddr){
                return;
            }
        }
        users.push(userAddr);
        userCount++;
    }
    
    function withdrawDeposit(uint256 amount, address userAddr) public {
        assert(usersBalance[userAddr] >= amount);
        usersBalance[userAddr] -= amount;
        balanceSum -= amount;
    }
    
    function addWashCount(uint256 amount, address userAddr) public {
        usersWashCount[userAddr] += amount;
        washCountSum += amount;
        
        // add user to the list
        for (uint i=0; i<users.length; i++){
            if (users[i] == userAddr){
                return;
            }
        }
        users.push(userAddr);
        userCount++;
    }
    
    function getRandomNumber(uint256 upperBound) pure internal returns (uint256) {
        return upperBound/2;
    }
    
    function selectWinner() public returns (address, address){
        // assert(block.number % lottoEpoch == 0);
        
        // select deposit winner
        uint256 luckyNumber = getRandomNumber(balanceSum);
        address depositWinner = users[users.length-1];
        for(uint i=0; i<users.length; i++) {
            if(luckyNumber > usersBalance[users[i]]) {
                luckyNumber -= usersBalance[users[i]];
            }
            else {
                depositWinner = users[i];
                break;
            }
        }
        
        // select washCount winner
        luckyNumber = getRandomNumber(washCountSum);
        address washCountWinner = users[users.length-1];
        for(uint i=0; i<users.length; i++) {
            if(luckyNumber > usersWashCount[users[i]]) {
                luckyNumber -= usersWashCount[users[i]];
            }
            else {
                washCountWinner = users[i];
            }
            
            // initialize wash count for next round
            usersWashCount[users[i]] = 0;
        }
        washCountSum = 0;
        
        // calculate winning prize amount = sum of interest
        uint256 prizeAmount = balanceSum;
        for (uint256 i=0; i< lottoEpoch; i++){
            prizeAmount *= (100 + interestRate);
            prizeAmount /= 100;
        }
        prizeAmount -= balanceSum;
        
        // give winnings to winners
        usersBalance[depositWinner] += prizeAmount/2;
        usersBalance[washCountWinner] += prizeAmount - prizeAmount/2;
        balanceSum += prizeAmount;
        
        // logging winners
        depositWinners.push(depositWinner);
        washCountWinners.push(washCountWinner);
        winningsAmount.push(prizeAmount);
        
        // start next round
        roundNumber += 1;
        
        // return winners' address
        return (depositWinner, washCountWinner);
    }
    
    
    
    
    
    // codes for debugging
    
    string public greeting;
    
    function setGreeting(string memory newGreeting) public {
        greeting = newGreeting;
    }
    
    function greet() public view returns (string memory) {
        return greeting;
    }
    
    
}
