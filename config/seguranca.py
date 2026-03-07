import hashlib
import re


def gerar_hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


def verificar_senha(senha, hash_armazenado):
    return gerar_hash_senha(senha) == hash_armazenado


def validar_email(email):
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(padrao, email))


def validar_telefone(telefone):
    apenas_numeros = re.sub(r'\D', '', telefone)
    return len(apenas_numeros) >= 10