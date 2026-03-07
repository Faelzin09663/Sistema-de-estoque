from datetime import datetime, date
import cep_test
from config import seguranca, utils
from config import DB_CLIENTES, LOG_CLIENTES, ADMIN_EMAIL, TOKEN_FILE


def listar_clientes():
    """Retorna a lista completa de clientes."""
    return utils.carregar_json(DB_CLIENTES)


def buscar_clientes(termo):
    """Busca clientes por nome ou email."""
    lista = utils.carregar_json(DB_CLIENTES)
    termo = termo.lower()
    return [u for u in lista if termo in u['nome'].lower() or termo in u['email'].lower()]


# --- Gestão de Token de Vendedor ---

def get_vendedor_token():
    """Retorna o token atual de vendedor, ou None se não definido."""
    dados = utils.carregar_json(TOKEN_FILE)
    if dados and isinstance(dados, list) and len(dados) > 0:
        return dados[0].get('token')
    return None


def set_vendedor_token(novo_token):
    """Define o token de vendedor (somente admin). Retorna (sucesso, msg)."""
    if not novo_token or len(novo_token.strip()) < 4:
        return False, "Token deve ter pelo menos 4 caracteres!"
    utils.salvar_json([{"token": novo_token.strip()}], TOKEN_FILE)
    utils.registrar_evento(f"TOKEN VENDEDOR atualizado.", LOG_CLIENTES)
    return True, "Token de vendedor atualizado com sucesso!"


def validar_token_vendedor(token_digitado):
    """Verifica se o token digitado é válido."""
    token_real = get_vendedor_token()
    if not token_real:
        return False, "Nenhum token de vendedor definido. Contate o administrador."
    if token_digitado.strip() == token_real:
        return True, "Token válido!"
    return False, "Token inválido!"


# --- Cadastro ---

def cadastrar_cliente(nome, email, telefone, senha, data_nasc_str, endereco_dados):
    """
    Cadastra um novo cliente em cadastro.json.
    Retorna (sucesso, mensagem).
    """
    if not seguranca.validar_email(email):
        return False, "Email inválido!"

    if not seguranca.validar_telefone(telefone):
        return False, "Telefone inválido!"

    lista = utils.carregar_json(DB_CLIENTES)

    if any(u['email'] == email for u in lista):
        return False, "Este e-mail já está cadastrado!"

    novo_id = lista[-1]['id'] + 1 if lista else 1
    senha_hash = seguranca.gerar_hash_senha(senha)
    cargo = 'admin' if email == ADMIN_EMAIL else 'usuario'

    # Calcular idade
    idade = None
    filiacao = None
    try:
        nascimento = datetime.strptime(data_nasc_str, "%d/%m/%Y").date()
        hoje = date.today()
        idade = hoje.year - nascimento.year - \
            ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
    except ValueError:
        pass

    novo_usuario = {
        "id": novo_id,
        "role": cargo,
        "nome": nome,
        "email": email,
        "telefone": telefone,
        "senha": senha_hash,
        "data_nascimento": data_nasc_str,
        "idade": idade,
        "filiacao": filiacao,
        "endereco": endereco_dados
    }

    lista.append(novo_usuario)
    utils.salvar_json(lista, DB_CLIENTES)
    utils.registrar_evento(f"CADASTRO: ID {novo_id} ({nome}) como {cargo}.", LOG_CLIENTES)
    return True, f"Cliente '{nome}' cadastrado com sucesso!"


def editar_cliente(id_alvo, campo, novo_valor):
    """
    Edita um campo específico de um cliente.
    campo: 'nome', 'email', 'telefone', 'senha', 'numero'
    Retorna (sucesso, mensagem).
    """
    lista = utils.carregar_json(DB_CLIENTES)
    u = next((item for item in lista if str(item["id"]) == str(id_alvo)), None)

    if not u:
        return False, "Cliente não encontrado."

    if campo == 'senha':
        u['senha'] = seguranca.gerar_hash_senha(novo_valor)
    elif campo == 'numero':
        u['endereco']['numero'] = novo_valor
    elif campo in ('nome', 'email', 'telefone'):
        u[campo] = novo_valor
    else:
        return False, f"Campo '{campo}' não reconhecido."

    utils.salvar_json(lista, DB_CLIENTES)
    utils.registrar_evento(f"EDIÇÃO: ID {id_alvo} campo '{campo}' alterado.", LOG_CLIENTES)
    return True, "Alteração salva!"


def deletar_cliente(id_alvo):
    """Deleta um cliente pelo ID. Retorna (sucesso, mensagem)."""
    lista = utils.carregar_json(DB_CLIENTES)
    nova_lista = [u for u in lista if str(u['id']) != str(id_alvo)]

    if len(nova_lista) == len(lista):
        return False, "ID não encontrado."

    utils.salvar_json(nova_lista, DB_CLIENTES)
    utils.registrar_evento(f"DELEÇÃO: ID {id_alvo}", LOG_CLIENTES)
    return True, "Cliente removido com sucesso!"


def promover_usuario(id_alvo):
    """Promove um cliente a admin. Retorna (sucesso, mensagem)."""
    lista = utils.carregar_json(DB_CLIENTES)
    u = next((item for item in lista if str(item.get('id')) == str(id_alvo)), None)

    if not u:
        return False, "ID não encontrado."

    u['role'] = 'admin'
    utils.salvar_json(lista, DB_CLIENTES)
    utils.registrar_evento(f"PROMOÇÃO: ID {id_alvo} promovido a Admin.", LOG_CLIENTES)
    return True, f"Usuário '{u['nome']}' promovido a Admin!"


def get_dashboard_clientes():
    """Retorna estatísticas de clientes."""
    lista = utils.carregar_json(DB_CLIENTES)
    if not lista:
        return {"total": 0, "adultos": 0, "menores": 0, "por_estado": {}}

    total = len(lista)
    adultos = sum(1 for u in lista if u.get('idade') and u['idade'] >= 18)
    menores = total - adultos

    ufs = [u['endereco'].get('uf', 'N/A') for u in lista if u.get('endereco')]
    por_estado = {}
    for uf in set(ufs):
        por_estado[uf] = ufs.count(uf)

    return {
        "total": total,
        "adultos": adultos,
        "menores": menores,
        "por_estado": por_estado
    }


def consultar_cep(cep):
    """Consulta um CEP via API. Retorna dict com dados ou None."""
    try:
        res = cep_test.consultar_cep(cep)
        if isinstance(res, dict) and "localidade" in res:
            return res
    except Exception:
        pass
    return None
