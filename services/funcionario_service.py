from datetime import datetime, date
from config import seguranca, utils
from config import DB_FUNCIONARIOS, LOG_FUNCIONARIOS


def listar_funcionarios():
    """Retorna a lista completa de funcionários."""
    return utils.carregar_json(DB_FUNCIONARIOS)


def buscar_funcionarios(termo):
    """Busca funcionários por nome ou email."""
    lista = utils.carregar_json(DB_FUNCIONARIOS)
    termo = termo.lower()
    return [u for u in lista if termo in u['nome'].lower() or termo in u['email'].lower()]


def cadastrar_vendedor(nome, email, telefone, senha, data_nasc_str, endereco_dados, token_vendedor):
    """
    Cadastra um novo vendedor em funcionarios.json.
    Valida o token antes de cadastrar.
    Retorna (sucesso, mensagem).
    """
    from services.cliente_service import validar_token_vendedor

    # Validar token
    valido, msg = validar_token_vendedor(token_vendedor or "")
    if not valido:
        return False, msg

    if not seguranca.validar_email(email):
        return False, "Email inválido!"

    if not seguranca.validar_telefone(telefone):
        return False, "Telefone inválido!"

    lista = utils.carregar_json(DB_FUNCIONARIOS)

    if any(u['email'] == email for u in lista):
        return False, "Este e-mail já está cadastrado!"

    # Validar idade (>= 18)
    try:
        nascimento = datetime.strptime(data_nasc_str, "%d/%m/%Y").date()
        hoje = date.today()
        idade = hoje.year - nascimento.year - \
            ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
        if idade < 18:
            return False, "Vendedor deve ser maior de 18 anos!"
    except ValueError:
        return False, "Data de nascimento inválida! Use dd/mm/aaaa."

    novo_id = lista[-1]['id'] + 1 if lista else 1
    senha_hash = seguranca.gerar_hash_senha(senha)

    novo_vendedor = {
        "id": novo_id,
        "role": "vendedor",
        "nome": nome,
        "email": email,
        "telefone": telefone,
        "senha": senha_hash,
        "data_nascimento": data_nasc_str,
        "idade": idade,
        "endereco": endereco_dados
    }

    lista.append(novo_vendedor)
    utils.salvar_json(lista, DB_FUNCIONARIOS)
    utils.registrar_evento(f"NOVO VENDEDOR: {nome}", LOG_FUNCIONARIOS)
    return True, f"Vendedor '{nome}' cadastrado com sucesso!"


def cadastrar_funcionario(nome, email, telefone, senha, data_nasc_str, endereco_dados):
    """
    Cadastra um novo funcionário.
    Retorna (sucesso, mensagem).
    """
    if not seguranca.validar_email(email):
        return False, "Email inválido!"

    if not seguranca.validar_telefone(telefone):
        return False, "Telefone inválido!"

    lista = utils.carregar_json(DB_FUNCIONARIOS)

    if any(u['email'] == email for u in lista):
        return False, "Este e-mail já está cadastrado!"

    # Validar idade (>= 18)
    try:
        nascimento = datetime.strptime(data_nasc_str, "%d/%m/%Y").date()
        hoje = date.today()
        idade = hoje.year - nascimento.year - \
            ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
        if idade < 18:
            return False, "Funcionário deve ser maior de 18 anos!"
    except ValueError:
        return False, "Data de nascimento inválida! Use dd/mm/aaaa."

    novo_id = lista[-1]['id'] + 1 if lista else 1
    senha_hash = seguranca.gerar_hash_senha(senha)

    novo_funcionario = {
        "id": novo_id,
        "role": "Funcionário",
        "nome": nome,
        "email": email,
        "telefone": telefone,
        "senha": senha_hash,
        "data_nascimento": data_nasc_str,
        "idade": idade,
        "endereco": endereco_dados
    }

    lista.append(novo_funcionario)
    utils.salvar_json(lista, DB_FUNCIONARIOS)
    utils.registrar_evento(f"NOVO FUNCIONÁRIO: {nome}", LOG_FUNCIONARIOS)
    return True, f"Funcionário '{nome}' cadastrado com sucesso!"


def editar_funcionario(id_alvo, campo, novo_valor):
    """Edita um campo de funcionário. Retorna (sucesso, mensagem)."""
    lista = utils.carregar_json(DB_FUNCIONARIOS)
    u = next((item for item in lista if str(item["id"]) == str(id_alvo)), None)

    if not u:
        return False, "Funcionário não encontrado."

    if campo == 'senha':
        u['senha'] = seguranca.gerar_hash_senha(novo_valor)
    elif campo == 'numero':
        u['endereco']['numero'] = novo_valor
    elif campo in ('nome', 'email', 'telefone'):
        u[campo] = novo_valor
    else:
        return False, f"Campo '{campo}' não reconhecido."

    utils.salvar_json(lista, DB_FUNCIONARIOS)
    utils.registrar_evento(f"EDIÇÃO FUNCIONÁRIO: ID {id_alvo} campo '{campo}' alterado.", LOG_FUNCIONARIOS)
    return True, "Alteração salva!"


def deletar_funcionario(id_alvo):
    """Deleta um funcionário pelo ID. Retorna (sucesso, mensagem)."""
    lista = utils.carregar_json(DB_FUNCIONARIOS)
    nova_lista = [u for u in lista if str(u['id']) != str(id_alvo)]

    if len(nova_lista) == len(lista):
        return False, "ID não encontrado."

    utils.salvar_json(nova_lista, DB_FUNCIONARIOS)
    utils.registrar_evento(f"DELEÇÃO FUNCIONÁRIO: ID {id_alvo}", LOG_FUNCIONARIOS)
    return True, "Funcionário removido com sucesso!"


def get_dashboard_funcionarios():
    """Retorna estatísticas de funcionários."""
    lista = utils.carregar_json(DB_FUNCIONARIOS)
    if not lista:
        return {"total": 0, "por_estado": {}}

    total = len(lista)
    ufs = [u['endereco'].get('uf', 'N/A') for u in lista if u.get('endereco')]
    por_estado = {}
    for uf in set(ufs):
        por_estado[uf] = ufs.count(uf)

    return {"total": total, "por_estado": por_estado}
