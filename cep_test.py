import requests

def consultar_cep(cep):
    # Limpa o CEP para conter apenas números
    cep = cep.replace("-", "").replace(".", "").strip()
    
    if len(cep) != 8:
        return "CEP inválido. Deve conter 8 dígitos."
    
    # Chamada à API ViaCEP
    url = f'https://viacep.com.br/ws/{cep}/json/'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'erro' in data:
            return "CEP não encontrado."
        return data
    else:
        return "Erro ao conectar com a API."

