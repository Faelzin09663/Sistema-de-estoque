import customtkinter as ctk
from config import COLOR_DANGER, COLOR_SUCCESS


class DataTable(ctk.CTkScrollableFrame):
    """Tabela de dados reutilizável com scroll e seleção."""

    def __init__(self, master, columns, column_widths=None, **kwargs):
        super().__init__(master, **kwargs)
        self.columns = columns
        self.column_widths = column_widths or [120] * len(columns)
        self.rows_data = []
        self.selected_id = None
        self.row_frames = []

        # Cabeçalho
        header_frame = ctk.CTkFrame(self, fg_color="#1a3a5c", corner_radius=0)
        header_frame.pack(fill="x", pady=(0, 2))

        for i, col in enumerate(columns):
            lbl = ctk.CTkLabel(
                header_frame, text=col, width=self.column_widths[i],
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#90caf9"
            )
            lbl.pack(side="left", padx=5, pady=6)

    def clear(self):
        """Remove todas as linhas."""
        for frame in self.row_frames:
            frame.destroy()
        self.row_frames = []
        self.rows_data = []
        self.selected_id = None

    def add_row(self, values, row_id=None):
        """Adiciona uma linha. row_id é o identificador para seleção."""
        row_color = "#1e2a3a" if len(self.row_frames) % 2 == 0 else "#243447"
        row_frame = ctk.CTkFrame(self, fg_color=row_color, corner_radius=4, height=36)
        row_frame.pack(fill="x", pady=1)
        row_frame.pack_propagate(False)

        for i, val in enumerate(values):
            width = self.column_widths[i] if i < len(self.column_widths) else 120
            lbl = ctk.CTkLabel(
                row_frame, text=str(val), width=width,
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            lbl.pack(side="left", padx=5, pady=4)
            lbl.bind("<Button-1>", lambda e, rid=row_id, rf=row_frame: self._select_row(rid, rf))

        row_frame.bind("<Button-1>", lambda e, rid=row_id, rf=row_frame: self._select_row(rid, rf))
        self.row_frames.append(row_frame)
        self.rows_data.append({"id": row_id, "values": values})

    def _select_row(self, row_id, row_frame):
        """Seleciona uma linha visualmente."""
        for i, rf in enumerate(self.row_frames):
            color = "#1e2a3a" if i % 2 == 0 else "#243447"
            rf.configure(fg_color=color)
        row_frame.configure(fg_color="#0f3460")
        self.selected_id = row_id

    def get_selected_id(self):
        return self.selected_id

    def load_data(self, data_list, id_key="id", display_keys=None):
        """Carrega dados de uma lista de dicts."""
        self.clear()
        if not display_keys:
            display_keys = self.columns
        for item in data_list:
            values = []
            for key in display_keys:
                val = item.get(key, "")
                if isinstance(val, dict):
                    val = f"{val.get('localidade', 'N/A')}-{val.get('uf', '')}"
                values.append(val)
            self.add_row(values, row_id=item.get(id_key))


class StatCard(ctk.CTkFrame):
    """Card de estatística para dashboards."""

    def __init__(self, master, title, value, icon="📊", color="#0f3460", **kwargs):
        super().__init__(master, fg_color=color, corner_radius=12, **kwargs)
        self.configure(height=100)
        ctk.CTkLabel(self, text=icon, font=ctk.CTkFont(size=28)).pack(pady=(12, 2))
        ctk.CTkLabel(self, text=str(value), font=ctk.CTkFont(size=24, weight="bold"),
                     text_color="#e0e0e0").pack()
        ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=11),
                     text_color="#90a4ae").pack(pady=(0, 10))


class FormPopup(ctk.CTkToplevel):
    """Popup modal reutilizável para formulários."""

    def __init__(self, master, title, fields, callback, **kwargs):
        """
        fields: list of dict → [{"label": "Nome", "key": "nome", "type": "entry"}, ...]
                type: "entry", "password", "combo", "cep"
        callback: função chamada com dict dos valores
        """
        super().__init__(master, **kwargs)
        self.title(title)
        self.geometry("450x550")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.callback = callback
        self.entries = {}

        ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 15))

        form_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20)

        for field in fields:
            ctk.CTkLabel(form_frame, text=field["label"], font=ctk.CTkFont(size=12),
                         anchor="w").pack(fill="x", pady=(8, 2))

            if field.get("type") == "cep":
                # Campo CEP com botão de busca
                cep_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
                cep_frame.pack(fill="x", pady=(0, 4))
                entry = ctk.CTkEntry(cep_frame, height=36)
                entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
                ctk.CTkButton(
                    cep_frame, text="🔍 Buscar", width=90, height=36,
                    fg_color="#2980b9", hover_color="#2471a3",
                    command=lambda: self._buscar_cep()
                ).pack(side="right")
            elif field.get("type") == "password":
                entry = ctk.CTkEntry(form_frame, show="•", height=36)
                entry.pack(fill="x", pady=(0, 4))
            elif field.get("type") == "combo":
                entry = ctk.CTkComboBox(form_frame, values=field.get("options", []))
                entry.pack(fill="x", pady=(0, 4))
            else:
                entry = ctk.CTkEntry(form_frame, height=36)
                entry.pack(fill="x", pady=(0, 4))

            if field.get("default"):
                if hasattr(entry, 'insert'):
                    entry.insert(0, field["default"])
                elif hasattr(entry, 'set'):
                    entry.set(field["default"])

            self.entries[field["key"]] = entry

        # Feedback
        self.feedback_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12),
                                           text_color=COLOR_DANGER)
        self.feedback_label.pack(pady=5)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkButton(btn_frame, text="Cancelar", fg_color="#555",
                      hover_color="#777", command=self.destroy).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_frame, text="Salvar", fg_color=COLOR_SUCCESS,
                      hover_color="#27ae60", command=self._submit).pack(side="right", expand=True, padx=5)

    def _buscar_cep(self):
        """Busca CEP via API e preenche os campos de endereço."""
        cep_entry = self.entries.get("cep")
        if not cep_entry:
            return

        cep = cep_entry.get().strip().replace("-", "")
        if len(cep) != 8:
            self.feedback_label.configure(text="CEP deve ter 8 dígitos!", text_color=COLOR_DANGER)
            return

        self.feedback_label.configure(text="🔄 Buscando CEP...", text_color="#90a4ae")
        self.update()

        try:
            from services.cliente_service import consultar_cep
            res = consultar_cep(cep)
            if res:
                campos_map = {"logradouro": "logradouro", "bairro": "bairro",
                              "localidade": "localidade", "uf": "uf"}
                for api_key, entry_key in campos_map.items():
                    entry = self.entries.get(entry_key)
                    if entry and res.get(api_key):
                        entry.delete(0, "end")
                        entry.insert(0, res[api_key])
                self.feedback_label.configure(
                    text=f"✅ CEP encontrado: {res.get('localidade', '')}-{res.get('uf', '')}",
                    text_color=COLOR_SUCCESS
                )
            else:
                self.feedback_label.configure(text="❌ CEP não encontrado.", text_color=COLOR_DANGER)
        except Exception as e:
            self.feedback_label.configure(text=f"❌ Erro ao buscar CEP: {e}", text_color=COLOR_DANGER)


    def _submit(self):
        """Coleta valores e chama o callback."""
        dados = {}
        for key, entry in self.entries.items():
            if isinstance(entry, ctk.CTkComboBox):
                dados[key] = entry.get()
            else:
                dados[key] = entry.get()
        result = self.callback(dados)
        if result:
            sucesso, msg = result
            if sucesso:
                self.destroy()
            else:
                self.feedback_label.configure(text=msg, text_color=COLOR_DANGER)


class ConfirmDialog(ctk.CTkToplevel):
    """Diálogo de confirmação Sim/Não."""

    def __init__(self, master, title, message, callback):
        super().__init__(master)
        self.title(title)
        self.geometry("350x180")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        ctk.CTkLabel(
            self, text=message,
            font=ctk.CTkFont(size=14),
            wraplength=300
        ).pack(pady=(30, 20))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=(0, 20))

        ctk.CTkButton(
            btn_frame, text="Não", fg_color="#555",
            hover_color="#777", command=self.destroy
        ).pack(side="left", expand=True, padx=5)

        def confirm():
            callback()
            self.destroy()

        ctk.CTkButton(
            btn_frame, text="Sim", fg_color=COLOR_DANGER,
            hover_color="#c0392b", command=confirm
        ).pack(side="right", expand=True, padx=5)
