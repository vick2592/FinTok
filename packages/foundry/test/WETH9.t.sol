// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../contracts/WETH9.sol";

contract WETH9Test is Test {
    WETH9 public wETH9;

    function setUp() public {
        wETH9 = new WETH9();
    }

    function testDepositAndWithdraw() public {
        uint initialBalance = address(this).balance;
        uint depositAmount = 1 ether;

        // Deposit
        wETH9.deposit{value: depositAmount}();
        
        // Check balance and WETH9 balance
        assertEq(address(this).balance, initialBalance - depositAmount);
        assertEq(wETH9.balanceOf(address(this)), depositAmount);

        uint withdrawAmount = depositAmount / 2;

        // Withdraw
        wETH9.withdraw(withdrawAmount);

        // Check balance and WETH9 balance after withdrawal
        assertEq(address(this).balance, initialBalance - depositAmount + withdrawAmount);
        assertEq(wETH9.balanceOf(address(this)), depositAmount - withdrawAmount);
    }
}
