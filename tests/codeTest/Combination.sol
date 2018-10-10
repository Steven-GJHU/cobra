contract Test {
    mapping (address => uint) public credit;
    mapping (address => uint) public balances;

    struct Account {
        bytes32 name;  
        address mappedAddress;
    }

    struct Test {
        bytes32 test;
        address testAddr;
    }

    function withdrawMoney(uint256 _weiToWithdraw) public {
        require(_weiToWithdraw <= balance[msg.sender]);
        require(msg.sender.call.value(_weiToWithdraw)());
        balances[msg.sender] -= _weiToWithdraw;
    }

    function transferFrom(address _from, address to, uint256 _value) public {
        balance[_to] += _value;
        // assert(balance[_from] >= _value);
        // balance[_from] -= _value;
        allowed[_from][msg.sender] *= _value;
        assert(allowed[_from][msg.sender] >= _value);
    }

    function register(bytes32 _name, address _mappedAddress) public {
        Account newAccount;
        newAccount.name = _name;
        newAccount.mappedAddress = _mappedAddress; 

        resolve[_name] = _mappedAddress;
        registeredNameRecord[msg.sender] = newAccount;
    }

    function Test(address _owner) public {
        owner = _owner;
    } 

    function withdrawEther(address _addr) public {
        require (tx.origin == owner);
        addr.transfer(this.balance);
    }
    
    function donate(uint amount) public {
        credit[msg.sender] += amount;
        // assert(credit[msg.sender] >= amount);
    }
    
    function queryCredit(address to) public returns (uint) {
        // return credit[to];
    }

    function overflow() public {

        uint a = 0, b = 2, balance;

        assert(a >= b);
        int d = a - b;


        uint c = a + b;
        //assert(c > a);

        a = c * b;
        //assert(b == 0 || c == a / b );

        c = 1 + 2;
        //assert(c > 1);

        //assert(5 > 2);
        b = 5 - 2;

        a = 4 * 3;
        balance += a;
        //assert(4 == 0 || 3 == a / 4);

        uint a = 1;
        uint b = 1;

        assert(c >= a);
        uint c = a + b;

        uint d = b - a;
        assert(a <= b);

        assert(0 == a || e / a == b);
        uint e = a * b;
    }

    function donateToSimpleDAO(uint amount) public {
        address(dao).call.value(amount)(bytes4(sha3("donate(uint256)")),amount);
    }

    function withdraw(uint amount) public {
        msg.sender.send(amount);
        if (credit[msg.sender]>= amount) {
            credit[msg.sender] -= amount*10**18;
            if (!msg.sender.call.value(amount*10**18)()) {
                suicide(msg.sender);
                throw;
            }
        }
    }
    
    function checkBalance() public returns (uint) {
        return address(this).balance;
    }

    function oddOrEven(bool yourGuess) external payable returns (bool) {

        // uint now = 1;

        if (yourGuess == now % 2 > 0) {
          uint fee = msg.value / 10;
          msg.sender.transfer(msg.value * 2 - fee);
        }
    }

    function ()  {
        // dont receive ether via fallback
    }

}

contract ForTest{
    function ForTest(address _owner) public {
        owner = _owner;
    }
}
