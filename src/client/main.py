# Arquivo: soap_mockup_client.py
# Descrição: Cliente SOAP em Python para testes com soap_mockup_server
# Autor: <github.com/malki-cedheq>
# Criado: 31/07/2025
# Atualizado: 01/08/2025

# Dependências: zeep, requests, lxml

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from lxml import etree
from zeep import Client
from zeep.transports import Transport
from zeep.plugins import HistoryPlugin
from requests import Session
from requests.auth import HTTPBasicAuth

# ==========================
# Configuração de Logging
# ==========================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = os.getenv("LOG_FILE", "soap_client.log")
MAX_LOG_SIZE = int(os.getenv("MAX_LOG_SIZE", 1 * 1024 * 1024))  # 1 MB
BACKUP_COUNT = int(os.getenv("BACKUP_COUNT", 5))

BASE_DIR = Path(__file__).resolve().parent  # pasta do arquivo main.py
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)  # cria a pasta se não existir
LOG_PATH = LOG_DIR / LOG_FILE

logger = logging.getLogger("soap_mockup_client")
logger.setLevel(LOG_LEVEL)

# Handler de arquivo com rotação
file_handler = RotatingFileHandler(
    LOG_PATH, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT, encoding="utf-8"
)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
file_handler.setFormatter(formatter)

# Handler de console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# ==========================
# Configurações do cliente
# ==========================
USERNAME = "usuario_teste"
PASSWORD = "senha_teste"
WSDL_URL = "http://127.0.0.1:8000/?wsdl"

# ==========================
# Inicialização da sessão SOAP
# ==========================
logger.info(f"Iniciando cliente SOAP para {WSDL_URL}")

# Configura sessão HTTP com autenticação básica
session = Session()
session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

# Transport com sessão autenticada
transport = Transport(session=session)

# Plugin para capturar histórico SOAP (request/response)
history = HistoryPlugin()

# Cria cliente SOAP Zeep
client = Client(WSDL_URL, transport=transport, plugins=[history])
logger.info("Cliente SOAP inicializado com sucesso")


# ==========================
# Função auxiliar para exibir XML detalhado
# ==========================
def print_soap_history():
    """
    Exibe e registra no log o XML completo da última requisição e resposta SOAP.
    Disponível apenas se LOG_LEVEL estiver como DEBUG.
    """
    if history.last_sent and logger.isEnabledFor(logging.DEBUG):
        xml_req = etree.tostring(
            history.last_sent["envelope"], pretty_print=True
        ).decode()
        logger.debug(f"📤 SOAP Request:\n{xml_req}")
    if history.last_received and logger.isEnabledFor(logging.DEBUG):
        xml_res = etree.tostring(
            history.last_received["envelope"], pretty_print=True
        ).decode()
        logger.debug(f"📥 SOAP Response:\n{xml_res}")


# ==========================
# Função de Inicialização do client
# ==========================
def main():
    # ==========================
    # 1️⃣ Criar novo pedido
    # ==========================
    """logger.info("Enviando requisição: criar_pedido")
    novo_id = client.service.criar_pedido("Pedido autenticado")
    logger.info(f"✅ Novo pedido criado com ID: {novo_id}")
    print_soap_history()

    # ==========================
    # 2️⃣ Consultar status do pedido
    # ==========================
    logger.info(f"Enviando requisição: consultar_status para ID={novo_id}")
    status = client.service.consultar_status(novo_id)
    logger.info(f"📌 Status do pedido {novo_id}: {status}")
    print_soap_history()

    # ==========================
    # 3️⃣ Cancelar pedido
    # ==========================
    logger.info(f"Enviando requisição: cancelar_pedido para ID={novo_id}")
    resultado = client.service.cancelar_pedido(novo_id)
    logger.info(f"❌ Pedido {novo_id} cancelado? {resultado}")
    print_soap_history()"""


# ==========================
# Inicialização do client
# ==========================
if __name__ == "__main__":
    main()
