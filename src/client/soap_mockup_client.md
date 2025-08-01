---

## 📌 Cliente SOAP Mock – Testes com soap\_mockup\_server

Este projeto implementa um **cliente SOAP em Python** utilizando [Zeep](https://docs.python-zeep.org/en/master/) para realizar testes contra o servidor `soap_mockup_server`.
Ele consome as operações **criar**, **consultar status** e **cancelar** pedidos, usando **autenticação básica HTTP**.

Inclui **logging estruturado** com rotação de arquivos e captura de XML detalhado de requisições/respostas em nível `DEBUG`.

---

### 🚀 Funcionalidades

* ✅ Cliente SOAP compatível com Python 3.13.
* ✅ Integração com servidor mock usando WSDL dinâmico.
* ✅ Autenticação HTTP Basic integrada.
* ✅ Logging estruturado com:

  * Rotação automática de arquivos.
  * Nível de log configurável (`DEBUG`, `INFO`, `WARNING`, `ERROR`).
  * Registro de XML completo em `DEBUG`.

---

### 🛠️ Requisitos

* Python 3.8+
* Dependências:

  ```bash
  pip install zeep requests lxml
  ```

---

### 📂 Estrutura do projeto

```
soap_client/
│── soap_mockup_client.py    # Cliente SOAP com logging e autenticação
│── soap_client.log          # Arquivo de log (gerado automaticamente)
│── README.md
```

---

## 📜 Executando o cliente

```bash
python soap_mockup_client.py
```

* O cliente irá:
  1️⃣ Criar um novo pedido.
  2️⃣ Consultar o status do pedido.
  3️⃣ Cancelar o pedido criado.

* O resultado será exibido no console e registrado em `soap_client.log`.

---

### 🔑 Autenticação

* O cliente utiliza **Basic Auth** para acessar o servidor.
* Credenciais padrão (devem coincidir com o servidor):

  ```
  Usuário: usuario_teste
  Senha: senha_teste
  ```

---

## 📌 Logging

### 📌 Níveis de log:

* `DEBUG` – Captura e registra o XML completo de requisições e respostas.
* `INFO` – Logs de operações e status principais.
* `WARNING` – Problemas de conexão ou falhas leves.
* `ERROR` – Exceções críticas.

### 📌 Configuração via variáveis de ambiente:

```bash
set LOG_LEVEL=DEBUG        # Nível de log (DEBUG/INFO/WARNING/ERROR)
set LOG_FILE=soap_client.log   # Nome do arquivo de log
set MAX_LOG_SIZE=2097152   # Tamanho máximo do log (bytes)
set BACKUP_COUNT=5         # Quantidade de arquivos antigos a manter
```

* Por padrão, o log é gravado em `soap_client.log` e exibido no console.
* A rotação de arquivos mantém até `BACKUP_COUNT` versões antigas.

---

### 📌 Exemplo de saída (INFO):

```
2025-08-01 02:30:15 [INFO] Iniciando cliente SOAP para http://127.0.0.1:8000/?wsdl
2025-08-01 02:30:15 [INFO] Cliente SOAP inicializado com sucesso
2025-08-01 02:30:15 [INFO] Enviando requisição: criar_pedido
2025-08-01 02:30:15 [INFO] ✅ Novo pedido criado com ID: 3
2025-08-01 02:30:15 [INFO] Enviando requisição: consultar_status para ID=3
2025-08-01 02:30:15 [INFO] 📌 Status do pedido 3: Processando
2025-08-01 02:30:15 [INFO] Enviando requisição: cancelar_pedido para ID=3
2025-08-01 02:30:15 [INFO] ❌ Pedido 3 cancelado? True
```

### 📌 Exemplo de saída (DEBUG):

Inclui XML completo das requisições e respostas:

```
2025-08-01 02:31:22 [DEBUG] 📤 SOAP Request:
<soapenv:Envelope ...>
   <soapenv:Body>
      <ped:criar_pedido>
         <descricao>Pedido autenticado</descricao>
      </ped:criar_pedido>
   </soapenv:Body>
</soapenv:Envelope>

2025-08-01 02:31:22 [DEBUG] 📥 SOAP Response:
<soapenv:Envelope ...>
   <soapenv:Body>
      <ped:criar_pedidoResponse>
         <id>3</id>
      </ped:criar_pedidoResponse>
   </soapenv:Body>
</soapenv:Envelope>
```

---

### 🔧 Personalização

* Alterar credenciais: edite `USERNAME` e `PASSWORD` no código.
* Ajustar URL do servidor: edite `WSDL_URL`.
* Controlar logs: use as variáveis de ambiente para definir nível, tamanho máximo e quantidade de backups.

---

### 🧪 Ferramentas recomendadas para depuração

* [SoapUI](https://www.soapui.org/) para monitorar o WSDL.
* [Wireshark](https://www.wireshark.org/) para inspeção de pacotes SOAP.
* O próprio log `soap_client.log` para análise de XML enviado/recebido.

---