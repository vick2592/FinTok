import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
api_key = os.environ['NEXT_PUBLIC_INFURA_API_KEY'] 

if __name__ == "__main__":
    print("API key is: ", api_key)
    #app.run(debug=True, port=8080, use_reloader=False)