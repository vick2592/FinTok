from flask import Flask
from flask_socketio import SocketIO
from apscheduler.schedulers.background import BackgroundScheduler
from routes import APIRoutes
from cache import Cache
from updater import start_updates_cle, start_updates_bfe
from collections import deque
import pandas as pd
import numpy as np
from train_test import CustomAgent, CustomEnv
from utils import TradingGraph, Write_to_file, Normalizing
from tensorflow.keras.optimizers import Adam
from indicators import *

# Initialize app and other global resources
app = Flask(__name__)
socketio = SocketIO(app)
cache = Cache()

# Initialize routes
api_routes = APIRoutes(app, socketio, cache)

#To get initial Chainlink Ethereum price
start_updates_cle()

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
    # Implement your logic here if needed

    # Print or use the action and prediction
    print(f"Action: {action}, Prediction: {prediction}")

# Call the function to make predictions
make_predictions()

# Initialize and start data updater
scheduler = BackgroundScheduler()
scheduler.add_job(start_updates_cle, 'interval', seconds=60)
scheduler.add_job(start_updates_bfe, 'interval', seconds=1800) # do 3600 every hour but for testing let it run every minute
scheduler.add_job(make_predictions, 'interval', seconds=60)  # Run every hour put hours=1
scheduler.start()

if __name__ == "__main__":
    app.run(debug=True, port=8080, use_reloader=False)