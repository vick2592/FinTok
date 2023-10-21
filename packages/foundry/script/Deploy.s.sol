//SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "../contracts/WETH9.sol";
import "../contracts/StakingRewards.sol";
import "./DeployHelpers.s.sol";

contract DeployScript is ScaffoldETHDeploy {
    error InvalidPrivateKey(string);

    function run() external {
        uint256 deployerPrivateKey = setupLocalhostEnv();
        if (deployerPrivateKey == 0) {
            revert InvalidPrivateKey(
                "You don't have a deployer account. Make sure you have set DEPLOYER_PRIVATE_KEY in .env or use `yarn generate` to generate a new random account"
            );
        }
        vm.startBroadcast(deployerPrivateKey);

        // Deploy WETH9 contract
        WETH9 weth = new WETH9();
        console.logString(
            string.concat(
                "WETH9 deployed at: ",
                vm.toString(address(weth))
            )
        );

        // Deploy StakingRewards contract
        StakingRewards stakingRewards = new StakingRewards(
            vm.addr(deployerPrivateKey),
            address(weth)  // Use the address of the deployed WETH contract as the reward token
        );
        console.logString(
            string.concat(
                "StakingRewards deployed at: ",
                vm.toString(address(stakingRewards))
            )
        );

        vm.stopBroadcast();

        /**
         * This function generates the file containing the contracts Abi definitions.
         * These definitions are used to derive the types needed in the custom scaffold-eth hooks, for example.
         * This function should be called last.
         */
        exportDeployments();
    }

    function test() public {}
}