class Usuario:
    def __init__(self, dados):
        # Dados básicos
        self.id = dados.get('id')
        self.nome = dados.get('nome')
        self.email = dados.get('email')
        self.telefone = dados.get('telefone')
        self.cargo = dados.get('role', 'usuario')
        
        # --- ATRIBUTOS NOVOS ADICIONADOS AQUI ---
        # Usamos o .get() para não dar erro se o dado estiver vazio no JSON
        self.data_nascimento = dados.get('data_nascimento', 'Não informada')
        self.endereco = dados.get('endereco', {})
        self.filiacao = dados.get('filiacao', None)

    def eh_admin(self):
        return str(self.cargo).lower() == 'admin'

class Administrador(Usuario):
    def __init__(self, dados):
        super().__init__(dados) # Puxa todos os atributos (nome, data, endereco) da classe Usuario
        self.cargo = 'admin'


class produto:
    def __init__(self, dados):
        self.id = dados.get('id')
        self.nome = dados.get('nome')
        self.preco = dados.get('preco')
        self.descricao = dados.get('descricao', 'Sem descrição')
        self.quantidade = dados.get('quantidade', 0)

    def em_estoque(self):
        return self.quantidade > 0
