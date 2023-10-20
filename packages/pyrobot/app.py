import os
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
#from your_contract import YourContract  # Import your contract

# Load environment variables from .env file
load_dotenv()

# Access environment variables
infura_api_key = os.environ['NEXT_PUBLIC_INFURA_API_KEY']
wallet_private_key = os.environ['NEXT_PUBLIC_private_key']

print(infura_api_key, wallet_private_key)

# Initialize Web3 with your Ethereum node's URL (e.g., Infura)
#w3 = Web3(Web3.HTTPProvider("YOUR_ETHEREUM_NODE_URL"))

# Connect to your Ethereum wallet
#w3.eth.default_account = w3.toChecksumAddress("YOUR_WALLET_ADDRESS")

# Load your contract using its ABI and address
#contract_address = "YOUR_CONTRACT_ADDRESS"
#contract_abi = YourContract.abi

#contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Initialize app and other global resources
app = Flask(__name__)
socketio = SocketIO(app)
cache = Cache()

# Initialize routes
api_routes = APIRoutes(app, socketio, cache)

#To get initial Chainlink Ethereum price and download Bitfinex Ethereum price
get_price_feed()

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
        # Action 1: Swap Ethereum for USDC on Uniswap v4
        # Implement the swap logic here using Web3

        # Example: Swap 1 ETH for USDC
        # amount_in_wei = w3.toWei(1, "ether")
        # transaction = {
        #     "from": w3.eth.default_account,
        #     "to": contract_address,
        #     "value": amount_in_wei,
        #     "gas": 2000000,  # Adjust gas limit as needed
        #     "gasPrice": w3.toWei("20", "gwei"),  # Adjust gas price as needed
        #     "nonce": w3.eth.getTransactionCount(w3.eth.default_account),
        # }

        # signed_transaction = w3.eth.account.signTransaction(transaction, private_key)
        # tx_hash = w3.eth.sendRawTransaction(signed_transaction.rawTransaction)
        # w3.eth.waitForTransactionReceipt(tx_hash)

        # print(f"Swapped 1 ETH for USDC. Transaction Hash: {tx_hash}")

        print("buying ETH")

    elif action == 2:
        # Action 2: Swap USDC for Ethereum on Uniswap v4
        # Implement the swap logic here using Web3

        # Example: Swap 100 USDC for ETH
        #amount_in_wei = w3.toWei(100, "ether")
        # Your swap logic here

        print(f"Swapped 100 USDC for ETH. Transaction Hash: YOUR_TX_HASH")

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
scheduler.add_job(make_predictions, 'interval', seconds=20) # Run every hour put hours=1
scheduler.start()

if __name__ == "__main__":
    app.run(debug=True, port=8080, use_reloader=False)