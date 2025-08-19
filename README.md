# Projeto SOAP com UV

## Instalação

### 1. Instalar o UV

Primeiro, instale o gerenciador de pacotes UV seguindo a documentação oficial:

[Documentação de Instalação do UV](https://astral.sh/docs/uv#installation)

### 2. Instalar Dependências

```bash
uv sync
```

### Criar ambiente virtual (apenas primeira vez)
uv venv

### Ativar Servidor (Windows PowerShell)
```bash
.\.venv\Scripts\Activate.ps1
uv pip install -e .
python -m src.server.main
```

### Ativar Cliente (Windows PowerShell)
```bash
.\.venv\Scripts\Activate.ps1
python -m src.client.main
```