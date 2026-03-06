import json
import os
import getpass
from datetime import datetime, date
import cep_test
import seguranca
import models

DB_FILE = "cadastro.json"
LOG_FILE = "atividades.txt"

# --- FUNÇÕES DE UTILIDADE ---

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def registrar_log(mensagem):
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {mensagem}\n")

def carregar_dados():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []

def salvar_dados(dados):
    with open(DB_FILE, "w", encoding="utf-8") as file:
        json.dump(dados, file, ensure_ascii=False, indent=4)

# --- FUNÇÕES DE GESTÃO ---

def deletar_usuario(id_alvo=None):
    lista = carregar_dados()
    if id_alvo is None:
        listar_usuarios()
        id_alvo = input("\nID para DELETAR: ")
    nova_lista = [u for u in lista if str(u['id']) != str(id_alvo)]
    if len(nova_lista) < len(lista):
        if input(f"Confirmar deleção do ID {id_alvo}? (s/n): ").lower() == 's':
            salvar_dados(nova_lista)
            registrar_log(f"DELEÇÃO: ID {id_alvo}")
            print("✔ Removido!")
    else: print("ID não encontrado.")

def gerar_dashboard():
    limpar_tela()
    lista = carregar_dados()
    if not lista: print("Sem dados."); return

    total = len(lista)
    maiores = sum(1 for u in lista if u['idade'] and u['idade'] >= 18)
    menores = total - maiores
    
    print("=== 📊 DASHBOARD DE ESTATÍSTICAS ===")
    print(f"Total de Usuários: {total}")
    print(f"Público: {maiores} Adultos | {menores} Menores")
    
    # Contagem por Estado (A tua lógica original!)
    ufs = [u['endereco'].get('uf', 'N/A') for u in lista]
    print("\nDistribuição por Estado:")
    for uf in set(ufs):
        print(f" - {uf}: {ufs.count(uf)} usuário(s)")
    
    print("="*30)
    input("\nPressione Enter para voltar...")


def editar_usuario(id_alvo=None):
    lista = carregar_dados()
    if not lista: print("Nenhum usuário."); return
    
    if id_alvo is None:
        listar_usuarios()
        id_alvo = input("\nDigite o ID para editar: ")

    u = next((item for item in lista if str(item["id"]) == str(id_alvo)), None)
    
    if u:
        while True:
            limpar_tela()
            print(f"📝 EDITANDO: {u['nome']} (ID: {u['id']})")
            print("1-Nome 2-Email 3-Tel 4-Senha 5-Endereço 6-Sair")
            op = input("Escolha: ")
            if op == "1": u['nome'] = input(f"Novo nome [{u['nome']}]: ") or u['nome']
            elif op == "2": u['email'] = input(f"Novo email [{u['email']}]: ") or u['email']
            elif op == "3": u['telefone'] = input(f"Novo tel [{u['telefone']}]: ") or u['telefone']
            elif op == "4": u['senha'] = seguranca.gerar_hash_senha(getpass.getpass("Nova Senha: "))
            elif op == "5": u['endereco']['numero'] = input(f"Novo Nº [{u['endereco']['numero']}]: ")
            elif op == "6": break
            
            salvar_dados(lista)
            registrar_log(f"EDIÇÃO: ID {u['id']} alterado.")
            print("✔ Salvo!")
    else: print("ID não encontrado.")

def cadastrar():
    limpar_tela()
    lista = carregar_dados()
    novo_id = lista[-1]['id'] + 1 if lista else 1

    print(">>> NOVO CADASTRO")
    nome = input("Nome: ")
    email = input("Email: ")
    if not seguranca.validar_email(email):
        print("❌ Email inválido! Cadastro cancelado."); return
    
    if any(u['email'] == email for u in lista):
        print("❌ Este e-mail já existe!"); return

    telefone = input("Telefone: ")
    if not seguranca.validar_telefone(telefone):
        print("❌ Telefone inválido!"); return

    senha_plana = getpass.getpass("Digite a senha: ")
    senha_protegida = seguranca.gerar_hash_senha(senha_plana)
    data_nasc_str = input("Data de Nascimento (dd/mm/aaaa): ")
    
    # Define o cargo inicial
    cargo = 'admin' if email == "rafawloficial@gmail.com" else 'usuario'

    idade = None; filiacao = None
    try:
        nascimento = datetime.strptime(data_nasc_str, "%d/%m/%Y").date()
        hoje = date.today()
        idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
        
        if idade < 18:
            print("\nMenor de idade. Dados dos responsáveis:")
            filiacao = {
                "pai": {"nome": input("Nome do Pai: "), "email": input("Email do Pai: ")},
                "mae": {"nome": input("Nome da Mãe: "), "email": input("Email da Mãe: ")}
            }
    except ValueError:
        print("⚠️ Data inválida.")

    end_cep = input("CEP (ou 1 para manual): ")
    info_endereco = {} # Começamos com um dicionário vazio

    if end_cep == "1":
        print("\n--- Preenchimento Manual ---")
        info_endereco = {
            "cep": "Manual",
            "logradouro": input("Rua/Av: "),
            "bairro": input("Bairro: "),
            "localidade": input("Cidade: "),
            "uf": input("UF: "),
            "numero": input("Número: ")
        }
    else:
        # Tenta buscar na API
        res = cep_test.consultar_cep(end_cep)
        
        # Se a API retornar um dicionário com sucesso
        if isinstance(res, dict) and "localidade" in res:
            print(f"✅ Endereço encontrado: {res.get('logradouro', 'S/R')}, {res['localidade']}-{res['uf']}")
            info_endereco = {
                "cep": end_cep,
                "logradouro": res.get("logradouro", "Não informado"),
                "bairro": res.get("bairro", "Não informado"),
                "localidade": res.get("localidade"),
                "uf": res.get("uf"),
                "numero": input("Digite o número da residência: ")
            }
        else:
            print("⚠️ CEP não encontrado ou inválido. Preencha manualmente:")
            info_endereco = {
                "cep": end_cep,
                "logradouro": input("Rua/Av: "),
                "bairro": input("Bairro: "),
                "localidade": input("Cidade: "),
                "uf": input("UF: "),
                "numero": input("Número: ")
            }
            
    novo_usuario = {
        "id": novo_id, 
        "role": cargo, # Adicionado vírgula e corrigida a sintaxe
        "nome": nome,
        "email": email,
        "telefone": telefone,
        "senha": senha_protegida,
        "data_nascimento": data_nasc_str,
        "idade": idade, 
        "filiacao": filiacao,
        "endereco": info_endereco
    }

    lista.append(novo_usuario)
    salvar_dados(lista)
    registrar_log(f"CADASTRO: ID {novo_id} ({nome}) como {cargo}.")
    print("\n✔ Cadastro realizado com sucesso!")

def listar_usuarios():
    lista = carregar_dados()
    print("\n>>> LISTA DE USUÁRIOS")
    if not lista:
        print("Nenhum registro encontrado."); return
    
    print(f"{'ID':<4} | {'NOME':<15} | {'EMAIL':<25} | {'LOCALIDADE'}")
    print("-" * 70)
    for u in lista:
        cidade = u['endereco'].get('localidade', 'N/A')
        uf = u['endereco'].get('uf', 'N/A')
        print(f"{u['id']:<4} | {u['nome'][:15]:<15} | {u['email'][:25]:<25} | {cidade}-{uf}")

def buscar_usuario():
    limpar_tela()
    print("=== 🔍 BUSCA DE USUÁRIOS ===")
    termo = input("Digite o nome ou e-mail para buscar: ").lower()
    lista = carregar_dados()
    resultados = [u for u in lista if termo in u['nome'].lower() or termo in u['email'].lower()]
    
    if resultados:
        for u in resultados:
            print(f"ID: {u['id']} | Nome: {u['nome']} | E-mail: {u['email']}")
    else:
        print("[!] Nenhum usuário encontrado.")
    input("\nPressione Enter para voltar...")

def promover_usuario():
    lista = carregar_dados()
    listar_usuarios()
    id_prom = input("\nDigite o ID para PROMOVER a Admin: ")
    encontrado = False
    for u in lista:
        if str(u.get('id')) == id_prom:
            u['role'] = 'admin'
            encontrado = True
            registrar_log(f"PROMOÇÃO: ID {u['id']} promovido a Admin.")
            break
    if encontrado:
        salvar_dados(lista)
        print("✔ Usuário promovido!")
    else:
        print("[!] ID não encontrado.")
    input("\nPressione Enter...")

# --- FUNÇÃO DE MENU DO USUÁRIO ---

def menu_usuario(usuario_obj):
    """
    Controla o que o usuário vê após o login.
    usuario_obj é uma instância das classes em models.py
    """
    while True:
        limpar_tela()
        print("\n" + "═"*30)
        print(f"👤 USER: {usuario_obj.nome.upper()}")
        print(f"📧 EMAIL: {usuario_obj.email}")
        print(f"🛡️ CARGO: {usuario_obj.cargo.upper()}")
        print("═"*30)
        print("1 - Ver meus dados")
        print("2 - Editar meus dados completos")
        print("3 - Deletar minha conta")
        
        # Opções exclusivas para Administradores
        if usuario_obj.eh_admin():
            print("4 - [ADMIN] Promover usuário a Admin")
            print("5 - [ADMIN] Ver dashboard de estatísticas")
            print("6 - [ADMIN] Listar todos os usuários")

        print("0 - Sair (Logout)")
        print("═"*30)
        
        op = input("Escolha uma opção: ")

        if op == "1":
            print("\n--- MEUS DADOS ---")
            print(f"ID: {usuario_obj.id}")
            print(f"Nome: {usuario_obj.nome}")
            print(f"E-mail: {usuario_obj.email}")
            print(f"Telefone: {usuario_obj.telefone}")
            print(f"Data de Nascimento: {usuario_obj.data_nascimento}")
            
            # Puxando os dados de endereço de forma segura
            logradouro = usuario_obj.endereco.get('logradouro', 'N/A')
            localidade = usuario_obj.endereco.get('localidade', 'N/A')
            uf = usuario_obj.endereco.get('uf', 'N/A')
            numero = usuario_obj.endereco.get('numero', 'S/N')
            
            print(f"Endereço: {logradouro}, {numero} - {localidade}/{uf}")
            print(f"Filiação: {usuario_obj.filiacao if usuario_obj.filiacao else 'N/A'}")
            input("\nPressione Enter para voltar...")
        
        elif op == "2":
            # Aqui chamamos a sua função completa que edita TUDO (senha, endereço, etc)
            # Passamos o ID do usuário logado para ele editar apenas a si mesmo
            editar_usuario(usuario_obj.id)
            
            # Como os dados foram alterados no JSON, avisamos que ele precisa logar novamente
            # para atualizar as informações na tela (o objeto na memória fica desatualizado)
            print("\n⚠️ Como seus dados foram alterados, por favor faça login novamente.")
            input("Pressione Enter para sair...")
            break

        elif op == "3":
            confirmar = input("\nTem certeza que deseja deletar sua conta? (s/n): ").lower()
            if confirmar == 's':
                senha_confirm = getpass.getpass("Digite sua senha para confirmar: ")
                dados_brutos = carregar_dados()
                u_bruto = next((d for d in dados_brutos if d['id'] == usuario_obj.id), None)
                
                if u_bruto and seguranca.verificar_senha(senha_confirm, u_bruto['senha']):
                    nova_lista = [d for d in dados_brutos if d['id'] != usuario_obj.id]
                    salvar_dados(nova_lista)
                    registrar_log(f"AUTO-DELEÇÃO: ID {usuario_obj.id} removeu a própria conta.")
                    print("✔ Conta removida. Você será desconectado.")
                    break
                else:
                    print("❌ Senha incorreta!")
                    input("\nEnter para continuar...")

        elif op == "4" and usuario_obj.eh_admin():
            promover_usuario()
        
        elif op == "5" and usuario_obj.eh_admin():
            # A função estava comentada. Agora ela vai rodar o seu código de Dashboard real!
            gerar_dashboard()

        elif op == "6" and usuario_obj.eh_admin():
            listar_usuarios()
            input("\nEnter para continuar...")

        elif op == "0":
            registrar_log(f"LOGOUT: {usuario_obj.email} saiu.")
            break
        else:
            print("Opção inválida!")
            input("\nEnter para continuar...")