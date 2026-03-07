import customtkinter as ctk
from gui.components import DataTable, FormPopup, ConfirmDialog
from services import cliente_service
from config import COLOR_PRIMARY, COLOR_DANGER, COLOR_SUCCESS


class ClientesFrame(ctk.CTkFrame):
    """Tela de gestão de clientes com tabela e CRUD."""

    def __init__(self, master, usuario):
        super().__init__(master, fg_color="transparent")
        self.usuario = usuario
        self._build()

    def _build(self):
        # Cabeçalho
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            header, text="👥  Gestão de Clientes",
            font=ctk.CTkFont(size=20, weight="bold"), anchor="w"
        ).pack(side="left")

        # Barra de ações
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=(0, 10))

        # Busca
        self.search_entry = ctk.CTkEntry(
            actions, placeholder_text="🔍 Buscar por nome ou e-mail...",
            width=300, height=36
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self._search())

        ctk.CTkButton(
            actions, text="Buscar", width=80, height=36,
            command=self._search
        ).pack(side="left", padx=(0, 15))

        ctk.CTkButton(
            actions, text="+ Novo Cliente", height=36,
            fg_color=COLOR_SUCCESS, hover_color="#27ae60",
            command=self._new_client
        ).pack(side="left", padx=5)

        if self.usuario.eh_admin():
            ctk.CTkButton(
                actions, text="✏️ Editar", height=36,
                fg_color="#f39c12", hover_color="#e67e22",
                command=self._edit_client
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                actions, text="🗑️ Deletar", height=36,
                fg_color=COLOR_DANGER, hover_color="#c0392b",
                command=self._delete_client
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                actions, text="⬆️ Promover", height=36,
                fg_color="#8e44ad", hover_color="#7d3c98",
                command=self._promote_client
            ).pack(side="left", padx=5)

        ctk.CTkButton(
            actions, text="🔄", width=36, height=36,
            command=self.refresh
        ).pack(side="right")

        # Feedback
        self.feedback = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=12)
        )
        self.feedback.pack(padx=20, pady=(0, 5))

        # Tabela
        self.table = DataTable(
            self,
            columns=["ID", "Nome", "E-mail", "Cargo", "Localidade"],
            column_widths=[50, 150, 200, 90, 150],
            height=400
        )
        self.table.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self._load_data()

    def _load_data(self):
        """Carrega dados na tabela."""
        self.table.clear()
        clientes = cliente_service.listar_clientes()
        for c in clientes:
            end = c.get("endereco", {})
            localidade = f"{end.get('localidade', 'N/A')}-{end.get('uf', '')}"
            cargo = c.get('role', 'usuario').upper()
            self.table.add_row(
                [c["id"], c["nome"][:20], c["email"][:25], cargo, localidade],
                row_id=c["id"]
            )

    def _search(self):
        termo = self.search_entry.get().strip()
        if not termo:
            self._load_data()
            return
        self.table.clear()
        resultados = cliente_service.buscar_clientes(termo)
        for c in resultados:
            end = c.get("endereco", {})
            localidade = f"{end.get('localidade', 'N/A')}-{end.get('uf', '')}"
            cargo = c.get('role', 'usuario').upper()
            self.table.add_row(
                [c["id"], c["nome"][:20], c["email"][:25], cargo, localidade],
                row_id=c["id"]
            )
        self._show_feedback(f"{len(resultados)} resultado(s) encontrado(s).", success=True)

    def _new_client(self):
        fields = [
            {"label": "Nome", "key": "nome"},
            {"label": "E-mail", "key": "email"},
            {"label": "Telefone", "key": "telefone"},
            {"label": "Senha", "key": "senha", "type": "password"},
            {"label": "Data de Nascimento (dd/mm/aaaa)", "key": "data_nasc"},
            {"label": "CEP", "key": "cep", "type": "cep"},
            {"label": "Logradouro", "key": "logradouro"},
            {"label": "Bairro", "key": "bairro"},
            {"label": "Cidade", "key": "localidade"},
            {"label": "UF", "key": "uf"},
            {"label": "Número", "key": "numero"},
        ]

        def on_save(dados):
            endereco = {k: dados.get(k, "") for k in ("cep", "logradouro", "bairro", "localidade", "uf", "numero")}
            sucesso, msg = cliente_service.cadastrar_cliente(
                dados.get("nome", ""), dados.get("email", ""),
                dados.get("telefone", ""), dados.get("senha", ""),
                dados.get("data_nasc", ""), endereco
            )
            if sucesso:
                self.refresh()
                self._show_feedback(msg, success=True)
            return sucesso, msg

        FormPopup(self, "Novo Cliente", fields, on_save)

    def _edit_client(self):
        sel_id = self.table.get_selected_id()
        if not sel_id:
            self._show_feedback("Selecione um cliente na tabela!", success=False)
            return

        fields = [
            {"label": "Nome", "key": "nome"},
            {"label": "E-mail", "key": "email"},
            {"label": "Telefone", "key": "telefone"},
            {"label": "Nova Senha (deixe vazio para manter)", "key": "senha", "type": "password"},
        ]

        def on_save(dados):
            for campo, valor in dados.items():
                if valor.strip():
                    cliente_service.editar_cliente(sel_id, campo, valor)
            self.refresh()
            self._show_feedback("Cliente atualizado!", success=True)
            return True, "OK"

        FormPopup(self, f"Editar Cliente ID {sel_id}", fields, on_save)

    def _delete_client(self):
        sel_id = self.table.get_selected_id()
        if not sel_id:
            self._show_feedback("Selecione um cliente na tabela!", success=False)
            return

        def on_confirm():
            sucesso, msg = cliente_service.deletar_cliente(sel_id)
            self.refresh()
            self._show_feedback(msg, success=sucesso)

        ConfirmDialog(self, "Confirmar Deleção", f"Deseja realmente deletar o cliente ID {sel_id}?", on_confirm)

    def _promote_client(self):
        sel_id = self.table.get_selected_id()
        if not sel_id:
            self._show_feedback("Selecione um cliente na tabela!", success=False)
            return

        def on_confirm():
            sucesso, msg = cliente_service.promover_usuario(sel_id)
            self._show_feedback(msg, success=sucesso)

        ConfirmDialog(self, "Promover a Admin", f"Promover cliente ID {sel_id} a Administrador?", on_confirm)

    def _show_feedback(self, msg, success=True):
        color = COLOR_SUCCESS if success else COLOR_DANGER
        self.feedback.configure(text=msg, text_color=color)
        self.after(4000, lambda: self.feedback.configure(text=""))

    def refresh(self):
        self._load_data()
