# Arquivo: soap_mockup_server.py
# Descrição: Servidor de mockup para teste de client SOAP com autenticação em SQLite
# Autor: <github.com/malki-cedheq>
# Criado: 31/07/2025
# Atualizado: 01/08/2025

# Dependências: pysimplesoap, flask, sqlite3

import os
import base64
import sqlite3
import hashlib
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from flask import Flask, request, Response
from pysimplesoap.server import SoapDispatcher

# ===== [ADICIONADO PELA UI] =====
from flask import render_template_string

# ================================

app = Flask(__name__)

# ==========================
# Configuração de Logging
# ==========================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = os.getenv("LOG_FILE", "soap_server.log")
MAX_LOG_SIZE = int(os.getenv("MAX_LOG_SIZE", 1 * 1024 * 1024))  # 1 MB
BACKUP_COUNT = int(os.getenv("BACKUP_COUNT", 5))

BASE_DIR = Path(__file__).resolve().parent  # pasta do arquivo main.py
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)  # cria a pasta se não existir
LOG_PATH = LOG_DIR / LOG_FILE

logger = logging.getLogger("soap_mockup_server")
logger.setLevel(LOG_LEVEL)

file_handler = RotatingFileHandler(
    LOG_PATH, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT, encoding="utf-8"
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
# [ADICIONADO PELA UI] Página HTML de testes
# ==========================
UI_HTML = r"""<!doctype html>
<html lang="pt-br">
<head>
  <meta charset="utf-8">
  <title>PedidoService - SOAP Tester</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root { --border:#e5e7eb; --muted:#6b7280; }
    body { font-family: system-ui, Arial, sans-serif; max-width: 1000px; margin: 24px auto; padding: 0 16px; background:#f8fafc; }
    h1 { margin: 0 0 12px; }
    a { color:#2563eb; text-decoration:none; }
    .card { background:white; border: 1px solid var(--border); border-radius: 12px; padding: 16px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,.06); }
    label { display:block; font-weight:600; margin-top:10px; }
    input, select { width:100%; padding:10px; border:1px solid #d1d5db; border-radius:10px; margin-top:6px; background:white; }
    button { margin-top:12px; margin-right:8px; padding:10px 14px; border-radius:10px; border:1px solid #d1d5db; cursor:pointer; background:white; }
    button:hover { background:#f3f4f6; }
    pre { background:#0b1021; color:#e5e7eb; padding:12px; border-radius:10px; overflow:auto; }
    .row { display:grid; grid-template-columns: 1fr 1fr; gap:16px; }
    .col3 { display:grid; grid-template-columns: 1fr 1fr 1fr; gap:16px; }
    @media (max-width:900px){ .row, .col3 { grid-template-columns: 1fr; } }
    small { color:var(--muted); }
    .muted { color:var(--muted); }
    .badge { display:inline-block; padding:4px 8px; border:1px solid var(--border); border-radius:999px; }
  </style>
</head>
<body>
  <h1>PedidoService - SOAP Tester</h1>
  <div class="card">
    <div class="col3">
      <div><b>Endpoint SOAP:</b><br><span class="badge">http://127.0.0.1:8000/</span></div>
      <div><b>WSDL:</b><br><a href="/?wsdl" target="_blank">/?wsdl</a></div>
      <div><b>Auth:</b><br><span class="badge">Basic (SQLite)</span></div>
    </div>
    <small>Dica: rode o servidor com <code>LOG_LEVEL=DEBUG</code> para ver o XML de requisição/resposta no console.</small>
  </div>

  <div class="card">
    <div class="row">
      <div>
        <label>Usuário</label>
        <input id="user" value="usuario_teste">
      </div>
      <div>
        <label>Senha</label>
        <input id="pass" type="password" value="senha_teste">
      </div>
    </div>

    <label>Operação</label>
    <select id="op">
      <option value="criar_pedido">criar_pedido(descricao: string) → int</option>
      <option value="consultar_status">consultar_status(pedido_id: int) → string</option>
      <option value="cancelar_pedido">cancelar_pedido(pedido_id: int) → bool</option>
    </select>

    <div id="params">
      <label id="label-main">Descrição (para criar_pedido)</label>
      <input id="param-main" value="Pedido via UI">
    </div>

    <div>
      <button onclick="enviar()">Enviar requisição SOAP</button>
      <button onclick="limpar()">Limpar</button>
    </div>
    <small class="muted">A UI monta o envelope SOAP e faz POST para <code>/</code> com cabeçalho <code>Authorization: Basic ...</code>.</small>
  </div>

  <div class="row">
    <div class="card">
      <b>SOAP Request</b>
      <pre id="req">(vazio)</pre>
    </div>
    <div class="card">
      <b>SOAP Response</b>
      <pre id="res">(vazio)</pre>
    </div>
  </div>

<script>
  const endpoint = "/"; // mesmo host/porta do Flask
  const ns = "http://exemplo.com/pedido";

  const op = document.getElementById('op');
  const labelMain = document.getElementById('label-main');
  const inputMain = document.getElementById('param-main');

  op.addEventListener('change', () => {
    if (op.value === 'criar_pedido') {
      labelMain.textContent = "Descrição (para criar_pedido)";
      inputMain.value = "Pedido via UI";
    } else {
      labelMain.textContent = "Pedido ID (para consultar/cancelar)";
      inputMain.value = "1";
    }
  });

  function authHeader() {
    const u = document.getElementById('user').value;
    const p = document.getElementById('pass').value;
    return "Basic " + btoa(u + ":" + p);
  }

  function envelope(bodyXml) {
    return `<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ped="${ns}">
  <soapenv:Header/>
  <soapenv:Body>
    ${bodyXml}
  </soapenv:Body>
</soapenv:Envelope>`;
  }

  function bodyFromOp() {
    const v = op.value;
    const val = inputMain.value.trim();
    if (v === "criar_pedido") {
      return `<ped:criar_pedido><ped:descricao>${escapeXml(val)}</ped:descricao></ped:criar_pedido>`;
    } else if (v === "consultar_status") {
      return `<ped:consultar_status><ped:pedido_id>${val}</ped:pedido_id></ped:consultar_status>`;
    } else {
      return `<ped:cancelar_pedido><ped:pedido_id>${val}</ped:pedido_id></ped:cancelar_pedido>`;
    }
  }

  async function enviar() {
    const bodyXml = bodyFromOp();
    const xml = envelope(bodyXml);
    document.getElementById('req').textContent = xml;

    try {
      const resp = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "text/xml; charset=utf-8",
          "SOAPAction": `http://127.0.0.1:8000/${op.value}`,
          "Authorization": authHeader()
        },
        body: xml
      });
      const text = await resp.text();
      document.getElementById('res').textContent = text;
    } catch (e) {
      document.getElementById('res').textContent = "Erro: " + e;
    }
  }

  function limpar(){
    document.getElementById('req').textContent = "(vazio)";
    document.getElementById('res').textContent = "(vazio)";
  }

  function escapeXml(s){
    return s.replace(/&/g,"&amp;")
            .replace(/</g,"&lt;")
            .replace(/>/g,"&gt;")
            .replace(/"/g,"&quot;")
            .replace(/'/g,"&apos;");
  }
</script>
</body>
</html>
"""


@app.route("/ui", methods=["GET"])
def ui_page():
    # Rota apenas para servir a página de testes (não exige autenticação aqui).
    # As chamadas SOAP feitas por essa página para "/" enviam Authorization: Basic.
    return render_template_string(UI_HTML)


# ==========================


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
