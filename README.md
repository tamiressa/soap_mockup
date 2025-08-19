# Projeto Python com UV

## Instalação

### 1. Instalar o UV

Primeiro, instale o gerenciador de pacotes UV seguindo a documentação oficial:

[Documentação de Instalação do UV](https://astral.sh/docs/uv#installation)

### 2. Instalar Dependências

```bash
uv sync
```

# Criar ambiente virtual (apenas primeira vez)
uv venv

# Ativar ambiente virtual (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Instalar pacote em modo desenvolvimento
uv pip install -e .

# Executar servidor
python -m src.server.main

# Ativar ambiente virtual (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Executar cliente
python -m src.client.main