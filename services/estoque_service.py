from config.config import DB_ESTOQUE, LOG_ESTOQUE, ALERTA_ESTOQUE_BAIXO
from config import utils
def listar_produtos():
    """Retorna a lista completa de produtos."""
    return utils.carregar_json(DB_ESTOQUE)


def buscar_produtos(termo):
    """Busca produtos por nome."""
    lista = utils.carregar_json(DB_ESTOQUE)
    termo = termo.lower()
    return [p for p in lista if termo in p['nome'].lower()]


def cadastrar_produto(nome, quantidade, preco, descricao=""):
    """Cadastra novo produto. Retorna (sucesso, mensagem)."""
    try:
        quantidade = int(quantidade)
        preco = float(preco)
    except (ValueError, TypeError):
        return False, "Quantidade e preço devem ser números válidos!"

    lista = utils.carregar_json(DB_ESTOQUE)
    novo_id = lista[-1]['id'] + 1 if lista else 1

    novo_produto = {
        "id": novo_id,
        "nome": nome,
        "quantidade": quantidade,
        "preco": preco,
        "descricao": descricao
    }

    lista.append(novo_produto)
    utils.salvar_json(lista, DB_ESTOQUE)
    utils.registrar_evento(f"Produto cadastrado: {nome} (ID: {novo_id})", LOG_ESTOQUE)
    return True, f"Produto '{nome}' cadastrado com sucesso!"


def editar_produto(id_alvo, campo, novo_valor):
    """Edita um campo de um produto. Retorna (sucesso, mensagem)."""
    lista = utils.carregar_json(DB_ESTOQUE)
    p = next((item for item in lista if str(item["id"]) == str(id_alvo)), None)

    if not p:
        return False, "Produto não encontrado."

    if campo in ('quantidade', 'preco'):
        try:
            novo_valor = int(novo_valor) if campo == 'quantidade' else float(novo_valor)
        except (ValueError, TypeError):
            return False, f"Valor inválido para '{campo}'."

    if campo in ('nome', 'quantidade', 'preco', 'descricao'):
        p[campo] = novo_valor
    else:
        return False, f"Campo '{campo}' não reconhecido."

    utils.salvar_json(lista, DB_ESTOQUE)
    utils.registrar_evento(f"Produto editado: ID {id_alvo} campo '{campo}'", LOG_ESTOQUE)
    return True, "Produto atualizado!"


def deletar_produto(id_alvo):
    """Deleta um produto pelo ID. Retorna (sucesso, mensagem)."""
    lista = utils.carregar_json(DB_ESTOQUE)
    nova_lista = [p for p in lista if str(p['id']) != str(id_alvo)]

    if len(nova_lista) == len(lista):
        return False, "Produto não encontrado."

    utils.salvar_json(nova_lista, DB_ESTOQUE)
    utils.registrar_evento(f"Produto deletado: ID {id_alvo}", LOG_ESTOQUE)
    return True, "Produto removido com sucesso!"


def registrar_saida(id_alvo, qtd_saida, usuario_nome):
    """Registra saída de estoque. Retorna (sucesso, mensagem)."""
    lista = utils.carregar_json(DB_ESTOQUE)
    p = next((item for item in lista if item['id'] == int(id_alvo)), None)

    if not p:
        return False, "Produto não encontrado."

    if p['quantidade'] <= 0:
        return False, "Produto esgotado!"

    try:
        qtd_saida = int(qtd_saida)
    except (ValueError, TypeError):
        return False, "Quantidade inválida."

    if qtd_saida <= 0 or qtd_saida > p['quantidade']:
        return False, f"Quantidade inválida. Máximo: {p['quantidade']}."

    p['quantidade'] -= qtd_saida
    utils.salvar_json(lista, DB_ESTOQUE)
    utils.registrar_evento(f"SAÍDA: {usuario_nome} retirou {qtd_saida}x {p['nome']}.", LOG_ESTOQUE)
    return True, f"Saída registrada! Restam {p['quantidade']} un."


def get_alertas_estoque():
    """Retorna produtos com estoque baixo."""
    lista = utils.carregar_json(DB_ESTOQUE)
    return [p for p in lista if p['quantidade'] <= ALERTA_ESTOQUE_BAIXO]


def get_dashboard_estoque():
    """Retorna estatísticas do estoque."""
    lista = utils.carregar_json(DB_ESTOQUE)
    if not lista:
        return {"total_produtos": 0, "total_itens": 0, "valor_total": 0, "alertas": 0}

    total_itens = sum(p['quantidade'] for p in lista)
    valor_total = sum(p['quantidade'] * p['preco'] for p in lista)
    alertas = len([p for p in lista if p['quantidade'] <= ALERTA_ESTOQUE_BAIXO])

    return {
        "total_produtos": len(lista),
        "total_itens": total_itens,
        "valor_total": valor_total,
        "alertas": alertas
    }
