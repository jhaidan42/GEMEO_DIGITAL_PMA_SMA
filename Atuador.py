from flask import request, jsonify
from flask_restful import Resource
from opcua import Server
import requests
import json
import time

#Classe que define os atributos e métodos do OperadorHumano (Conforme diagrama de classes)
class Atuador:
    def __init__(self, nomeAgente, idAgente):
        self.idAgente = idAgente
        self.nomeAgente = nomeAgente
        self.agenteFonte = {}
        self.urlFonte = ""
        self.dadosInformar = {}
        self.nomeServidorOPCUA = f"{nomeAgente}_ServidorOPCUA"
 
    def receberDados(self):
        response = requests.post(url = self.urlFonte, json = self.agenteFonte)
        if response.status_code == 200:
        # A resposta da API está no formato JSON
            data = response.json()
            return data
        else:
            print('Falha ao obter a variável da API')

    def disponibilizarDadosAPI(self):
        with open(f'{self.nomeAgente}.json', 'w') as file:
            json.dump(self.dadosInformar, file)

        print(f'\nPredicao do agente {self.nomeAgente} disponivel na rota da API: {self.dadosInformar}\n')
    
    def disponibilizarDadosOPCUA(self, tempo):
        
        # Criar o servidor OPC UA
        servidorOPCUA = Server()
        uri = "http://example.com"
        servidorOPCUA.set_endpoint("opc.tcp://localhost:4840")
        servidorOPCUA.set_server_name(self.nomeServidorOPCUA)
            
        # Criar um objeto de nó 
        addspace = servidorOPCUA.register_namespace(uri)
        node = servidorOPCUA.get_objects_node()
        obj_variaveis = node.add_object(addspace, f"objeto{self.nomeAgente}")
        obj_variaveis.add_variable(addspace, list(self.dadosInformar.keys())[0], list(self.dadosInformar.values())[0])

        # Exibir os números de namespace e strings de identificação
        print(f"Número de namespace (ns): {addspace}, String de identificação (s): {uri}")
        
        if tempo != 'continuo':
            servidorOPCUA.start()
            print("Servidor OPC UA iniciado!")
            time.sleep(tempo)
            servidorOPCUA.stop()
            print("Servidor OPC UA encerrado!")

        elif tempo == 'continuo':     
            servidorOPCUA.start()
            print("Servidor OPC UA iniciado!")

            servidorOPCUA.stop()
            print("Servidor OPC UA encerrado!")

#Classe que estabelece uma rota de API para cada Agente
class AtuadorAPI(Resource):    
    def post(self):
        nomeAgente = request.json['nomeAgente']
        
        with open(f'{nomeAgente}.json', 'r') as file:
            data = json.load(file)
        return jsonify(data)


        