# config/__init__.py — Re-exporta tudo para manter compatibilidade dos imports
# Uso: from config import DB_CLIENTES, seguranca, utils, models, etc.

from config.config import *
from config import seguranca
from config import models
from config import utils
