import customtkinter as ctk
from services import auth_service, cliente_service, funcionario_service
from config import COLOR_PRIMARY, COLOR_DANGER


class LoginFrame(ctk.CTkFrame):
    """Tela de login e criação de conta."""

    def __init__(self, master, on_login_success):
        super().__init__(master, fg_color="transparent")
        self.on_login_success = on_login_success
        self.showing_register = False
        self._build_login()

    def _build_login(self):
        """Monta a interface de login."""
        for widget in self.winfo_children():
            widget.destroy()
        self.showing_register = False

        # Container central
        container = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=16, width=400)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Logo/Título
        ctk.CTkLabel(
            container, text="🏢",
            font=ctk.CTkFont(size=48)
        ).pack(pady=(30, 5))

        ctk.CTkLabel(
            container, text="Sistema ERP Corporativo",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#e0e0e0"
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            container, text="Faça login para continuar",
            font=ctk.CTkFont(size=13),
            text_color="#90a4ae"
        ).pack(pady=(0, 25))

        # Campos
        self.email_entry = ctk.CTkEntry(
            container, placeholder_text="E-mail",
            width=320, height=42, font=ctk.CTkFont(size=14)
        )
        self.email_entry.pack(pady=6, padx=40)

        self.senha_entry = ctk.CTkEntry(
            container, placeholder_text="Senha", show="•",
            width=320, height=42, font=ctk.CTkFont(size=14)
        )
        self.senha_entry.pack(pady=6, padx=40)
        self.senha_entry.bind("<Return>", lambda e: self._do_login())

        # Feedback
        self.feedback = ctk.CTkLabel(
            container, text="", font=ctk.CTkFont(size=12),
            text_color=COLOR_DANGER
        )
        self.feedback.pack(pady=5)

        # Botão login
        ctk.CTkButton(
            container, text="Entrar", width=320, height=42,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=COLOR_PRIMARY, hover_color="#1565c0",
            command=self._do_login
        ).pack(pady=(5, 8), padx=40)

        # Link criar conta
        ctk.CTkButton(
            container, text="Criar nova conta",
            fg_color="transparent", text_color="#64b5f6",
            hover_color="#1a2744", font=ctk.CTkFont(size=13),
            command=self._show_register
        ).pack(pady=(0, 25))

    def _do_login(self):
        email = self.email_entry.get().strip()
        senha = self.senha_entry.get()

        if not email or not senha:
            self.feedback.configure(text="Preencha todos os campos!", text_color=COLOR_DANGER)
            return

        usuario, msg = auth_service.login(email, senha)
        if usuario:
            self.on_login_success(usuario)
        else:
            self.feedback.configure(text=f"❌ {msg}", text_color=COLOR_DANGER)

    def _show_register(self):
        """Troca para formulário de cadastro."""
        for widget in self.winfo_children():
            widget.destroy()
        self.showing_register = True

        container = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=16, width=420)
        container.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            container, text="📋 Criar Conta",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(25, 10))

        # Seletor de tipo de conta
        ctk.CTkLabel(
            container, text="Tipo de Conta:",
            font=ctk.CTkFont(size=13), text_color="#90a4ae"
        ).pack(pady=(0, 5))

        self.tipo_conta_var = ctk.StringVar(value="Cliente")
        self.tipo_selector = ctk.CTkSegmentedButton(
            container, values=["Cliente", "Vendedor"],
            variable=self.tipo_conta_var,
            command=self._on_tipo_change,
            font=ctk.CTkFont(size=13)
        )
        self.tipo_selector.pack(padx=30, pady=(0, 5))

        # Frame do token (aparece só quando Vendedor)
        self.token_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.token_entry = ctk.CTkEntry(
            self.token_frame, placeholder_text="Token de Vendedor (dado pelo admin)",
            height=34
        )
        self.token_entry.pack(fill="x", padx=30)
        # Inicialmente escondido
        self.token_frame.pack_forget()

        form = ctk.CTkScrollableFrame(container, fg_color="transparent", height=300, width=350)
        form.pack(padx=30)

        fields = [
            ("Nome", "nome"), ("E-mail", "email"), ("Telefone", "telefone"),
            ("Senha", "senha"), ("Data de Nascimento", "data_nasc"),
            ("CEP", "cep"), ("Logradouro", "logradouro"), ("Bairro", "bairro"),
            ("Cidade", "localidade"), ("UF", "uf"), ("Número", "numero")
        ]

        self.reg_entries = {}
        for label, key in fields:
            ctk.CTkLabel(form, text=label, font=ctk.CTkFont(size=12), anchor="w").pack(fill="x", pady=(6, 1))
            if key == "senha":
                entry = ctk.CTkEntry(form, show="•", height=34)
                entry.pack(fill="x", pady=(0, 2))
            elif key == "cep":
                cep_frame = ctk.CTkFrame(form, fg_color="transparent")
                cep_frame.pack(fill="x", pady=(0, 2))
                entry = ctk.CTkEntry(cep_frame, height=34)
                entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
                ctk.CTkButton(
                    cep_frame, text="🔍 Buscar", width=90, height=34,
                    fg_color="#2980b9", hover_color="#2471a3",
                    command=self._auto_cep
                ).pack(side="right")
            else:
                entry = ctk.CTkEntry(form, height=34)
                entry.pack(fill="x", pady=(0, 2))
            self.reg_entries[key] = entry

        self.reg_feedback = ctk.CTkLabel(
            container, text="", font=ctk.CTkFont(size=12), text_color=COLOR_DANGER
        )
        self.reg_feedback.pack(pady=5)

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=(0, 20))

        ctk.CTkButton(
            btn_frame, text="← Voltar", fg_color="#555",
            hover_color="#777", command=self._build_login
        ).pack(side="left", expand=True, padx=5)

        ctk.CTkButton(
            btn_frame, text="Cadastrar", fg_color="#2ecc71",
            hover_color="#27ae60", command=self._do_register
        ).pack(side="right", expand=True, padx=5)

    def _on_tipo_change(self, value):
        """Mostra/esconde campo de token baseado no tipo de conta."""
        if value == "Vendedor":
            self.token_frame.pack(after=self.tipo_selector, fill="x", pady=(5, 5))
        else:
            self.token_frame.pack_forget()

    def _auto_cep(self):
        """Busca CEP via botão e preenche campos de endereço."""
        cep = self.reg_entries["cep"].get().strip().replace("-", "")
        if len(cep) != 8:
            self.reg_feedback.configure(text="CEP deve ter 8 dígitos!", text_color=COLOR_DANGER)
            return

        self.reg_feedback.configure(text="🔄 Buscando CEP...", text_color="#90a4ae")
        self.update()

        res = cliente_service.consultar_cep(cep)
        if res:
            for key in ("logradouro", "bairro", "localidade", "uf"):
                entry = self.reg_entries.get(key)
                if entry and res.get(key):
                    entry.delete(0, "end")
                    entry.insert(0, res[key])
            self.reg_feedback.configure(
                text=f"✅ Endereço encontrado: {res.get('localidade', '')}-{res.get('uf', '')}",
                text_color="#2ecc71"
            )
        else:
            self.reg_feedback.configure(text="❌ CEP não encontrado. Preencha manualmente.", text_color=COLOR_DANGER)

    def _do_register(self):
        """Executa o cadastro."""
        dados = {k: e.get().strip() for k, e in self.reg_entries.items()}

        if not all([dados.get("nome"), dados.get("email"), dados.get("senha")]):
            self.reg_feedback.configure(text="Preencha nome, e-mail e senha!", text_color=COLOR_DANGER)
            return

        # Tipo de conta e token
        tipo = self.tipo_conta_var.get().lower()  # "cliente" ou "vendedor"
        token = self.token_entry.get().strip() if tipo == "vendedor" else None

        endereco = {
            "cep": dados.get("cep", ""),
            "logradouro": dados.get("logradouro", ""),
            "bairro": dados.get("bairro", ""),
            "localidade": dados.get("localidade", ""),
            "uf": dados.get("uf", ""),
            "numero": dados.get("numero", "")
        }

        sucesso, msg = False, ""

        if tipo == "vendedor":
            # Vendedor vai para funcionarios.json
            sucesso, msg = funcionario_service.cadastrar_vendedor(
                dados["nome"], dados["email"], dados["telefone"],
                dados["senha"], dados.get("data_nasc", ""), endereco,
                token_vendedor=token
            )
        else:
            # Cliente vai para cadastro.json
            sucesso, msg = cliente_service.cadastrar_cliente(
                dados["nome"], dados["email"], dados["telefone"],
                dados["senha"], dados.get("data_nasc", ""), endereco
            )

        if sucesso:
            self.reg_feedback.configure(text=f"✅ {msg}", text_color="#2ecc71")
            self.after(1500, self._build_login)
        else:
            self.reg_feedback.configure(text=f"❌ {msg}", text_color=COLOR_DANGER)
