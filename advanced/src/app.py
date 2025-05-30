from flask import Flask
from config import Config
from data_manager import SportsData
from routes import api_routes, frontend_routes
import logging

app = Flask(__name__)
app.config.from_object(Config)

logging.basicConfig(filename='server.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

data_manager = SportsData(
    token=app.config['TOKEN'],
    base_url=app.config['BASE_API_URL'],
    cache_file=app.config['CACHE_FILE']
)

api_routes.register_routes(app, data_manager)
frontend_routes.register_routes(app, data_manager)

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=8000)
