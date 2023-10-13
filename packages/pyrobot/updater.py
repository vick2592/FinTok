import os
from web3 import Web3
from cache import Cache
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Access environment variables
api_key = os.environ['NEXT_PUBLIC_INFURA_API_KEY']

def fetch_ethereum_price_chainlink_nodes():
    # Connect to an Ethereum node. You can use services like Infura, or use a local Ethereum node.
    w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/{}".format(api_key)))

    # Chainlink ETH/USD price feed address
    price_feed_address = '0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419'  # Update this if the address changes

    # ABI for the price feed contract
    abi = [{"inputs": [],"name": "latestRoundData","outputs": [{"internalType": "uint80","name": "roundId","type": "uint80"},{"internalType": "int256","name": "answer","type": "int256"},{"internalType": "uint256","name": "startedAt","type": "uint256"},{"internalType": "uint256","name": "updatedAt","type": "uint256"},{"internalType": "uint80","name": "answeredInRound","type": "uint80"}],"stateMutability": "view","type": "function"}]

    # Create a contract object
    contract = w3.eth.contract(address=price_feed_address, abi=abi)

    # Fetch the latest round data
    latest_round_data = contract.functions.latestRoundData().call()

    # The 'answer' field in the data is the price, but it's not in a human-friendly format
    raw_price = latest_round_data[1]

    # Convert the raw price to a human-friendly format
    price = raw_price / 10**8  # Change the exponent according to the contract's decimal configuration

    return price

def fetch_bitfinex_candlestick_data(symbol, timeframe, limit):
    base_url = 'https://api.bitfinex.com/v2'
    endpoint = f'/candles/trade:{timeframe}:{symbol}/hist?limit={limit}'
    url = base_url + endpoint

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        # Data format: [[MTS, OPEN, CLOSE, HIGH, LOW, VOLUME], ...]
        return data
    else:
        print(f"Failed to fetch Bitfinex data. Status code: {response.status_code}")
        return None

cache = Cache()

def start_updates():
    eth_price_chainlink_nodes = fetch_ethereum_price_chainlink_nodes()
    symbol = 'tETHUSD'  # Example: Bitcoin/US Dollar
    timeframe = '1m'    # Example: 1 minute candlesticks
    limit = 1          # Example: Number of data points to retrieve
    candlestick_data = fetch_bitfinex_candlestick_data(symbol, timeframe, limit)
    
    if candlestick_data:
        open_prices = [candle[1] for candle in candlestick_data]
        high_prices = [candle[3] for candle in candlestick_data]
        low_prices = [candle[4] for candle in candlestick_data]
        close_prices = [candle[2] for candle in candlestick_data]

        print(f"Updated - Chainlink Price: {eth_price_chainlink_nodes}")
        print(f"Bitfinex Candlestick Data:")
        print(f"Open Prices: {open_prices}")
        print(f"High Prices: {high_prices}")
        print(f"Low Prices: {low_prices}")
        print(f"Close Prices: {close_prices}")

        cache.set('ETH_Price_Chainlink_Nodes', f'{eth_price_chainlink_nodes}')
    else:
        print(f"Failed to fetch Bitfinex candlestick data.")