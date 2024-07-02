from flask import request, jsonify
from flask_restful import Resource
from opcua import Client, Server, ua
import requests
import json
import time

#Classe que define os atributos e métodos do Gerenciador (Conforme diagrama de classes)
class Gerenciador:
    def __init__(self, nomeAgente, idAgente):
        self.idAgente = idAgente
        self.nomeAgente = nomeAgente
        self.agentesFonte = {}
        self.urlsFonte = {}
        self.dadosInformar = {}
        self.nomeServidorOPCUA = f"{nomeAgente}_ServidorOPCUA"
 
    def receberDados(self, agenteFonte, classeFonte):
        response = requests.post(url = self.urlsFonte[classeFonte], json = self.agentesFonte[agenteFonte])
        if response.status_code == 200:
        # A resposta da API está no formato JSON
            data = response.json()
            return data
        else:
            print('Falha ao obter a variável da API!\n')

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
        print(f"Número de namespace (ns): {addspace}, String de identificação (s): {uri}\n")
        
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

    def alterarVariavel(self, nomeFonte, nodeId, nomeVariavel):
        # Cria um cliente OPC UA
        client = Client(self.urlsFonte[nomeFonte])
        # Conectar ao servidor
        client.connect()
        # Acessa a variável do servidor
        noh = client.get_node(nodeId)
        valorAlterar = list(self.dadosInformar[nomeVariavel].values())[0]
        if type(valorAlterar) == bool:
            client_node_dv = ua.DataValue(ua.Variant(valorAlterar, ua.VariantType.Boolean))
        else:
            client_node_dv = ua.DataValue(ua.Variant(valorAlterar, ua.VariantType.Int16))
        #Altera o valor da variável
        noh.set_value(client_node_dv)
        # Desconectar do servidor
        client.disconnect()

#Classe que estabelece uma rota de API para cada Agente
class GerenciadorAPI(Resource):    
    def post(self):
        nomeAgente = request.json['nomeAgente']
        #idAgente = request.json['idAgente']
        
        with open(f'{nomeAgente}.json', 'r') as file:
            data = json.load(file)
        return jsonify(data)


        