from Gerenciador import GerenciadorAPI
from flask import Flask
from flask_restful import Api

app = Flask(__name__)
api = Api(app)

api.add_resource(GerenciadorAPI, '/gerenciador')

if __name__ == '__main__':
	app.run(host='192.168.3.115', port=5002)