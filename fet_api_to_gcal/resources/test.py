from flask_restful import Resource


class Test(Resource):
    def get(self):
        return "testing get"
    
    def post(self):
        return "testing post"


