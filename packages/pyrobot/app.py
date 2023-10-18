from flask import Flask
from flask_socketio import SocketIO
from apscheduler.schedulers.background import BackgroundScheduler
from routes import APIRoutes
from cache import Cache
from updater import start_updates_cle, start_updates_bfe
from train_test import CustomAgent, CustomEnv
import pandas as pd
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

# Create a global variable for your trained agent
df = pd.read_csv('./ETHUSD_1h.csv')
df = df.dropna()
df = df.sort_values('Date')

df = AddIndicators(df) # insert indicators to df 2021_02_21_17_54_Crypto_trader
#df = indicators_dataframe(df, threshold=0.5, plot=False) # insert indicators to df 2021_02_18_21_48_Crypto_trader
depth = len(list(df.columns[1:])) # OHCL + indicators without Date
trained_agent = CustomAgent(lookback_window_size=100, lr=0.00001, epochs=5, optimizer=Adam, batch_size=32, model="CNN", depth=depth, comment="Normalized")

# Create a function to load the trained model and make predictions
def make_predictions():
    global trained_agent
    # Load the trained model weights (you may need to provide the correct paths)
    trained_agent.load(folder="2023_10_17_22_07_Crypto_trader", name="1061.05_Crypto_trader")
    
# Function to fetch the current state from the CSV file
    def fetch_hourly_ETH_price_data():
        try:
            # Load the CSV file containing hourly ETH price data
            df = pd.read_csv('./ETHUSD_1h.csv')

            # Get the most recent data point (last row)
            current_state = df.iloc[-1].to_numpy()  # Assumes your data is in a suitable format

            # Optionally, you can pre-process the data to fit your state representation

            return current_state
        except Exception as e:
            print(f"Error fetching current state: {str(e)}")
            return None
        

    
    # Get the current state from your data source (hourly data)
    current_state = fetch_hourly_ETH_price_data()  # Fetch the current state from your data source
    current_state = current_state.reshape(1, 1, 6)
    
    if current_state is not None:
    # Use the current state for making predictions
        action, prediction = trained_agent.act(current_state)
        print(f"Action: {action}, Prediction: {prediction}")
    else:
        print("Error fetching current state")

#Test is make_predictions() works
make_predictions()

# Initialize and start data updater
scheduler = BackgroundScheduler()
scheduler.add_job(start_updates_cle, 'interval', seconds=60)
scheduler.add_job(start_updates_bfe, 'interval', seconds=60) # do 3600 every hour but for testing let it run every minute
scheduler.add_job(make_predictions, 'interval', hours=1)  # Run every hour
scheduler.start()

if __name__ == "__main__":
    app.run(debug=True, port=8080, use_reloader=False)