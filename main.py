import login
import cadastro


def menu_principal():
    while True:
        print("\n" + "═"*30)
        print("      SISTEMA DE GESTÃO")
        print("═"*30)
        print("1 - Cadastrar Usuário")
        print("2 - Logar na sua conta")
        print("3 - Sair")
        print("═"*30)

        opcao = input("Escolha uma opção: ")
        if opcao == "1":
            cadastro.cadastrar()
        elif opcao == "2":
            usuario = login.login()
            if usuario:
                cadastro.menu_usuario(usuario)
        elif opcao == "3":
            break

if __name__ == "__main__":
    menu_principal()