import customtkinter as ctk
from gui.components import DataTable, FormPopup, ConfirmDialog
from services import estoque_service
from config import COLOR_PRIMARY, COLOR_DANGER, COLOR_SUCCESS, COLOR_WARNING, ALERTA_ESTOQUE_BAIXO


class EstoqueFrame(ctk.CTkFrame):
    """Tela de gestão de estoque com tabela, CRUD e saída."""

    def __init__(self, master, usuario):
        super().__init__(master, fg_color="transparent")
        self.usuario = usuario
        self._build()

    def _build(self):
        # Cabeçalho
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            header, text="📦  Gestão de Estoque",
            font=ctk.CTkFont(size=20, weight="bold"), anchor="w"
        ).pack(side="left")

        # Barra de ações
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=(0, 10))

        self.search_entry = ctk.CTkEntry(
            actions, placeholder_text="🔍 Buscar produto...",
            width=250, height=36
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self._search())

        ctk.CTkButton(
            actions, text="Buscar", width=80, height=36,
            command=self._search
        ).pack(side="left", padx=(0, 15))

        if self.usuario.eh_admin():
            ctk.CTkButton(
                actions, text="+ Novo Produto", height=36,
                fg_color=COLOR_SUCCESS, hover_color="#27ae60",
                command=self._new_product
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                actions, text="✏️ Editar", height=36,
                fg_color="#f39c12", hover_color="#e67e22",
                command=self._edit_product
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                actions, text="🗑️ Deletar", height=36,
                fg_color=COLOR_DANGER, hover_color="#c0392b",
                command=self._delete_product
            ).pack(side="left", padx=5)

        ctk.CTkButton(
            actions, text="📤 Registrar Saída", height=36,
            fg_color="#2980b9", hover_color="#2471a3",
            command=self._registrar_saida
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
            columns=["ID", "Produto", "Quantidade", "Preço", "Descrição"],
            column_widths=[50, 180, 100, 100, 250],
            height=400
        )
        self.table.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self._load_data()

    def _load_data(self):
        self.table.clear()
        produtos = estoque_service.listar_produtos()
        for p in produtos:
            qtd_text = str(p["quantidade"])
            if p["quantidade"] <= ALERTA_ESTOQUE_BAIXO:
                qtd_text = f"⚠️ {p['quantidade']}"
            self.table.add_row(
                [p["id"], p["nome"], qtd_text, f"R$ {p['preco']:.2f}", p.get("descricao", "")],
                row_id=p["id"]
            )

    def _search(self):
        termo = self.search_entry.get().strip()
        if not termo:
            self._load_data()
            return
        self.table.clear()
        resultados = estoque_service.buscar_produtos(termo)
        for p in resultados:
            qtd_text = f"⚠️ {p['quantidade']}" if p["quantidade"] <= ALERTA_ESTOQUE_BAIXO else str(p["quantidade"])
            self.table.add_row(
                [p["id"], p["nome"], qtd_text, f"R$ {p['preco']:.2f}", p.get("descricao", "")],
                row_id=p["id"]
            )
        self._show_feedback(f"{len(resultados)} produto(s) encontrado(s).", success=True)

    def _new_product(self):
        fields = [
            {"label": "Nome do Produto", "key": "nome"},
            {"label": "Quantidade", "key": "quantidade"},
            {"label": "Preço (R$)", "key": "preco"},
            {"label": "Descrição", "key": "descricao"},
        ]

        def on_save(dados):
            sucesso, msg = estoque_service.cadastrar_produto(
                dados.get("nome", ""), dados.get("quantidade", ""),
                dados.get("preco", ""), dados.get("descricao", "")
            )
            if sucesso:
                self.refresh()
                self._show_feedback(msg, success=True)
            return sucesso, msg

        FormPopup(self, "Novo Produto", fields, on_save)

    def _edit_product(self):
        sel_id = self.table.get_selected_id()
        if not sel_id:
            self._show_feedback("Selecione um produto na tabela!", success=False)
            return

        fields = [
            {"label": "Nome", "key": "nome"},
            {"label": "Quantidade", "key": "quantidade"},
            {"label": "Preço (R$)", "key": "preco"},
            {"label": "Descrição", "key": "descricao"},
        ]

        def on_save(dados):
            for campo, valor in dados.items():
                if valor.strip():
                    estoque_service.editar_produto(sel_id, campo, valor)
            self.refresh()
            self._show_feedback("Produto atualizado!", success=True)
            return True, "OK"

        FormPopup(self, f"Editar Produto ID {sel_id}", fields, on_save)

    def _delete_product(self):
        sel_id = self.table.get_selected_id()
        if not sel_id:
            self._show_feedback("Selecione um produto na tabela!", success=False)
            return

        def on_confirm():
            sucesso, msg = estoque_service.deletar_produto(sel_id)
            self.refresh()
            self._show_feedback(msg, success=sucesso)

        ConfirmDialog(self, "Confirmar Deleção", f"Deletar produto ID {sel_id}?", on_confirm)

    def _registrar_saida(self):
        sel_id = self.table.get_selected_id()
        if not sel_id:
            self._show_feedback("Selecione um produto na tabela!", success=False)
            return

        fields = [
            {"label": "Quantidade para retirar", "key": "quantidade"},
        ]

        def on_save(dados):
            sucesso, msg = estoque_service.registrar_saida(
                sel_id, dados.get("quantidade", "0"), self.usuario.nome
            )
            if sucesso:
                self.refresh()
                self._show_feedback(msg, success=True)
            return sucesso, msg

        FormPopup(self, f"Registrar Saída — Produto ID {sel_id}", fields, on_save)

    def _show_feedback(self, msg, success=True):
        color = COLOR_SUCCESS if success else COLOR_DANGER
        self.feedback.configure(text=msg, text_color=color)
        self.after(4000, lambda: self.feedback.configure(text=""))

    def refresh(self):
        self._load_data()
