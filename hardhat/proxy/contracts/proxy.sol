// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

abstract contract Bank {
    IERC20 public underlying;
    mapping(address => uint256) public _balances;

    event Deposit(address indexed account, uint256 amount);
    event Withdraw(address indexed account, uint256 amount);
    event Received(address caller, uint256 amount, string message);

    function deposit(uint256 amount) external virtual;

    function withdraw(uint256 amount) external virtual;
}

contract CoinBank is Bank {
    using SafeERC20 for IERC20;
    using SafeMath for uint256;

    fallback() external {
        emit Received(msg.sender, 0, "CoinBank Fallback was called");
    }

    function deposit(uint256 amount) external override {
        require(amount > 0, "too less to deposit");
        underlying.safeTransferFrom(msg.sender, address(this), amount);
        _balances[msg.sender] = _balances[msg.sender].add(amount);
        emit Deposit(msg.sender, amount);
    }

    function withdraw(uint256 amount) external override {
        require(amount <= _balances[msg.sender], "too big to withdraw");
        underlying.safeTransfer(msg.sender, amount);
        _balances[msg.sender] = _balances[msg.sender].sub(amount);
        emit Withdraw(msg.sender, amount);
    }
}

contract CoinbankHalf is Bank {
    using SafeERC20 for IERC20;
    using SafeMath for uint256;

    fallback() external {
        emit Received(msg.sender, 0, "CoinBank Half Fallback was called");
    }

    function deposit(uint256 amount) external override {
        require(amount > 0, "too less to deposit");
        underlying.safeTransferFrom(msg.sender, address(this), amount.div(2));
        _balances[msg.sender] = _balances[msg.sender].add(amount);
        emit Deposit(msg.sender, amount);
    }

    function withdraw(uint256 amount) external override {
        require(amount <= _balances[msg.sender], "too big to withdraw");
        underlying.safeTransfer(msg.sender, amount.div(2));
        _balances[msg.sender] = _balances[msg.sender].sub(amount);
        emit Withdraw(msg.sender, amount);
    }
}

contract PiggyBank is Bank {
    address public coinbank;

    constructor(address bank, address asset) {
        coinbank = bank;
        underlying = IERC20(asset);
    }

    function setBank(address bank) external {
        coinbank = bank;
    }

    function callDeposit(uint256 amount) external {
        //return coinbank.call(bytes4(keccak256("deposit(uint256)")), amount);
        //(bool success, bytes memory data) = coinbank.call(
        (bool success, ) = coinbank.call(
            abi.encodeWithSignature("deposit(uint256)", amount)
        );
        require(success, "call failed");
    }

    function deposit(uint256 amount) external override {
        (bool success, ) = coinbank.delegatecall(
            abi.encodeWithSignature("deposit(uint256)", amount)
        );
        require(success, "delegatecall failed");
    }

    function callWithdraw(uint256 amount) external {
        (bool success, ) = coinbank.call(
            abi.encodeWithSignature("withdraw(uint256)", amount)
        );
        require(success, "call failed");
    }

    function withdraw(uint256 amount) external override {
        (bool success, ) = coinbank.delegatecall(
            abi.encodeWithSignature("withdraw(uint256)", amount)
        );
        require(success, "delegatecall failed");
    }
}
