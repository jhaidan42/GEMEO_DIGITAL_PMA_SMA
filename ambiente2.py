from Gerenciador import Gerenciador
from Sensor import Sensor
import joblib
from datetime import datetime
import pandas as pd
import time
from inputimeout import inputimeout, TimeoutOccurred
import sys


#Função de obter a data do dia
def get_user_input(prompt, timeout):
   try:
      user_input = inputimeout(prompt=prompt, timeout=timeout)
      if user_input.lower() == 's':
         return True
      else:
         return None
   except TimeoutOccurred:
      return None

def obterDataDia():
    dataDia = pd.DataFrame({
    'DateTime':[datetime.today()],
    'Dia': '',
    'DiaDaSemana': '', 
    'Mes': '',
    'Ano': '',    
    'DiaDaSemana_0': [False],    
    'DiaDaSemana_1': [False],  
    'DiaDaSemana_2': [False],  
    'DiaDaSemana_3': [False],  
    'DiaDaSemana_4': [False],  
    'DiaDaSemana_5': [False],  
    'Mes_1': [False],   'Mes_2': [False],   'Mes_3': [False],   'Mes_4': [False],   'Mes_5': [False],   'Mes_6': [False],   
    'Mes_7': [False],   'Mes_8': [False],   'Mes_9': [False],   'Mes_10': [False],   'Mes_11': [False],   'Mes_12': [False],  
    })

    dataDia['DateTime'] = pd.to_datetime(dataDia['DateTime'])
    dataDia['Dia'] = dataDia['DateTime'].dt.day
    dataDia['DiaDaSemana'] = dataDia['DateTime'].dt.dayofweek
    dataDia['Mes'] = dataDia['DateTime'].dt.month
    dataDia['Ano'] = dataDia['DateTime'].dt.year

    weekday_dummies = pd.get_dummies(dataDia['DiaDaSemana'], prefix='DiaDaSemana')
    month_dummies = pd.get_dummies(dataDia['Mes'], prefix='Mes')
    dataDia.update(weekday_dummies)
    dataDia.update(month_dummies)

    entrada = dataDia[['Dia', 'DiaDaSemana_0','DiaDaSemana_1','DiaDaSemana_2','DiaDaSemana_3', 'DiaDaSemana_4', 'DiaDaSemana_5',\
            'Mes_1', 'Mes_2', 'Mes_3', 'Mes_4', 'Mes_5', 'Mes_6', 'Mes_7', 'Mes_8', 'Mes_9', 'Mes_10', 'Mes_11', 'Mes_12', 'Ano']]

    return entrada, dataDia

   #Data do dia para entrada do modelo de predição do Takt Time
   
while True:  
   entradaModeloTakt, dataDia = obterDataDia()
   #Cria agentes
   gerenciadorPlanta = Gerenciador('Gerenciador_Planta', 'ag16')
   sensorTransporte = Sensor("Sensor_Transporte", 'ag06')

   #Importa modelos de ML para o agente GerenciadorPlanta
   modGerenciadorTaxaSaida = joblib.load('construcaoModelo/modGerenciadorTaxaSaida.pkl')
   modGerenciadorTakt = joblib.load('construcaoModelo/modGerenciadorTakt.pkl')

   #Define de quem e de quais endereços o agente GerenciadorPlanta vai receber dados
   gerenciadorPlanta.agentesFonte = {'Robo_Entrada': {'nomeAgente':'Robo_Entrada'}, 'Esteira_Principal': {'nomeAgente':'Esteira_Principal'}, \
                                    'Robo_Inspecao': {'nomeAgente':'Robo_Inspecao'}, 'Limpador_Pneumatico': {'nomeAgente':'Limpador_Pneumatico'} , \
                                       'Robo_Saida': {'nomeAgente':'Robo_Saida'}, 'Sensor_Transporte': {'nomeAgente':'Sensor_Transporte'}}
   gerenciadorPlanta.urlsFonte = {'Atuador': 'http://192.168.3.115:5001/atuador', 'Sensor': 'http://192.168.3.115:5003/sensor',
                                 'CLP6': "opc.tcp://192.168.1.24:4840"}

   #Define de quem e de quais endereços o agente SensorTransporte vai receber dados
   sensorTransporte.urlFonteOPCUA['Estado_Esteira'] = 'opc.tcp://192.168.1.24:4840'
   sensorTransporte.urlFonteOPCUA['Velocidade_Esteira'] = 'opc.tcp://192.168.1.24:4840'
   sensorTransporte.nodeIdOPCUA["Estado_Esteira"] = 'ns=3;s="Supervisorio_Variaveis"."Transporte_Bool"[1]'
   sensorTransporte.nodeIdOPCUA['Velocidade_Esteira'] = 'ns=3;s="OPC_EST_INTEG"."EST_TRANS"."Velocidade_Esteira"'

   #SensorTransporte lê dados e disponobiliza para outros agentes
   sensorTransporte.dadosInformar['Estado_Esteira'] = list(sensorTransporte.lerDados(nomeFonte= 'Estado_Esteira').values())[0]
   sensorTransporte.dadosInformar['Velocidade_Esteira'] = list(sensorTransporte.lerDados(nomeFonte= 'Velocidade_Esteira').values())[0]
   sensorTransporte.disponibilizarDadosAPI()

   #GerenciadorPlanta recebe a disponibildiade prevista dos outros agentes, pega a data do dia e os junta num dataframe para ser a entrada da 
   #predição da taxa de saída
   entradaModeloTaxaSaida = {}
   entradaModeloTaxaSaida['disponibilidade_entrada'] = list(gerenciadorPlanta.receberDados(agenteFonte='Robo_Entrada', classeFonte='Atuador').values())[0]
   entradaModeloTaxaSaida['disponibilidade_transporte'] = list(gerenciadorPlanta.receberDados(agenteFonte='Esteira_Principal', classeFonte='Atuador').values())[0]
   entradaModeloTaxaSaida['disponibilidade_inspecao'] = list(gerenciadorPlanta.receberDados(agenteFonte='Robo_Inspecao', classeFonte='Atuador').values())[0]
   entradaModeloTaxaSaida['disponibilidade_limpeza'] = list(gerenciadorPlanta.receberDados(agenteFonte='Limpador_Pneumatico', classeFonte='Atuador').values())[0]
   entradaModeloTaxaSaida['disponibilidade_saida'] = list(gerenciadorPlanta.receberDados(agenteFonte='Robo_Saida', classeFonte='Atuador').values())[0]
   entradaModeloTaxaSaida = pd.DataFrame(entradaModeloTaxaSaida, index = [0])
   entradaModeloTaxaSaida = pd.concat([entradaModeloTakt, entradaModeloTaxaSaida], axis=1)

   #GerenciadorPlanta recebe o Estado e a Velocidade da Esteira atuais
   estadoEsteira = gerenciadorPlanta.receberDados(agenteFonte='Sensor_Transporte', classeFonte='Sensor')['Estado_Esteira']
   #estadoEsteira = 1
   velocidadeEsteira = gerenciadorPlanta.receberDados(agenteFonte='Sensor_Transporte', classeFonte='Sensor')['Velocidade_Esteira']

   #GerenciadorPlanta faz a predição da Taxa de Saída e do Takt Time
   predicaoTaxaSaida = modGerenciadorTaxaSaida.predict(entradaModeloTaxaSaida)
   if predicaoTaxaSaida[0] < 0:
      predicaoTaxaSaida[0] = 0
   predicaoTakt = modGerenciadorTakt.predict(entradaModeloTakt.drop(columns=['Ano'], inplace=False))
   if predicaoTakt[0] < 0:
      predicaoTakt[0] = 0

   prompt = "Se deseja simular a alteracao de velocidade da esteira pressione 's'.\nSe não deseja, Aguarde 10 segundos ou pressione qualquer outra tecla.\n"
   timeout = 10
   simular = get_user_input(prompt, timeout)
   
   if simular is not None:
      ritmoPredito = float(input(f'Digite um ritmo de produção menor do que {predicaoTakt[0]} (s/und).\n'))   
   else:
      print("\nSimulação não escolhida. A predição real será mantida.\n")
      try:
         ritmoPredito = 3600/predicaoTaxaSaida[0]
      except ZeroDivisionError:
         ritmoPredito = 0

   #GerenciadorPlanta toma a decisão sobre a velocidade da esteira
   decisaoEsteira = {}
   
   if estadoEsteira == 0:
      decisaoEsteira = {'A esteira não está em funcionamento': 40}
  
   elif predicaoTakt[0] == 0:
      decisaoEsteira = {'A demanda prevista é 0 (s/und). Manter Velocidade da Esteira reduzida durante os próximos 5 minutos': 40}
    
   elif ritmoPredito >= predicaoTakt[0]:
      decisaoEsteira = {f'Ritmo de produção predito ({ritmoPredito} s/und) atenderá a demanda prevista({predicaoTakt[0]} s/und). Manter Velocidade da Esteira reduzida durante os próximos 5 minutos': 40}
      
   else:
      decisaoEsteira = {f'Ritmo de produção predito ({ritmoPredito} s/und) não atenderá a demanda prevista({predicaoTakt[0]} s/und). Aumentar Velocidade da Esteira para os próximos 5 minutos': 55}
      alteracao = True

   gerenciadorPlanta.dadosInformar = {'Takt_Time': {f'Predicao para o Takt Time (s/und) da estação de Entrada para o dia {dataDia["Ano"][0]\
                                                                     }-{dataDia["Mes"][0]\
                                                                        }-{dataDia["Dia"][0]\
                                                                           }': predicaoTakt[0]},
                                       'Taxa_de_Saida':{f'Predicao para o Taxa de Saída (und/h) da PMA para o dia {dataDia["Ano"][0]\
                                                                     }-{dataDia["Mes"][0]\
                                                                        }-{dataDia["Dia"][0]\
                                                                           }': predicaoTaxaSaida[0]},
                                       'Decisão do Gerenciador_Planta': decisaoEsteira}


   print(f'Agente {gerenciadorPlanta.nomeAgente} informa: {gerenciadorPlanta.dadosInformar}\n')
   gerenciadorPlanta.disponibilizarDadosAPI()
   #gerenciadorPlanta.disponibilizarDadosOPCUA(tempo=10)
   gerenciadorPlanta.dadosInformar["Alterar_Velocidade"] = {"Alterar_Velocidade": True}
   gerenciadorPlanta.alterarVariavel(nomeFonte='CLP6', nodeId='ns=3;s="OPC_EST_INTEG"."Status_Esteira"', nomeVariavel='Alterar_Velocidade')
   gerenciadorPlanta.alterarVariavel(nomeFonte='CLP6', nodeId='ns=3;s="OPC_EST_INTEG"."EST_TRANS"."Velocidade_Esteira"', nomeVariavel='Decisão do Gerenciador_Planta')
   gerenciadorPlanta.dadosInformar["Alterar_Velocidade"] = {"Alterar_Velocidade": False}
   gerenciadorPlanta.alterarVariavel(nomeFonte='CLP6', nodeId='ns=3;s="OPC_EST_INTEG"."Status_Esteira"', nomeVariavel='Alterar_Velocidade')
   
   print(f"\nAgente Sensor_Transporte informa - Novo valor de velocidade da esteira: {list(sensorTransporte.lerDados(nomeFonte= 'Velocidade_Esteira').values())[0]}\n")

   time.sleep(15)