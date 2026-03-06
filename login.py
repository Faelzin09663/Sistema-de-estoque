import models    # Importante para transformar dict em objeto
import seguranca
import cadastro  # ESSA LINHA RESOLVE O NAMEERROR

def login():
    print("\n" + "═"*30)
    print("      LOGAR NA SUA CONTA")
    print("═"*30)
    email = input("Digite seu e-mail: ")
    senha = input("Digite sua senha: ")

    # Agora o Python sabe que carregar_dados vem do arquivo cadastro
    usuarios = cadastro.carregar_dados()
    usuario_encontrado = next((u for u in usuarios if u['email'] == email), None)

    if usuario_encontrado and seguranca.verificar_senha(senha, usuario_encontrado['senha']):
        print(f"\n✅ Bem-vindo, {usuario_encontrado['nome']}!")
        
        # ESSA PARTE RESOLVE O ATTRIBUTEERROR (transforma dict em classe)
        if usuario_encontrado.get('role') == 'admin':
            return models.Administrador(usuario_encontrado)
        else:
            return models.Usuario(usuario_encontrado)
    else:
        print("\n❌ E-mail ou senha incorretos!")
        return None