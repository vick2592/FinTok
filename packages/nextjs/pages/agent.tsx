import { useState } from "react";
import type { NextPage } from "next";
import { useAccount } from "wagmi";
import { MetaHeader } from "~~/components/MetaHeader";
import { Address, AddressInput, EtherInput } from "~~/components/scaffold-eth";
import { useDeployedContractInfo, useScaffoldContractRead, useScaffoldContractWrite } from "~~/hooks/scaffold-eth";

const Agent: NextPage = () => {
  const { address } = useAccount();
  const [ethAmount, setEthAmount] = useState("");
  const [stakeAmount, setStakeAmount] = useState("");
  const [withdrawAmount, setWithdrawAmount] = useState("");
  const { data: deployedContractData } = useDeployedContractInfo("StakingRewards");
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const stakingAddress = deployedContractData?.address;

  const { data: balance } = useScaffoldContractRead({
    contractName: "WETH9",
    functionName: "balanceOf",
    args: [address],
  });

  const { data: stakedBalance } = useScaffoldContractRead({
    contractName: "StakingRewards",
    functionName: "balanceOf",
    args: [address],
  });

  const { writeAsync: deposit } = useScaffoldContractWrite({
    contractName: "WETH9",
    functionName: "deposit",
    value: BigInt(ethAmount * 10 ** 18),
  });

  const { writeAsync: approve } = useScaffoldContractWrite({
    contractName: "WETH9",
    functionName: "approve",
    args: [stakingAddress, balance],
  });

  const { writeAsync: stake } = useScaffoldContractWrite({
    contractName: "StakingRewards",
    functionName: "stake",
    args: [stakeAmount],
  });

  const { writeAsync: withdraw } = useScaffoldContractWrite({
    contractName: "StakingRewards",
    functionName: "withdraw",
    args: [withdrawAmount],
  });

  return (
    <>
      <MetaHeader title="Trading Agent" description="Trade with robot">
        {/* We are importing the font this way to lighten the size of SE2. */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link href="https://fonts.googleapis.com/css2?family=Bai+Jamjuree&display=swap" rel="stylesheet" />
      </MetaHeader>
      <div className="flex items-center flex-col flex-grow pt-10">
        <div className="card w-96 bg-base-100 shadow-xl">
          <div className="card-body">
            <h2 className="card-title">Deposit and Approve WETH</h2>
            <div className="p-2">
              Your Address: <Address address={address} />
            </div>
            <div className="p-2">
              WETH Balance: {balance !== undefined ? String(balance / BigInt(10 ** 18)) : "Loading..."} ETH
            </div>
            <div className="p-2">
              <EtherInput
                placeholder="Enter ETH or USD amount"
                value={ethAmount}
                onChange={amount => setEthAmount(amount)}
              />
            </div>
            <div className="mt-2 card-actions justify-center">
              <button
                className="w-full btn btn-primary"
                onClick={() => {
                  deposit();
                }}
              >
                Deposit Tokens
              </button>
            </div>
            <div className="mt-2 card-actions justify-end">
              <button
                className="w-full btn approvebtn"
                onClick={() => {
                  approve();
                }}
              >
                Approve Tokens
              </button>
            </div>
          </div>
        </div>
      </div>
      <div className="flex items-center flex-col flex-grow pt-10">
        <div className="card w-96 bg-base-100 shadow-xl">
          <div className="card-body">
            <h2 className="card-title">Stake to Trading Agent</h2>
            <div className="p-2">
              Staked Balance: {stakedBalance !== undefined ? String(stakedBalance / BigInt(10 ** 18)) : "Loading..."}{" "}
              ETH
            </div>
            <div className="p-1">
              <EtherInput
                placeholder="Enter ETH or USD amount"
                value={stakeAmount}
                onChange={amount => setStakeAmount(amount)}
              />
            </div>
            <div className="mt-2 card-actions justify-end">
              <button
                className="w-full btn btn-primary"
                onClick={() => {
                  stake();
                }}
              >
                Stake To Agent
              </button>
            </div>
            <h2 className="card-title">Withdraw from Trading Agent</h2>
            <div className="p-1">
              <EtherInput
                placeholder="Enter ETH or USD amount"
                value={withdrawAmount}
                onChange={amount => setWithdrawAmount(amount)}
              />
            </div>
            <div className="mt-2 card-actions justify-end">
              <button
                className="w-full btn traderbtn"
                onClick={() => {
                  withdraw();
                }}
              >
                Withdraw Rewards from Agent
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Agent;
