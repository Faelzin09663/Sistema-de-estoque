# config.py — Configurações centralizadas do sistema
import os

# Raiz do projeto (sistema-de-estoque/) — resolve caminhos independente do CWD
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Arquivos de Banco de Dados ---
DB_CLIENTES = os.path.join(_PROJECT_ROOT, "database", "cadastro.json")
DB_FUNCIONARIOS = os.path.join(_PROJECT_ROOT, "database", "funcionarios.json")
DB_ESTOQUE = os.path.join(_PROJECT_ROOT, "database", "estoque.json")

# --- Arquivos de Log ---
LOG_CLIENTES = os.path.join(_PROJECT_ROOT, "logs", "atividades.txt")
LOG_FUNCIONARIOS = os.path.join(_PROJECT_ROOT, "logs", "atividades_funcionarios.txt")
LOG_ESTOQUE = os.path.join(_PROJECT_ROOT, "logs", "atividades_estoque.txt")

# --- Token de Vendedor ---
TOKEN_FILE = os.path.join(_PROJECT_ROOT, "database", "vendedor_token.json")

# --- Admin padrão ---
ADMIN_EMAIL = "Seu email aqui para ser admin"

# --- GUI ---
APP_TITLE = "Sistema ERP Corporativo"
APP_WIDTH = 1100
APP_HEIGHT = 700
SIDEBAR_WIDTH = 200

# --- Cores do tema ---
COLOR_PRIMARY = "#1a73e8"
COLOR_ACCENT = "#00b4d8"
COLOR_SUCCESS = "#2ecc71"
COLOR_DANGER = "#e74c3c"
COLOR_WARNING = "#f39c12"
COLOR_BG_DARK = "#1a1a2e"
COLOR_BG_SIDEBAR = "#16213e"
COLOR_BG_CARD = "#0f3460"
COLOR_TEXT = "#e0e0e0"

# --- Estoque ---
ALERTA_ESTOQUE_BAIXO = 5
