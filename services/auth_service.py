from config import seguranca, models, utils
from config import DB_CLIENTES, DB_FUNCIONARIOS


def login(email, senha):
    """
    Tenta autenticar o usuário.
    Retorna (usuario_obj, mensagem) ou (None, mensagem_erro).
    """
    arquivos = [DB_CLIENTES, DB_FUNCIONARIOS]

    usuario_encontrado = None
    for arquivo in arquivos:
        base_dados = utils.carregar_json(arquivo)
        usuario_encontrado = next(
            (u for u in base_dados if u['email'] == email), None
        )
        if usuario_encontrado:
            break

    if not usuario_encontrado:
        return None, "E-mail ou senha incorretos."

    if not seguranca.verificar_senha(senha, usuario_encontrado['senha']):
        return None, "E-mail ou senha incorretos."

    # Determina o tipo de usuário
    if usuario_encontrado.get('role') == 'admin' or email == "rafawloficial@gmail.com":
        usuario_obj = models.Administrador(usuario_encontrado)
    else:
        usuario_obj = models.Usuario(usuario_encontrado)

    return usuario_obj, f"Bem-vindo(a), {usuario_obj.nome}!"

