from Atuador import Atuador
import joblib
from datetime import datetime
import pandas as pd

def obterDataDia():
    dataDia= pd.DataFrame({
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

DadosEntradaModelo, dataDia = obterDataDia()

#Cria roboEntrada da classe Atuador
roboEntrada = Atuador('Robo_Entrada', 'ag17')
modRoboEntrada = joblib.load('construcaoModelo/modRoboEntrada.pkl')
predicaoEntrada = modRoboEntrada.predict(DadosEntradaModelo)
roboEntrada.dadosInformar = {f'Predicao para Disponibilidade da estação de Entrada para o dia {dataDia["Ano"][0]\
                                                                   }-{dataDia["Mes"][0]\
                                                                      }-{dataDia["Dia"][0]\
                                                                         }': predicaoEntrada[0]}


#Cria esteiraPrincipal da classe Atuador
esteiraPrincipal = Atuador('Esteira_Principal', 'ag07')
modEsteira = joblib.load('construcaoModelo/modEsteira.pkl')
predicaoTransporte = modEsteira.predict(DadosEntradaModelo)
esteiraPrincipal.dadosInformar = {f'Predicao para Disponibilidade da estação de Transporte para o dia {dataDia["Ano"][0]\
                                                                   }-{dataDia["Mes"][0]\
                                                                      }-{dataDia["Dia"][0]\
                                                                         }': predicaoTransporte[0]}

#Cria roboInspecao da classe Atuador
roboInspecao = Atuador('Robo_Inspecao', 'ag18')
modRoboInspecao = joblib.load('construcaoModelo/modRoboInspecao.pkl')
predicaoInspecao = modRoboInspecao.predict(DadosEntradaModelo)
roboInspecao.dadosInformar = {f'Predicao para Disponibilidade da estação de Inspeção para o dia {dataDia["Ano"][0]\
                                                                   }-{dataDia["Mes"][0]\
                                                                      }-{dataDia["Dia"][0]\
                                                                         }': predicaoInspecao[0]}

#Cria limpadorPneumatico da classe Atuador
limpadorPneumatico = Atuador('Limpador_Pneumatico', 'ag19')
modlimpadorPneumatico = joblib.load('construcaoModelo/modLimpadorPneumatico.pkl')
predicaoLimpeza = modlimpadorPneumatico.predict(DadosEntradaModelo)
limpadorPneumatico.dadosInformar = {f'Predicao para Disponibilidade da estação de Limpeza para o dia {dataDia["Ano"][0]\
                                                                   }-{dataDia["Mes"][0]\
                                                                      }-{dataDia["Dia"][0]\
                                                                         }': predicaoLimpeza[0]}

#Cria roboSaida da classe Atuador
roboSaida = Atuador('Robo_Saida', 'ag20')
modRoboSaida = joblib.load('construcaoModelo/modRoboSaida.pkl')
predicaoSaida = modRoboSaida.predict(DadosEntradaModelo)
roboSaida.dadosInformar = {f'Predicao para Disponibilidade da estação de Saída para o dia {dataDia["Ano"][0]\
                                                                   }-{dataDia["Mes"][0]\
                                                                      }-{dataDia["Dia"][0]\
                                                                         }': predicaoSaida[0]}

#Opera Agentes
print(f'\nAgente {roboEntrada.nomeAgente} informa: {roboEntrada.dadosInformar}\n')
roboEntrada.disponibilizarDadosAPI()
#roboEntrada.disponibilizarDadosOPCUA(tempo=10)

print(f'\nAgente {esteiraPrincipal.nomeAgente} informa: {esteiraPrincipal.dadosInformar}\n')
esteiraPrincipal.disponibilizarDadosAPI()
#esteiraPrincipal.disponibilizarDadosOPCUA(tempo=10)

print(f'\nAgente {roboInspecao.nomeAgente} informa: {roboInspecao.dadosInformar}\n')
roboInspecao.disponibilizarDadosAPI()
#roboInspecao.disponibilizarDadosOPCUA(tempo=10)

print(f'\nAgente {limpadorPneumatico.nomeAgente} informa: {limpadorPneumatico.dadosInformar}\n')
limpadorPneumatico.disponibilizarDadosAPI()
#limpadorPneumatico.disponibilizarDadosOPCUA(tempo=10)

print(f'\nAgente {roboSaida.nomeAgente} informa: {roboSaida.dadosInformar}\n')
roboSaida.disponibilizarDadosAPI()
#roboSaida.disponibilizarDadosOPCUA(tempo=10)