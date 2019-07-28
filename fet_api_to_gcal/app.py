from flask import Flask
from flask_restful import Api
from fet_api_to_gcal.resources.test import Test

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
api = Api(app)


api.add_resource(Test, "/api/v1/test")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
    

