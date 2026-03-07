import json
import os
from datetime import datetime


def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')


def carregar_json(caminho_arquivos):
    if not os.path.exists(caminho_arquivos):
        return []
    with open(caminho_arquivos, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []


def salvar_json(dados, caminho_arquivos):
    os.makedirs(os.path.dirname(caminho_arquivos), exist_ok=True)
    with open(caminho_arquivos, "w", encoding="utf-8") as file:
        json.dump(dados, file, indent=4, ensure_ascii=False)


def registrar_evento(mensagem, arquivo_log):
    os.makedirs(os.path.dirname(arquivo_log), exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(arquivo_log, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {mensagem}\n")
