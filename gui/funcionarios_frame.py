import customtkinter as ctk
from gui.components import DataTable, FormPopup, ConfirmDialog
from services import funcionario_service
from config import COLOR_PRIMARY, COLOR_DANGER, COLOR_SUCCESS


class FuncionariosFrame(ctk.CTkFrame):
    """Tela de gestão de funcionários com tabela e CRUD."""

    def __init__(self, master, usuario):
        super().__init__(master, fg_color="transparent")
        self.usuario = usuario
        self._build()

    def _build(self):
        # Cabeçalho
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            header, text="🏢  Gestão de Funcionários",
            font=ctk.CTkFont(size=20, weight="bold"), anchor="w"
        ).pack(side="left")

        # Barra de ações
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=(0, 10))

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
            actions, text="+ Novo Funcionário", height=36,
            fg_color=COLOR_SUCCESS, hover_color="#27ae60",
            command=self._new_func
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            actions, text="✏️ Editar", height=36,
            fg_color="#f39c12", hover_color="#e67e22",
            command=self._edit_func
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            actions, text="🗑️ Deletar", height=36,
            fg_color=COLOR_DANGER, hover_color="#c0392b",
            command=self._delete_func
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            actions, text="🔄", width=36, height=36,
            command=self.refresh
        ).pack(side="right")

        # Feedback
        self.feedback = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.feedback.pack(padx=20, pady=(0, 5))

        # Tabela
        self.table = DataTable(
            self,
            columns=["ID", "Nome", "E-mail", "Telefone", "Localidade"],
            column_widths=[50, 150, 200, 120, 150],
            height=400
        )
        self.table.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self._load_data()

    def _load_data(self):
        self.table.clear()
        funcionarios = funcionario_service.listar_funcionarios()
        for f in funcionarios:
            end = f.get("endereco", {})
            localidade = f"{end.get('localidade', 'N/A')}-{end.get('uf', '')}"
            self.table.add_row(
                [f["id"], f["nome"][:20], f["email"][:25], f.get("telefone", ""), localidade],
                row_id=f["id"]
            )

    def _search(self):
        termo = self.search_entry.get().strip()
        if not termo:
            self._load_data()
            return
        self.table.clear()
        resultados = funcionario_service.buscar_funcionarios(termo)
        for f in resultados:
            end = f.get("endereco", {})
            localidade = f"{end.get('localidade', 'N/A')}-{end.get('uf', '')}"
            self.table.add_row(
                [f["id"], f["nome"][:20], f["email"][:25], f.get("telefone", ""), localidade],
                row_id=f["id"]
            )
        self._show_feedback(f"{len(resultados)} resultado(s).", success=True)

    def _new_func(self):
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
            sucesso, msg = funcionario_service.cadastrar_funcionario(
                dados.get("nome", ""), dados.get("email", ""),
                dados.get("telefone", ""), dados.get("senha", ""),
                dados.get("data_nasc", ""), endereco
            )
            if sucesso:
                self.refresh()
                self._show_feedback(msg, success=True)
            return sucesso, msg

        FormPopup(self, "Novo Funcionário", fields, on_save)

    def _edit_func(self):
        sel_id = self.table.get_selected_id()
        if not sel_id:
            self._show_feedback("Selecione um funcionário na tabela!", success=False)
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
                    funcionario_service.editar_funcionario(sel_id, campo, valor)
            self.refresh()
            self._show_feedback("Funcionário atualizado!", success=True)
            return True, "OK"

        FormPopup(self, f"Editar Funcionário ID {sel_id}", fields, on_save)

    def _delete_func(self):
        sel_id = self.table.get_selected_id()
        if not sel_id:
            self._show_feedback("Selecione um funcionário na tabela!", success=False)
            return

        def on_confirm():
            sucesso, msg = funcionario_service.deletar_funcionario(sel_id)
            self.refresh()
            self._show_feedback(msg, success=sucesso)

        ConfirmDialog(self, "Confirmar Deleção", f"Deletar funcionário ID {sel_id}?", on_confirm)

    def _show_feedback(self, msg, success=True):
        color = COLOR_SUCCESS if success else COLOR_DANGER
        self.feedback.configure(text=msg, text_color=color)
        self.after(4000, lambda: self.feedback.configure(text=""))

    def refresh(self):
        self._load_data()
