import customtkinter as ctk
from gui.components import StatCard
from services import cliente_service, funcionario_service, estoque_service
from config import COLOR_DANGER, COLOR_WARNING


class DashboardFrame(ctk.CTkFrame):
    """Painel de estatísticas e visão geral do sistema."""

    def __init__(self, master, usuario):
        super().__init__(master, fg_color="transparent")
        self.usuario = usuario
        self._build()

    def _build(self):
        # Título
        ctk.CTkLabel(
            self, text=f"📊  Dashboard — Bem-vindo(a), {self.usuario.nome}!",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        ).pack(fill="x", padx=20, pady=(20, 15))

        # --- Cards de estatísticas ---
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", padx=20, pady=(0, 15))

        stats_clientes = cliente_service.get_dashboard_clientes()
        stats_func = funcionario_service.get_dashboard_funcionarios()
        stats_est = estoque_service.get_dashboard_estoque()

        cards_data = [
            ("Clientes", stats_clientes["total"], "👥", "#0f3460"),
            ("Funcionários", stats_func["total"], "🏢", "#1a5276"),
            ("Produtos", stats_est["total_produtos"], "📦", "#1b4332"),
            ("Itens em Estoque", stats_est["total_itens"], "🔢", "#2c3e50"),
        ]

        for i, (title, value, icon, color) in enumerate(cards_data):
            card = StatCard(cards_frame, title=title, value=value, icon=icon, color=color)
            card.grid(row=0, column=i, padx=8, pady=5, sticky="nsew")

        for i in range(len(cards_data)):
            cards_frame.columnconfigure(i, weight=1)

        # --- Linha 2: Valor e Alertas ---
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=(0, 15))

        valor_card = StatCard(
            info_frame, title="Valor Total Estoque",
            value=f"R$ {stats_est['valor_total']:,.2f}",
            icon="💰", color="#1a3c34"
        )
        valor_card.grid(row=0, column=0, padx=8, pady=5, sticky="nsew")

        alerta_color = COLOR_DANGER if stats_est["alertas"] > 0 else "#1b4332"
        alerta_card = StatCard(
            info_frame, title="Alertas Estoque Baixo",
            value=stats_est["alertas"],
            icon="⚠️", color=alerta_color
        )
        alerta_card.grid(row=0, column=1, padx=8, pady=5, sticky="nsew")

        if self.usuario.eh_admin():
            adultos_card = StatCard(
                info_frame, title="Clientes Adultos",
                value=stats_clientes["adultos"],
                icon="🧑", color="#2c3e50"
            )
            adultos_card.grid(row=0, column=2, padx=8, pady=5, sticky="nsew")

            menores_card = StatCard(
                info_frame, title="Clientes Menores",
                value=stats_clientes["menores"],
                icon="👶", color="#2c3e50"
            )
            menores_card.grid(row=0, column=3, padx=8, pady=5, sticky="nsew")

        for i in range(4):
            info_frame.columnconfigure(i, weight=1)

        # --- Alertas de estoque baixo ---
        alertas = estoque_service.get_alertas_estoque()
        if alertas:
            alert_frame = ctk.CTkFrame(self, fg_color="#3d1f1f", corner_radius=10)
            alert_frame.pack(fill="x", padx=20, pady=(5, 10))

            ctk.CTkLabel(
                alert_frame, text="⚠️  Produtos com estoque baixo:",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLOR_WARNING, anchor="w"
            ).pack(fill="x", padx=15, pady=(10, 5))

            for p in alertas:
                ctk.CTkLabel(
                    alert_frame,
                    text=f"  • {p['nome']} — {p['quantidade']} restante(s)",
                    font=ctk.CTkFont(size=12),
                    text_color="#e0e0e0", anchor="w"
                ).pack(fill="x", padx=15, pady=1)

            ctk.CTkLabel(alert_frame, text="").pack(pady=3)  # spacer

        # --- Distribuição por estado ---
        if self.usuario.eh_admin() and stats_clientes["por_estado"]:
            estado_frame = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=10)
            estado_frame.pack(fill="x", padx=20, pady=5)

            ctk.CTkLabel(
                estado_frame, text="🗺️  Distribuição de Clientes por Estado",
                font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
            ).pack(fill="x", padx=15, pady=(10, 5))

            for uf, count in sorted(stats_clientes["por_estado"].items()):
                ctk.CTkLabel(
                    estado_frame,
                    text=f"  {uf}: {count} cliente(s)",
                    font=ctk.CTkFont(size=12), anchor="w"
                ).pack(fill="x", padx=15, pady=1)

            ctk.CTkLabel(estado_frame, text="").pack(pady=5)

    def refresh(self):
        """Recarrega o dashboard."""
        for widget in self.winfo_children():
            widget.destroy()
        self._build()
