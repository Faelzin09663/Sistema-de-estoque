import customtkinter as ctk
from config import APP_TITLE, APP_WIDTH, APP_HEIGHT, COLOR_BG_SIDEBAR, COLOR_SUCCESS, COLOR_DANGER
from services import cliente_service
from gui.login_frame import LoginFrame
from gui.dashboard_frame import DashboardFrame
from gui.clientes_frame import ClientesFrame
from gui.funcionarios_frame import FuncionariosFrame
from gui.estoque_frame import EstoqueFrame


class App(ctk.CTk):
    """Janela principal do sistema ERP com sidebar de navegação."""

    def __init__(self):
        super().__init__()

        # Configuração da janela
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title(APP_TITLE)
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.minsize(900, 600)

        self.usuario = None
        self.current_frame = None
        self.sidebar_buttons = {}

        # Layout principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Mostra login
        self._show_login()

    def _show_login(self):
        """Mostra a tela de login (tela cheia, sem sidebar)."""
        self.usuario = None
        self._clear_all()

        self.login_frame = LoginFrame(self, on_login_success=self._on_login)
        self.login_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

    def _on_login(self, usuario):
        """Callback quando login é bem-sucedido."""
        self.usuario = usuario
        self._clear_all()
        self._build_sidebar()
        self._navigate("dashboard")

    def _clear_all(self):
        """Remove todos os widgets."""
        for widget in self.winfo_children():
            widget.destroy()
        self.sidebar_buttons = {}

    def _build_sidebar(self):
        """Constrói a sidebar de navegação."""
        self.sidebar = ctk.CTkFrame(self, width=200, fg_color=COLOR_BG_SIDEBAR, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(20, 5))

        ctk.CTkLabel(
            logo_frame, text="🏢 ERP",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#e0e0e0"
        ).pack()

        # Info do usuário
        user_frame = ctk.CTkFrame(self.sidebar, fg_color="#1a2744", corner_radius=8)
        user_frame.pack(fill="x", padx=12, pady=(8, 15))

        ctk.CTkLabel(
            user_frame, text=f"👤 {self.usuario.nome[:16]}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#e0e0e0"
        ).pack(pady=(8, 2))

        cargo_color = "#f39c12" if self.usuario.eh_admin() else "#90a4ae"
        ctk.CTkLabel(
            user_frame, text=self.usuario.cargo.upper(),
            font=ctk.CTkFont(size=10),
            text_color=cargo_color
        ).pack(pady=(0, 8))

        # Separador
        ctk.CTkFrame(self.sidebar, height=1, fg_color="#2a3a5c").pack(fill="x", padx=12, pady=5)

        # Botões de navegação
        nav_items = [
            ("📊  Dashboard", "dashboard"),
            ("👥  Clientes", "clientes"),
        ]

        if self.usuario.eh_admin():
            nav_items.append(("🏢  Funcionários", "funcionarios"))

        nav_items.append(("📦  Estoque", "estoque"))

        for text, key in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=text, height=40,
                font=ctk.CTkFont(size=14),
                fg_color="transparent", text_color="#b0bec5",
                hover_color="#1a3a5c", anchor="w",
                command=lambda k=key: self._navigate(k)
            )
            btn.pack(fill="x", padx=8, pady=2)
            self.sidebar_buttons[key] = btn

        # Spacer
        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        # Separador inferior
        ctk.CTkFrame(self.sidebar, height=1, fg_color="#2a3a5c").pack(fill="x", padx=12, pady=5)

        # Meus dados
        ctk.CTkButton(
            self.sidebar, text="⚙️  Meus Dados", height=36,
            font=ctk.CTkFont(size=13),
            fg_color="transparent", text_color="#78909c",
            hover_color="#1a3a5c", anchor="w",
            command=self._show_my_data
        ).pack(fill="x", padx=8, pady=2)

        # Token vendedor (somente admin)
        if self.usuario.eh_admin():
            ctk.CTkButton(
                self.sidebar, text="🔑  Token Vendedor", height=36,
                font=ctk.CTkFont(size=13),
                fg_color="transparent", text_color="#f39c12",
                hover_color="#3d2e0f", anchor="w",
                command=self._set_token_vendedor
            ).pack(fill="x", padx=8, pady=2)

        # Logout
        ctk.CTkButton(
            self.sidebar, text="🚪  Sair", height=36,
            font=ctk.CTkFont(size=13),
            fg_color="transparent", text_color="#e57373",
            hover_color="#3d1f1f", anchor="w",
            command=self._logout
        ).pack(fill="x", padx=8, pady=(2, 15))

    def _navigate(self, page):
        """Troca o frame de conteúdo."""
        # Highlight sidebar
        for key, btn in self.sidebar_buttons.items():
            if key == page:
                btn.configure(fg_color="#0f3460", text_color="#e0e0e0")
            else:
                btn.configure(fg_color="transparent", text_color="#b0bec5")

        # Destroi frame atual
        if self.current_frame:
            self.current_frame.destroy()

        # Cria novo frame
        if page == "dashboard":
            self.current_frame = DashboardFrame(self, self.usuario)
        elif page == "clientes":
            self.current_frame = ClientesFrame(self, self.usuario)
        elif page == "funcionarios":
            self.current_frame = FuncionariosFrame(self, self.usuario)
        elif page == "estoque":
            self.current_frame = EstoqueFrame(self, self.usuario)

        if self.current_frame:
            self.current_frame.grid(row=0, column=1, sticky="nsew")

    def _show_my_data(self):
        """Mostra dados do usuário logado em popup."""
        if self.current_frame:
            self.current_frame.destroy()

        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=0, column=1, sticky="nsew")
        self.current_frame = frame

        container = ctk.CTkFrame(frame, fg_color="#16213e", corner_radius=16, width=500)
        container.place(relx=0.5, rely=0.4, anchor="center")

        ctk.CTkLabel(
            container, text="📋  Meus Dados Pessoais",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(25, 15))

        dados = [
            ("ID", str(self.usuario.id)),
            ("Nome", self.usuario.nome),
            ("E-mail", self.usuario.email),
            ("Telefone", self.usuario.telefone or "N/A"),
            ("Cargo", self.usuario.cargo.upper()),
            ("Nascimento", getattr(self.usuario, 'data_nascimento', 'N/A')),
        ]

        end = getattr(self.usuario, 'endereco', {})
        if end:
            logradouro = end.get('logradouro', 'N/A')
            numero = end.get('numero', 'S/N')
            cidade = end.get('localidade', 'N/A')
            uf = end.get('uf', '')
            cep = end.get('cep', 'N/A')
            dados.append(("Endereço", f"{logradouro}, {numero}"))
            dados.append(("Cidade/UF", f"{cidade}/{uf} — CEP: {cep}"))

        for label, value in dados:
            row = ctk.CTkFrame(container, fg_color="transparent")
            row.pack(fill="x", padx=25, pady=3)
            ctk.CTkLabel(row, text=f"{label}:", font=ctk.CTkFont(size=13, weight="bold"),
                         text_color="#90a4ae", width=100, anchor="e").pack(side="left", padx=(0, 10))
            ctk.CTkLabel(row, text=value, font=ctk.CTkFont(size=13),
                         anchor="w").pack(side="left")

        ctk.CTkLabel(container, text="").pack(pady=10)

        # Reset sidebar highlights
        for btn in self.sidebar_buttons.values():
            btn.configure(fg_color="transparent", text_color="#b0bec5")

    def _logout(self):
        """Faz logout e volta para a tela de login."""
        self._show_login()

    def _set_token_vendedor(self):
        """Tela para admin definir/alterar o token de vendedor."""
        if self.current_frame:
            self.current_frame.destroy()

        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=0, column=1, sticky="nsew")
        self.current_frame = frame

        container = ctk.CTkFrame(frame, fg_color="#16213e", corner_radius=16, width=450)
        container.place(relx=0.5, rely=0.4, anchor="center")

        ctk.CTkLabel(
            container, text="🔑  Token de Vendedor",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(25, 10))

        ctk.CTkLabel(
            container, text="Defina um token que vendedores usarão\npara criar suas contas.",
            font=ctk.CTkFont(size=13), text_color="#90a4ae",
            justify="center"
        ).pack(pady=(0, 15))

        # Token atual
        token_atual = cliente_service.get_vendedor_token()
        ctk.CTkLabel(
            container, text=f"Token atual: {token_atual or '(nenhum definido)'}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#f39c12" if token_atual else "#e57373"
        ).pack(pady=(0, 15))

        # Novo token
        ctk.CTkLabel(
            container, text="Novo Token:",
            font=ctk.CTkFont(size=12), anchor="w"
        ).pack(fill="x", padx=30, pady=(0, 3))

        token_entry = ctk.CTkEntry(container, height=40, placeholder_text="Digite o novo token...")
        token_entry.pack(fill="x", padx=30, pady=(0, 10))

        feedback = ctk.CTkLabel(container, text="", font=ctk.CTkFont(size=12))
        feedback.pack(pady=5)

        def salvar_token():
            novo = token_entry.get().strip()
            sucesso, msg = cliente_service.set_vendedor_token(novo)
            if sucesso:
                feedback.configure(text=f"✅ {msg}", text_color=COLOR_SUCCESS)
            else:
                feedback.configure(text=f"❌ {msg}", text_color=COLOR_DANGER)

        ctk.CTkButton(
            container, text="Salvar Token", height=40,
            fg_color="#f39c12", hover_color="#e67e22",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=salvar_token
        ).pack(padx=30, pady=(5, 25))

        # Reset sidebar highlights
        for btn in self.sidebar_buttons.values():
            btn.configure(fg_color="transparent", text_color="#b0bec5")
