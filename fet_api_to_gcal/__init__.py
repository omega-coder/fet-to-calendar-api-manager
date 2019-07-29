from flask import Flask
from flask_cors import CORS
import fet_api_to_gcal.config

app = Flask(__name__)
app.config.from_object(config.DevelopmentConfig)
CORS(app)


from fet_api_to_gcal import routes