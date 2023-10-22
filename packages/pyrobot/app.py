import os
import requests
import json
from flask import Flask
from flask_socketio import SocketIO
from apscheduler.schedulers.background import BackgroundScheduler
from routes import APIRoutes
from cache import Cache
from updater import get_price_feed
from collections import deque
import pandas as pd
import numpy as np
from train_test import CustomAgent, CustomEnv
from utils import Normalizing
from tensorflow.keras.optimizers import Adam
from indicators import *
from dotenv import load_dotenv
from web3 import Web3
from contracts_abi import UNISWAP_ROUTER_ABI
#from your_contract import YourContract  # Import your contract

# Load environment variables from .env file
load_dotenv()

wallet_private_key = os.environ['NEXT_PUBLIC_private_key']

# Initialize app and other global resources
app = Flask(__name__)
socketio = SocketIO(app)
cache = Cache()

# Initialize routes
api_routes = APIRoutes(app, socketio, cache)

#To get initial Chainlink Ethereum price and download Bitfinex Ethereum price
get_price_feed()

# Define the Ethereum network URL and Web3 instance
scroll_sepolia_node_url = "https://sepolia-rpc.scroll.io/"
w3 = Web3(Web3.HTTPProvider(scroll_sepolia_node_url))

# Set your private key and Ethereum wallet address via Environment variables
infura_api_key = os.environ['NEXT_PUBLIC_INFURA_API_KEY']
private_key = os.environ['DEPLOYER_PRIVATE_KEY']
wallet_address = os.environ['DEPLOYER_WALLET_ADDRESS']

# Define the Uniswap V4 router contract address and ABI
uniswap_router_address = "0x17AFD0263D6909Ba1F9a8EAC697f76532365Fb95"
uniswap_router_abi = UNISWAP_ROUTER_ABI  # Replace with the actual ABI
#print(uniswap_router_abi)

# Set GHO and ETH token addresses 
gho_token_address = "0xD9692f1748aFEe00FACE2da35242417dd05a8615"
eth_token_address = "0x5300000000000000000000000000000000000004"

# Define the amount and minimum amount for the swap
amount_gho_to_eth = 34.0  # Replace with the amount of GHO to swap to ETH
amount_eth_to_gho = 0.02  # Replace with the amount of ETH to swap to GHO
min_amount_gho_to_eth = 0.01  # Minimum amount of ETH you want to receive
min_amount_eth_to_gho = 14.0  # Minimum amount of GHO you want to receive

# Helper function to send Ethereum transactions
def send_ethereum_transaction(transaction):
    signed_transaction = w3.eth.account.signTransaction(transaction, private_key)
    tx_hash = w3.eth.sendRawTransaction(signed_transaction.rawTransaction)
    return tx_hash

# Action 1: Swap GHO to ETH
def action_1():
    gwei_price = 20  # Replace with your desired gas price in Gwei
    gas_price_in_wei = int(gwei_price * 1e9)  # 1 Gwei = 1e9 Wei
    scroll_sepolia_node_url = "https://sepolia-rpc.scroll.io/"
    w3 = Web3(Web3.HTTPProvider(scroll_sepolia_node_url))
    print("Action 1: Swapping GHO to ETH")
    amount_in_wei = int(amount_gho_to_eth * 1e18)
    nonce = w3.eth.get_transaction_count(wallet_address)

    # Prepare the transaction data
    transaction = {
        "to": uniswap_router_address,
        "value": amount_in_wei,
        "gas": 2000000,
        "gasPrice": gas_price_in_wei,
        "nonce": nonce,
    }

    # Build the swap call to Uniswap V4 router
    uniswap_router_contract = w3.eth.contract(address=uniswap_router_address, abi=uniswap_router_abi)
    swap_function = uniswap_router_contract.functions.swapExactTokensForETH(
        amount_gho_to_eth * 1e18,
        min_amount_gho_to_eth * 1e18,
        [gho_token_address, eth_token_address],
        wallet_address,
        Web3.toWei(1800, 's'),  # Replace with your desired deadline
    )

    transaction['data'] = swap_function.encode_input()

    # Send the Ethereum transaction
    tx_hash = send_ethereum_transaction(transaction)
    print(f"Swap initiated. Transaction Hash: {tx_hash}")

# Action 2: Swap ETH to GHO (reverse swap)
def action_2():
    scroll_sepolia_node_url = "https://sepolia-rpc.scroll.io/"
    w3 = Web3(Web3.HTTPProvider(scroll_sepolia_node_url))
    gwei_price = 20  # Replace with your desired gas price in Gwei
    gas_price_in_wei = int(gwei_price * 1e9)  # 1 Gwei = 1e9 Wei
    print("Action 2: Swapping ETH to GHO")
    amount_in_wei = int(amount_eth_to_gho * 1e18)
    nonce = w3.eth.get_transaction_count(wallet_address)

    # Prepare the transaction data
    transaction = {
        "to": uniswap_router_address,
        "value": amount_in_wei,
        "gas": 2000000,
        "gasPrice": gas_price_in_wei,
        "nonce": nonce,
    }

    # Build the swap call to Uniswap V4 router (reverse swap)
    uniswap_router_contract = w3.eth.contract(address=uniswap_router_address, abi=uniswap_router_abi)
    swap_function = uniswap_router_contract.functions.swapExactETHForTokens(
        min_amount_eth_to_gho * 1e18,
        [eth_token_address, gho_token_address],
        wallet_address,
        Web3.toWei(1800, 's'),  # Replace with your desired deadline
    )

    transaction['data'] = swap_function.encode_input()

    # Send the Ethereum transaction
    tx_hash = send_ethereum_transaction(transaction)
    print(f"Swap initiated. Transaction Hash: {tx_hash}")

# Call the appropriate action based on your predictions
# For example:
# action_1()  # To swap GHO to ETH
# action_2()  # To swap ETH to GHO

# Function to make predictions
def make_predictions():
    # Get the current state from the test environment
    print("Making Prediction...")
    # Load the test dataset
    df = pd.read_csv('./ETHUSD_1h.csv')
   
    # Open the CSV file using the 'with open' statement
    # file_path = './ETHUSD_1h.csv'
    # with open(file_path, 'rb') as file:
    #     df = pd.read_csv(file)
    df = df.dropna()
    df = df.sort_values('Date')
    df = AddIndicators(df)
    depth = len(list(df.columns[1:]))
    test_df = df[-100:]  # Assuming you want to predict on the last 100 rows for testing
    df_nomalized = Normalizing(df[99:])[1:].dropna()
    # Initialize the environment with the test dataset
    test_env = CustomEnv(df=test_df, df_normalized=df_nomalized, lookback_window_size=100)

    agent = CustomAgent(lookback_window_size=100, lr=0.00001, epochs=5, optimizer=Adam, batch_size=32, model="CNN", depth=depth, comment="Normalized")
    agent.load(folder="2023_10_17_22_07_Crypto_trader", name="1061.05_Crypto_trader")
    state = test_env.reset()

    # Make predictions using the trained agent
    action, prediction = agent.act(state)

    # Perform action (buy/sell/hold) based on the agent's prediction
    if action == 1:
        print("Buying 0.02 ETH")
        action_1()

    elif action == 2:
        print("Selling 0.02 ETH")
        action_2()

    else:
        # Hold (do nothing)
        print("Holding. No action taken.")

    # Print or use the action and prediction
    print(f"Action: {action}, Prediction: {prediction}")

# Call the function to make predictions
#make_predictions()
# time.sleep(20)
# print(" make prediction 2 " )
# make_predictions()

# Initialize and start data updater
scheduler = BackgroundScheduler()
scheduler.add_job(get_price_feed, 'interval', seconds=1800) # do 3600 every hour but for testing let it run every minute
scheduler.add_job(make_predictions, 'interval', seconds=150) # Run every hour put hours=1
scheduler.start()

if __name__ == "__main__":
    app.run(debug=True, port=8080, use_reloader=False)