/*import { useEffect, useState } from "react";*/
import Image from "next/image";
import Button from "../components/Button";
import fetch from "isomorphic-unfetch";
import type { NextPage } from "next";
import { useQuery } from "react-query";
import { AdjustmentsVerticalIcon } from "@heroicons/react/24/outline";
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
  const yourWidth = 500;
  const yourHeight = 500;

  return (
    <>
      <MetaHeader />
      <div className="flex items-center flex-col flex-grow pt-10">
        <div className="px-5">
          <h1 className="text-center mb-8">
            <span className="block text-3xl mb-2 font-bold">Welcome to FinTok</span>
            <span className="block text-2xl mb-2">The Worlds First Decentralized Trading Robot</span>
          </h1>
          <p className="text-center text-lg">
            Current ETH Price is{" "}
            <span className="italic bg-base-300 text-base font-bold max-w-full break-words break-all inline-block">
              $ {isLoading ? "Loading..." : isError ? "Error" : data?.ETH_Price_Chainlink_Nodes}
            </span>{" "}
            Powered by ChainLink.
          </p>
        </div>
        {/* Button to launch Trading Agent App */}
        <div className="btn traderbtn mt-8 text-center">
          <Button href="/agent">
            <div className="flex items-center">
              <AdjustmentsVerticalIcon className="h-6 w-6 ml-2" />
              <span className="ml-2">Launch Trading Agent</span>
            </div>
          </Button>
        </div>
        {/* Responsive GIF Image */}
        <div className="w-full max-w-4xl mt-5 sm:mt-16">
          <Image
            src="/assets/Trading.gif" // Adjust the path to match your directory structure
            alt="Trading GIF"
            width={yourWidth}
            height={yourHeight}
            className="w-full rounded-xl"
          />
        </div>
      </div>
    </>
  );
};

export default Home;
