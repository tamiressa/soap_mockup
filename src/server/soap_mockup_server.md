---

## 📌 Servidor SOAP Mock – Serviço de Pedidos (com SQLite, Autenticação e Logging Avançado)

Este projeto implementa um **servidor SOAP mock** em Python 3 utilizando [PySimpleSOAP](https://pypi.org/project/PySimpleSOAP/) e [Flask](https://flask.palletsprojects.com/).
O servidor simula um sistema de pedidos com operações **criar**, **consultar status** e **cancelar** pedidos.
Inclui **autenticação básica HTTP (Basic Auth)** com armazenamento em **SQLite** e sistema de **logging avançado** com rotação de arquivos e captura de XML detalhado.

---

### 🚀 Funcionalidades

* ✅ Servidor SOAP compatível com **Python 3.13**.
* ✅ WSDL dinâmico gerado na rota `/?wsdl`.
* ✅ Banco de pedidos em memória para testes rápidos.
* ✅ Autenticação HTTP Basic com credenciais armazenadas em SQLite (com hash SHA-256).
* ✅ Logging estruturado com:

  * Rotação automática de arquivos.
  * Nível de log configurável (`DEBUG`, `INFO`, `WARNING`, `ERROR`).
  * Captura de **XML completo** de requisições e respostas em nível `DEBUG`.

---

### 🛠️ Requisitos

* Python 3.8+
* Dependências:

  ```bash
  pip install flask pysimplesoap
  ```

---

### 📂 Estrutura do projeto

```
soap_server/
│── soap_mockup_server.py    # Código do servidor SOAP (Flask + PySimpleSOAP + SQLite + Logging)
│── usuarios.db              # Banco SQLite (gerado automaticamente)
│── soap_server.log          # Arquivo de log com rotação automática
│── README.md
```

---

## 📜 Executando o servidor

```bash
python soap_mockup_server.py
```

* O servidor estará disponível em:

  ```
  http://127.0.0.1:8000
  ```

* O WSDL dinâmico pode ser acessado em:

  ```
  http://127.0.0.1:8000/?wsdl
  ```

---

### 🔑 Autenticação

* Todas as requisições SOAP exigem **Basic Auth**.
* Credenciais padrão (armazenadas em SQLite e com hash SHA-256):

  ```
  Usuário: usuario_teste
  Senha: senha_teste
  ```

Se o cliente não enviar credenciais corretas, o servidor retorna `401 Unauthorized`.

---

## 📌 Operações disponíveis

### 1️⃣ Criar Pedido

* **Método:** `criar_pedido(descricao: str) -> int`
* **Descrição:** Cria um novo pedido e retorna o ID.

### 2️⃣ Consultar Status

* **Método:** `consultar_status(pedido_id: int) -> str`
* **Descrição:** Consulta o status de um pedido pelo ID.

### 3️⃣ Cancelar Pedido

* **Método:** `cancelar_pedido(pedido_id: int) -> bool`
* **Descrição:** Cancela um pedido existente.

---

### 📌 Exemplos de chamadas SOAP

#### Criar pedido

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:ped="http://exemplo.com/pedido">
   <soapenv:Body>
      <ped:criar_pedido>
         <descricao>Pedido de teste</descricao>
      </ped:criar_pedido>
   </soapenv:Body>
</soapenv:Envelope>
```

#### Consultar status

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:ped="http://exemplo.com/pedido">
   <soapenv:Body>
      <ped:consultar_status>
         <pedido_id>1</pedido_id>
      </ped:consultar_status>
   </soapenv:Body>
</soapenv:Envelope>
```

#### Cancelar pedido

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:ped="http://exemplo.com/pedido">
   <soapenv:Body>
      <ped:cancelar_pedido>
         <pedido_id>2</pedido_id>
      </ped:cancelar_pedido>
   </soapenv:Body>
</soapenv:Envelope>
```

---

## 🔗 Testando o servidor

### ✅ Via cURL:

```bash
curl -u usuario_teste:senha_teste \
  -H "Content-Type: text/xml" \
  -d @request.xml \
  http://127.0.0.1:8000
```

### ✅ Via cliente Python (Zeep):

```python
from zeep import Client
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep.transports import Transport

session = Session()
session.auth = HTTPBasicAuth("usuario_teste", "senha_teste")
client = Client("http://127.0.0.1:8000/?wsdl", transport=Transport(session=session))

novo_id = client.service.criar_pedido("Pedido via Zeep")
print("Novo ID:", novo_id)
```

---

## 📊 Logging

### 📌 Níveis de log:

* `DEBUG` – Captura XML completo de requisições e respostas.
* `INFO` – Logs de operações e eventos normais.
* `WARNING` – Tentativas de acesso inválidas ou erros de negócio.
* `ERROR` – Exceções críticas.

### 📌 Variáveis de ambiente:

```bash
set LOG_LEVEL=DEBUG        # Nível de log (DEBUG/INFO/WARNING/ERROR)
set LOG_FILE=server.log    # Nome do arquivo de log
set MAX_LOG_SIZE=2097152   # Tamanho máximo do log (bytes)
set BACKUP_COUNT=10        # Quantidade de arquivos antigos para manter
```

### 📌 Rotação de logs:

* Mantém até `BACKUP_COUNT` arquivos.
* Cada arquivo tem no máximo `MAX_LOG_SIZE` bytes.

---

## 🔧 Personalização

* Alterar credenciais: use a função `add_user()` para criar novos usuários no SQLite.
* Substituir o banco em memória (`PEDIDOS`) por um banco real.
* Adicionar novas operações registrando funções no `SoapDispatcher`.

---

## 🧪 Ferramentas recomendadas para teste

* [SoapUI](https://www.soapui.org/) (suporta autenticação e SOAP/XML)
* Postman (modo SOAP/XML + Basic Auth)
* Cliente Zeep (Python)

---