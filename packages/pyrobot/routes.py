from flask import jsonify, request
from flask_cors import CORS

class APIRoutes:

    def __init__(self, app, socketio, cache):
        self.app = app
        CORS(self.app)
        self.socketio = socketio
        self.cache = cache
        self.register_routes()

    def register_routes(self):
        @self.app.route('/api/ethereum_cpf/price', methods=['GET'])
        def get_ethereum_cpf_price():
            print(self.cache.get('ETH_Price_Chainlink_Nodes'))
            return jsonify({"ETH_Price_Chainlink_Nodes": self.cache.get('ETH_Price_Chainlink_Nodes')})

        # More routes...
