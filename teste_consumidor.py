import requests

urlOperadorSaida = 'http://127.0.0.1:5002/gerenciador'
operadorSaidaAPI = {
    'nomeAgente': 'Gerenciador_Planta' 
}

response = requests.post(url = urlOperadorSaida, json = operadorSaidaAPI)

if response.status_code == 200:
# A resposta da API está no formato JSON
	data = response.json()
	print(f'Predicao lida da API: {data}')
	
else:
	print('Falha ao obter a variável da API')


