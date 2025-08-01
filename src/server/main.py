# Arquivo: soap_mockup_server.py
# Descrição: Servidor de mockup para teste de client SOAP com autenticação em SQLite
# Autor: <github.com/malki-cedheq>
# Criado: 31/07/2025
# Atualizado: 01/08/2025

# Dependências: pysimplesoap, flask, sqlite3

from flask import Flask, request, Response
from pysimplesoap.server import SoapDispatcher
import base64, sqlite3, hashlib, logging, os
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

# ==========================
# Configuração de Logging
# ==========================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = os.getenv("LOG_FILE", "soap_server.log")
MAX_LOG_SIZE = int(os.getenv("MAX_LOG_SIZE", 1 * 1024 * 1024))  # 1 MB
BACKUP_COUNT = int(os.getenv("BACKUP_COUNT", 5))

logger = logging.getLogger("soap_mockup_server")
logger.setLevel(LOG_LEVEL)

file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT, encoding="utf-8"
)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# ==========================
# Banco mock de pedidos
# ==========================
PEDIDOS = {
    1: {"status": "Processando", "descricao": "Pedido inicial"},
    2: {"status": "Enviado", "descricao": "Pedido enviado"},
}

# ==========================
# Configuração do SQLite
# ==========================
DB_FILE = "usuarios.db"


def init_db():
    """Cria o banco de dados SQLite e a tabela de usuários caso não existam."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()
    logger.info("Banco de dados inicializado.")


def add_user(username: str, password: str):
    """Adiciona um novo usuário ao banco com senha hash SHA-256."""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO usuarios (username, password_hash) VALUES (?, ?)",
        (username, password_hash),
    )
    conn.commit()
    conn.close()
    logger.info(f"Usuário padrão adicionado (ou já existente): {username}")


def check_user(username: str, password: str) -> bool:
    """Valida usuário/senha consultando o banco SQLite."""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM usuarios WHERE username=? AND password_hash=?",
        (username, password_hash),
    )
    result = cursor.fetchone()
    conn.close()
    if result:
        logger.info(f"Autenticação bem-sucedida para usuário: {username}")
        return True
    else:
        logger.warning(f"Tentativa de login falhou para usuário: {username}")
        return False


# Inicializa banco e cria usuário padrão
init_db()
add_user("usuario_teste", "senha_teste")


# ==========================
# Middleware de autenticação
# ==========================
def auth(environ) -> bool:
    """Autenticação Basic Auth usando SQLite."""
    auth_header = environ.get("HTTP_AUTHORIZATION")
    if auth_header and auth_header.startswith("Basic "):
        encoded = auth_header.split(" ", 1)[1]
        user, pwd = base64.b64decode(encoded).decode().split(":", 1)
        return check_user(user, pwd)
    logger.warning("Requisição sem credenciais válidas.")
    return False


# ==========================
# Funções SOAP
# ==========================
def criar_pedido(descricao: str) -> int:
    """Cria um novo pedido no banco em memória."""
    novo = max(PEDIDOS.keys(), default=0) + 1
    PEDIDOS[novo] = {"status": "Processando", "descricao": descricao}
    logger.info(f"Pedido criado ID={novo} Descrição='{descricao}'")
    return novo


def consultar_status(pedido_id: int) -> str:
    """Consulta o status de um pedido pelo ID."""
    status = PEDIDOS.get(pedido_id, {}).get("status", "Pedido não encontrado")
    logger.info(f"Consulta status para ID={pedido_id} -> {status}")
    return status


def cancelar_pedido(pedido_id: int) -> bool:
    """Cancela um pedido existente."""
    if pedido_id in PEDIDOS:
        PEDIDOS[pedido_id]["status"] = "Cancelado"
        logger.info(f"Pedido cancelado ID={pedido_id}")
        return True
    logger.warning(f"Tentativa de cancelar pedido inexistente ID={pedido_id}")
    return False


# ==========================
# Configuração do dispatcher SOAP
# ==========================
DISPATCHER = SoapDispatcher(
    name="PedidoService",
    location="http://127.0.0.1:8000/",
    action="http://127.0.0.1:8000/",
    namespace="http://exemplo.com/pedido",
    prefix="ped",
    trace=True,
)

# Registro das operações SOAP
DISPATCHER.register_function(
    "criar_pedido", criar_pedido, returns={"id": int}, args={"descricao": str}
)

DISPATCHER.register_function(
    "consultar_status",
    consultar_status,
    returns={"status": str},
    args={"pedido_id": int},
)

DISPATCHER.register_function(
    "cancelar_pedido",
    cancelar_pedido,
    returns={"success": bool},
    args={"pedido_id": int},
)


# ==========================
# Rotas Flask para SOAP e WSDL
# ==========================
@app.route("/", methods=["GET", "POST"])
def soap_service():
    """
    Endpoint principal que trata:
    - Autenticação Basic Auth.
    - Servir WSDL dinâmico (GET /?wsdl).
    - Processar chamadas SOAP (POST).
    """
    client_ip = request.remote_addr

    # 🔒 Verifica autenticação
    if not auth(request.environ):
        logger.warning(f"Acesso não autorizado de {client_ip}")
        return Response(
            "Unauthorized",
            status=401,
            headers={"WWW-Authenticate": 'Basic realm="SOAP Service"'},
        )

    # ✅ Servir WSDL dinâmico
    if request.method == "GET" and "wsdl" in request.query_string.decode():
        logger.info(f"WSDL solicitado de {client_ip}")
        return Response(DISPATCHER.wsdl(), mimetype="text/xml")

    # ✅ Processar requisições SOAP
    xml_request = request.data.decode("utf-8")
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"XML recebido:\n{xml_request}")

    response = DISPATCHER.dispatch(xml_request)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"XML de resposta:\n{response}")

    logger.info(f"Requisição SOAP recebida de {client_ip}")
    return Response(response, mimetype="text/xml")


# ==========================
# Função de Inicialização do servidor
# ==========================
def main():
    logger.info("Servidor SOAP (PySimpleSOAP + Flask + SQLite) iniciando...")
    logger.info("URL: http://127.0.0.1:8000")
    logger.info(f"Nível de log: {LOG_LEVEL}")
    app.run(host="0.0.0.0", port=8000)


# ==========================
# Inicialização do servidor
# ==========================
if __name__ == "__main__":
    main()
