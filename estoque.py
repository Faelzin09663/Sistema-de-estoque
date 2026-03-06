import json
import os
from datetime import datetime

ARQUIVO_ESTOQUE = 'estoque.json'
ARQUIVO_LOGS = 'atividades.txt'

# Registra os LOGS no sistema, como cadastro de produtos e saídas
def registrar_log(mensagem):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(ARQUIVO_LOGS, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {mensagem}\n")

# Carrega os dados do estoque no banco de dados (arquivo JSON) e salva as alterações

def carregar_estoque():
    if not os.path.exists(ARQUIVO_ESTOQUE):
        return []
    with open(ARQUIVO_ESTOQUE, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []
        
  #   Salva os dados do estoque no banco de dados (arquivo JSON) e salva as alterações  

def salvar_estoque(dados):
    with open(ARQUIVO_ESTOQUE, "w", encoding="utf-8") as file:
        json.dump(dados, file, indent=4, ensure_ascii=False)

# Cadastra novos produtos no estoque, listagem de produtos e registrar saídas do estoque (com controle de quantidade e logs)

def cadastrar_produto():
    print("\n" + "="*30)
    print("\n📦 --- NOVO PRODUTO ---")
    print("="*30)
    lista_estoque = carregar_estoque()
    novo_id = lista_estoque[-1]['id'] + 1 if lista_estoque else 1
    name = input("Nome do produto: ")
    try:
        quantidade = int(input("Quantidade: "))
        preco = float(input("Preço: "))
    except ValueError:
        print("\n❌ Quantidade e preço devem ser números válidos!")
        return
    descricao = input("Descrição (opcional): ")

    novo_produto = {
        "id": novo_id,
        "nome": name,
        "quantidade": quantidade,
        "preco": preco,
        "descricao": descricao
    }

    lista_estoque.append(novo_produto)
    salvar_estoque(lista_estoque)
    print(f"\n✅ Produto '{name}' cadastrado com sucesso!")
    registrar_log(f"Produto cadastrado: {name} (ID: {novo_id})")

# Listagem de produtos e registrar saídas do estoque (com controle de quantidade e logs)

def listar_produtos():
    lista_estoque = carregar_estoque()
    print("\n" + "="*30)
    print("\n📋 --- ESTOQUE ATUAL ---")
    print("="*30)
    if not lista_estoque:
        print("\n⚠️  O estoque está vazio!")
        return
    
    print(f"{'ID':<4} | {'PRODUTO':<20} | {'QTD':<5} | {'PREÇO'}")
    print("-" * 50)
    for p in lista_estoque:
        print(f"{p['id']:<4} | {p['nome'][:20]:<20} | {p['quantidade']:<5} | R$ {p['preco']:.2f}") 

# registrar saídas do estoque (com controle de quantidade e logs)

def registrar_saida(usuario_nome):
    lista_estoque = carregar_estoque()
    if not lista_estoque:
        print("\n⚠️  O estoque está vazio!")
        return  
    listar_produtos()
    try:
        id_alvo = int(input("\nDigite o ID do produto para registrar saída: "))
        produto = next((p for p in lista_estoque if p['id'] == id_alvo), None)
    except ValueError:
        print("\n❌ ID deve ser um número válido!")
        return
    
    if produto:
        if produto['quantidade'] <= 0:
            print("❌ Produto esgotado!")
            return
        try:
            qtd_saida = int(input(f"Quantas unidades de '{produto['nome']}' deseja retirar? (Max: {produto['quantidade']}): "))
            if 0 < qtd_saida <= produto['quantidade']:
                produto['quantidade'] -= qtd_saida
                salvar_estoque(lista_estoque)
                registrar_log(f"SAÍDA: {usuario_nome} retirou {qtd_saida}x {produto['nome']}.")
                print(f"✔ Saída registrada! Restam {produto['quantidade']} no estoque.")
            else:
                print("❌ Quantidade inválida.")
        except ValueError:
            print("❌ Quantidade inválida.")
    else:
        print("❌ Produto não encontrado.")


while True:
    print("\n" + "="*30)
    print("\n📦 --- GESTÃO DE ESTOQUE ---")
    print("="*30)
    print("\n1. Cadastrar produto")
    print("2. Listar produtos")
    print("3. Registrar saída")
    print("4. Sair")
    print("="*30)
    
    opcao = input("\nEscolha uma opção: ")
    
    if opcao == "1":
        cadastrar_produto()
    elif opcao == "2":
        listar_produtos()
    elif opcao == "3":
        usuario_nome = input("Digite seu nome: ")
        registrar_saida(usuario_nome)
    elif opcao == "4":
        print("\n👋 Até logo!")
        break
    else:
        print("\n❌ Opção inválida!")
