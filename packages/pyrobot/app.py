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
from contracts_abi import UNISWAP_ROUTER_ABI, UNISWAP_POOL_ABI
import time
from eth_abi.packed import encode_packed

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
chain_id = 534351

# Set your private key and Ethereum wallet address via Environment variables
infura_api_key = os.environ['NEXT_PUBLIC_INFURA_API_KEY']
private_key = os.environ['DEPLOYER_PRIVATE_KEY']
wallet_address = os.environ['DEPLOYER_WALLET_ADDRESS']

# Define the Uniswap V4 router contract address and ABI
uniswap_router_address = "0x17AFD0263D6909Ba1F9a8EAC697f76532365Fb95"
#uniswap_router_abi = UNISWAP_ROUTER_ABI  # Replace with the actual ABI
#uniswap_pool_address = "0xB856587fe1cbA8600F75F1b1176E44250B11C788"
#uniswap_pool_abi = UNISWAP_POOL_ABI  # Replace with the actual ABI
#print(uniswap_router_abi)

# Set GHO and ETH token addresses 
gho_token_address = "0xD9692f1748aFEe00FACE2da35242417dd05a8615"
#Regular ETH below
eth_token_address = "0x5300000000000000000000000000000000000004"
#Wrapped ETH below
#eth_token_address = "0x9Fe9B02e3b3ec6642FB308b2CDD4574dCc761C91"

# Define the amount and minimum amount for the swap
amount_gho_to_eth = 34  # Replace with the amount of GHO to swap to ETH
amount_eth_to_gho = 0.02 # Replace with the amount of ETH to swap to GHO
min_amount_gho_to_eth = 0.01  # Minimum amount of ETH you want to receive
min_amount_eth_to_gho = 14.0  # Minimum amount of GHO you want to receive

# Action 1: Swap GHO to ETH
def action_1():
    gwei_price = 20  # Replace with your desired gas price in Gwei
    gas_price_in_wei = int(gwei_price * 1e9)  # 1 Gwei = 1e9 Wei
    nonce = w3.eth.get_transaction_count(wallet_address)
    print("Action 1: Swapping GHO to ETH")

    # Define the parameters for the swap
    amount_in = int(amount_gho_to_eth * 1e18)  # Amount of GHO to swap (in wei)
    amount_out_min = int(min_amount_gho_to_eth * 1e18)  # Minimum amount of ETH to receive (in wei)
    swap_path = [gho_token_address, eth_token_address]  # Define the token swap path as a list
    recipient_address = wallet_address  # Address to receive the swapped ETH
    amount_in_wei = int(amount_gho_to_eth * 1e18)

    # Construct the deadline
    minutes_in_future = 10
    current_time = int(time.time())  # Get the current Unix timestamp
    deadline = current_time + (minutes_in_future * 60)  # Add seconds to the current time

    # Create the transaction data
    transaction = {
        "from": wallet_address,
        "to": uniswap_router_address,
        "value": amount_in_wei,
        "gas": 2000000,
        "gasPrice": gas_price_in_wei,
        "nonce": nonce,
        "data": encode_packed(
            ['uint256', 'uint256', 'address[]', 'address', 'uint256'],
            [amount_in, amount_out_min, swap_path, recipient_address, deadline]
        ),
        "chainId": chain_id
    }

    # Sign and send the Ethereum transaction
    signed_transaction = w3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    transaction_hash_bytes = tx_hash
    transaction_hash_hex = transaction_hash_bytes.hex()
    transaction_hash_0x = transaction_hash_hex

    print(f"Swap initiated. Transaction Hash: {transaction_hash_0x}")

# Action 2: Swap ETH to GHO
def action_2():
    gwei_price = 20  # Replace with your desired gas price in Gwei
    gas_price_in_wei = int(gwei_price * 1e9)  # 1 Gwei = 1e9 Wei
    nonce = w3.eth.get_transaction_count(wallet_address)
    print("Action 2: Swapping ETH to GHO")

    # Define the parameters for the swap
    amount_in = int(amount_eth_to_gho * 1e18)  # Amount of GHO to swap (in wei)
    amount_out_min = int(min_amount_eth_to_gho * 1e18)  # Minimum amount of ETH to receive (in wei)
    swap_path = [eth_token_address, gho_token_address]  # Define the token swap path as a list
    recipient_address = wallet_address  # Address to receive the swapped ETH
    amount_in_wei = int(amount_eth_to_gho * 1e18)

    # Construct the deadline
    minutes_in_future = 10
    current_time = int(time.time())  # Get the current Unix timestamp
    deadline = current_time + (minutes_in_future * 60)  # Add seconds to the current time

    # Create the transaction data
    transaction = {
        "from": wallet_address,
        "to": uniswap_router_address,
        "value": amount_in_wei,
        "gas": 2000000,
        "gasPrice": gas_price_in_wei,
        "nonce": nonce,
        "data": encode_packed(
            ['uint256', 'uint256', 'address[]', 'address', 'uint256'],
            [amount_in, amount_out_min, swap_path, recipient_address, deadline]
        ),
        "chainId": chain_id
    }

    # Sign and send the Ethereum transaction
    signed_transaction = w3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    transaction_hash_bytes = tx_hash
    transaction_hash_hex = transaction_hash_bytes.hex()
    transaction_hash_0x = transaction_hash_hex

    print(f"Swap initiated. Transaction Hash: {transaction_hash_0x}")

# Call the appropriate action based on your predictions
# For example:
# action_1()  # To swap GHO to ETH
# action_2()  # To swap ETH to GHO
# time.sleep(20)

# Function to make predictions
def make_predictions():
    # Get the current state from the test environment
    print("Making Prediction...")
    # Load the test dataset
    df = pd.read_csv('./ETHUSD_1h.csv')
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

# Initialize and start data updater
scheduler = BackgroundScheduler()
scheduler.add_job(get_price_feed, 'interval', seconds=1800) # do 3600 every hour but for testing let it run every minute
scheduler.add_job(make_predictions, 'interval', seconds=3600) # Run every hour put hours=1
scheduler.start()

if __name__ == "__main__":
    app.run(debug=True, port=8080, use_reloader=False)