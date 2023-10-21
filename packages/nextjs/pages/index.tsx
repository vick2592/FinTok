/*import { useEffect, useState } from "react";*/
import Link from "next/link";
import fetch from "isomorphic-unfetch";
import type { NextPage } from "next";
import { useQuery } from "react-query";
import { BugAntIcon, MagnifyingGlassIcon, SparklesIcon } from "@heroicons/react/24/outline";
import { MetaHeader } from "~~/components/MetaHeader";

//const projectId = process.env.NEXT_PUBLIC_INFURA_API_KEY || "Create .env file in root directory and enter API key";

const Home: NextPage = () => {
  const fetchData = async () => {
    const response = await fetch("http://127.0.0.1:8080/api/ethereum_cpf/price");

    if (!response.ok) {
      throw new Error("Failed to fetch data");
    }

    return response.json();
  };
  const { data, isLoading, isError } = useQuery("ethereumPrice", fetchData, {
    staleTime: 60000, // Set the staleTime to 60,000 milliseconds (1 minute)
  });

  return (
    <>
      <MetaHeader />
      <div className="flex items-center flex-col flex-grow pt-10">
        <div className="px-5">
          <h1 className="text-center mb-8">
            <span className="block text-2xl mb-2 font-bold">Welcome to FinTok</span>
          </h1>
          <p className="text-center text-lg">
            Current ETH Price is{" "}
            <span className="italic bg-base-300 text-base font-bold max-w-full break-words break-all inline-block">
              {isLoading ? "Loading..." : isError ? "Error" : data?.ETH_Price_Chainlink_Nodes}
            </span>{" "}
            Powered by ChainLink.
          </p>
        </div>

        <div className="flex-grow bg-base-300 w-full mt-16 px-8 py-12">
          <div className="flex justify-center items-center gap-12 flex-col sm:flex-row">
            <div className="flex flex-col bg-base-100 px-10 py-10 text-center items-center max-w-xs rounded-3xl">
              <BugAntIcon className="h-8 w-8 fill-secondary" />
              <p>
                Tinker with your smart contract using the{" "}
                <Link href="/debug" passHref className="link">
                  Debug Contract
                </Link>{" "}
                tab.
              </p>
            </div>
            <div className="flex flex-col bg-base-100 px-10 py-10 text-center items-center max-w-xs rounded-3xl">
              <MagnifyingGlassIcon className="h-8 w-8 fill-secondary" />
              <p>
                Explore your local transactions with the{" "}
                <Link href="/blockexplorer" passHref className="link">
                  Block Explorer
                </Link>{" "}
                tab.
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Home;
