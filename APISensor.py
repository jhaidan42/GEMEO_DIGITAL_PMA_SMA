from Sensor import SensorAPI
from flask import Flask
from flask_restful import Api

app = Flask(__name__)
api = Api(app)

api.add_resource(SensorAPI, '/sensor')

if __name__ == '__main__':
	app.run(host='192.168.3.115', port=5003)