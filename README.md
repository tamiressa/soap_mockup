# Instalação

## Instalar uv

> https://docs.astral.sh/uv/getting-started/installation/

## Instalar dependências
```bash
uv sync
```

# Execução

## servidor
```bash
    uv venv // primeira vez
	.\.venv\Scripts\Activate.ps1
	uv pip install -e .
	python -m src.server.main
```

## client
```bash
    .\.venv\Scripts\Activate.ps1
	python -m src.client.main
```