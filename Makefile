# Face Guard AI/ML Challenge — executor de tarefas.
# Rode `make help` para ver a lista. Comece com `make setup`.

PYTHON ?= python3
VENV   := .venv
BIN    := $(VENV)/bin
PY     := $(BIN)/python
PIP    := $(BIN)/pip

# Mantém o Ultralytics totalmente local e offline-friendly durante o dev e a avaliação:
# sem telemetria/sync com o HUB, sem downloads-surpresa de fontes/assets no seu home dir.
export YOLO_CONFIG_DIR := $(CURDIR)/.ultralytics
export MPLBACKEND := Agg

.DEFAULT_GOAL := help

.PHONY: help
help: ## Mostra esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

.PHONY: preflight
preflight: ## Verifica versão do Python / disco antes de instalar qualquer coisa
	$(PYTHON) scripts/preflight.py

.PHONY: venv
venv: preflight
	test -d $(VENV) || $(PYTHON) -m venv $(VENV)

.PHONY: setup
setup: venv ## Cria venv, instala deps, baixa pesos, gera datasets (rode isto primeiro)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PY) -c "from ultralytics import settings; settings.update({'sync': False})" || true
	$(MAKE) fetch-weights
	$(MAKE) assets
	@echo "\n✅ Setup concluído. Próximo passo: 'make test' (depois abra o README.md, nível por nível)."

.PHONY: fetch-weights
fetch-weights: ## Baixa + verifica o checksum do yolov8n.pt pré-treinado
	$(PY) scripts/fetch_weights.py

.PHONY: assets
assets: ## (Re)gera a imagem de exemplo, o vídeo e o dataset de formas determinísticos
	$(PY) scripts/generate_assets.py

.PHONY: run
run: ## Inicia o servidor FastAPI (http://127.0.0.1:8000/docs)
	$(BIN)/uvicorn app.main:app --reload --host $${FG_HOST:-127.0.0.1} --port $${FG_PORT:-8000}

.PHONY: test
test: ## Roda a suíte de aceitação completa (inclui os testes lentos dos níveis 2/4)
	$(BIN)/pytest

.PHONY: test-fast
test-fast: ## Roda tudo exceto os testes lentos de torch/treino
	$(BIN)/pytest -m "not slow"

.PHONY: lint
lint: ## Faz lint com o ruff
	$(BIN)/ruff check .

.PHONY: check-commits
check-commits: ## Valida seus Conventional Commits (consultivo)
	$(PY) scripts/check_commits.py

.PHONY: check-integrity
check-integrity: ## Verifica que você não modificou os arquivos protegidos/não-editáveis
	$(PY) scripts/check_integrity.py

.PHONY: clean
clean: ## Remove venv, caches e artefatos gerados
	rm -rf $(VENV) .pytest_cache .ruff_cache .ultralytics runs models/*.pt
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
