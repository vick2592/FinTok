// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../contracts/StakingRewards.sol";

contract StakingRewardsTest is Test {
    StakingRewards public stakingRewards;

    function setUp() public {
        // Deploy the StakingRewards contract
        stakingRewards = new StakingRewards(address(this), address(this));
    }

    function testStakeAndWithdraw() public {
        uint initialBalance = address(this).balance;
        uint depositAmount = 1 ether;

        // Stake tokens
        stakingRewards.stake(depositAmount);

        // Check total supply and staker's balance
        assertEq(stakingRewards.totalSupply(), depositAmount);
        assertEq(stakingRewards.balanceOf(address(this)), depositAmount);

        uint withdrawAmount = depositAmount / 2;

        // Withdraw tokens
        stakingRewards.withdraw(withdrawAmount);

        // Check total supply and staker's balance after withdrawal
        assertEq(stakingRewards.totalSupply(), depositAmount - withdrawAmount);
        assertEq(stakingRewards.balanceOf(address(this)), depositAmount - withdrawAmount);
    }

    function testRewardDistribution() public {
        // Assume you have set a rewards duration and notified reward amount

        uint rewardAmount = 1000; // Reward amount
        uint duration = 60; // Duration in seconds
        stakingRewards.setRewardsDuration(duration);
        stakingRewards.notifyRewardAmount(rewardAmount);

        // Check reward distribution and earned rewards
        stakingRewards.stake(1 ether); // Stake 1 ether
        stakingRewards.getReward(); // Claim rewards
        assertEq(stakingRewards.earned(address(this)), rewardAmount * 60 / 1 ether); // Verify earned rewards
    }
}