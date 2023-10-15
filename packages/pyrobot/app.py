from flask import Flask
from flask_socketio import SocketIO
from apscheduler.schedulers.background import BackgroundScheduler
from routes import APIRoutes
from cache import Cache
from updater import start_updates_cle

# Initialize app and other global resources
app = Flask(__name__)
socketio = SocketIO(app)
cache = Cache()

# Initialize routes
api_routes = APIRoutes(app, socketio, cache)

# Initialize and start data updater
scheduler = BackgroundScheduler()
scheduler.add_job(start_updates_cle, 'interval', seconds=60)
scheduler.start()

if __name__ == "__main__":
    app.run(debug=True, port=8080, use_reloader=False)