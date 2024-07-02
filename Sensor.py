from opcua import Client, Server
from flask import request, jsonify
from flask_restful import Resource
import json
import time

#Classe que define os atributos e métodos do Sensor (Conforme diagrama de classes)
class Sensor:
    def __init__(self, nomeAgente, idAgente):
        self.idAgente = idAgente
        self.nomeAgente = nomeAgente
        self.dadosInformar = {}
        self.nodeIdOPCUA = {}
        self.urlFonteOPCUA = {}
        self.nomeServidorOPCUA = f"{nomeAgente}_ServidorOPCUA"
 
    def lerDados(self, nomeFonte):
        # Cria um cliente OPC UA
        client = Client(self.urlFonteOPCUA[nomeFonte])
        # Conectar ao servidor
        client.connect()
        # Acessa a variável do servidor
        noh = client.get_node(self.nodeIdOPCUA[nomeFonte])
        # Lê o nome da variável
        try:
            nomeVariavel = noh.get_description().Text
        except Exception as e: 
            nomeVariavel = self.nodeIdOPCUA[nomeFonte]    

        # Lê o valor da variável
        valor = noh.get_value()  
        # Desconectar do servidor
        client.disconnect()
        return {nomeVariavel:valor}

    def disponibilizarDadosAPI(self):
        with open(f'{self.nomeAgente}.json', 'w') as file:
            json.dump(self.dadosInformar, file)

        print(f'\nDado a informar, do agente {self.nomeAgente}, disponivel na rota da API:: {self.dadosInformar}\n')
    
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
        print(f"\nNúmero de namespace (ns): {addspace}, String de identificação (s): {uri}\n")
        
        if tempo != 'continuo':
            servidorOPCUA.start()
            print("Servidor OPC UA iniciado!\n")
            time.sleep(tempo)
            servidorOPCUA.stop()
            print("Servidor OPC UA encerrado!\n")

        elif tempo == 'continuo':     
            servidorOPCUA.start()
            print("Servidor OPC UA iniciado!\n")

            servidorOPCUA.stop()
            print("Servidor OPC UA encerrado!\n")

#Classe que estabelece uma rota de API para cada Agente
class SensorAPI(Resource):    
    def post(self):
        nomeAgente = request.json['nomeAgente']
        
        with open(f'{nomeAgente}.json', 'r') as file:
            data = json.load(file)
        return jsonify(data)