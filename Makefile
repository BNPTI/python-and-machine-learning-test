# AI/ML Engineering Challenge — atalhos para macOS/Linux.
# Tudo isto também roda em qualquer SO (inclusive Windows) com: python dev.py <comando>
# Comece com: make setup PYTHON=python3.12

PYTHON ?= python3

.DEFAULT_GOAL := help

.PHONY: help setup test test-fast run lint assets fetch-weights check-integrity clean

help: ## Mostra os comandos disponíveis
	@$(PYTHON) dev.py --help

setup: ## Cria venv, instala deps, baixa pesos, gera datasets (rode primeiro)
	$(PYTHON) dev.py setup

test: ## Roda a suíte de aceitação completa (inclui os testes lentos)
	$(PYTHON) dev.py test

test-fast: ## Roda tudo exceto os testes lentos de torch/treino
	$(PYTHON) dev.py test-fast

run: ## Sobe a API (Swagger UI em /docs)
	$(PYTHON) dev.py run

lint: ## Faz lint com o ruff
	$(PYTHON) dev.py lint

assets: ## (Re)gera a imagem, o vídeo e o dataset de formas determinísticos
	$(PYTHON) dev.py assets

fetch-weights: ## Baixa + verifica o checksum do yolov8n.pt pré-treinado
	$(PYTHON) dev.py fetch-weights

check-integrity: ## Verifica que os arquivos protegidos não foram modificados
	$(PYTHON) dev.py check-integrity

clean: ## Remove venv, caches e artefatos gerados
	$(PYTHON) dev.py clean
