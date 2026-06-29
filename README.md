# AI/ML Engineering Challenge

Este desafio simula o trabalho de um sistema de *video management*: detectar
objetos em streams de câmeras, identificar anomalias comportamentais em vídeo, e
treinar, versionar e servir os modelos por trás disso.

São **cinco níveis**, de uma API simples até treinar e fazer deploy de um modelo.
Cada nível já vem com a estrutura base pronta (imports, assinaturas de função,
modelos de dados) e deixa algumas funções para você implementar (marcadas com
`TODO(candidate)`), além de um teste automatizado que verifica o resultado.

> Faça quantos níveis conseguir — qualidade acima de quantidade. Um Nível 1–3
> limpo e correto é um resultado forte; não pule para o Nível 5 deixando os
> níveis anteriores malfeitos.

---

## 1. Escopo

O desafio exercita:

- **Python** — código limpo, tipado e legível; estrutura sensata.
- **APIs** — endpoints FastAPI que respeitam um contrato.
- **Modelos** — consumir um detector pré-treinado (YOLO) e ler sua saída.
- **Vídeo & anomalias** — processamento de frames e lógica temporal com debounce.
- **Treino** — fine-tuning, métricas e versionamento de modelo.
- **Deploy** — um registro de modelos com hot-swap, mais um doc de design curto.
- **Higiene de engenharia** — Conventional Commits, Semantic Versioning, testes.

Os dados são **formas sintéticas** e um cenário de **zone-intrusion**: totalmente
reproduzíveis, sem dados sensíveis, exercitando as mesmas habilidades
transferíveis — inferência load-once, debounce temporal, treino/versão/serviço.

## 2. Requisitos

- **Python 3.11 ou 3.12** (`torch`/`ultralytics` não publicam wheels fora dessa
  faixa; o `setup` verifica isso).
- ~5 GB de disco livre, ~8 GB de RAM, e internet para o setup **único** (baixa o
  build CPU do PyTorch e os pesos `yolov8n.pt`). Sem GPU necessária.
- `git` (e, opcionalmente, `make` no macOS/Linux).

## 3. Início rápido

O runner `dev.py` funciona em **Windows, macOS e Linux** e depende apenas de Python:

```bash
python dev.py setup       # venv + deps + pesos + datasets (uma vez)
python dev.py test-fast   # testes rápidos (sem treino)
python dev.py run         # sobe a API em http://127.0.0.1:8000/docs
```

> No **Windows**, use o launcher do Python: `py -3.12 dev.py setup`.
> No **macOS/Linux**, se preferir, há atalhos equivalentes via `make` (ex.:
> `make setup PYTHON=python3.12`, `make test`).

O `setup` roda um preflight, instala as dependências fixadas, baixa os pesos
pré-treinados e gera os datasets. Depois abra os níveis abaixo em ordem.

Comandos (`python dev.py <comando>`; no macOS/Linux também `make <comando>`):

| Comando | O que faz |
|---|---|
| `setup` | Cria a venv, instala deps, baixa pesos e gera datasets |
| `test` | Suíte completa, **incluindo** os testes lentos de treino |
| `test-fast` | Tudo exceto os testes lentos de torch/treino |
| `run` | Sobe a API (Swagger UI em `/docs`) |
| `lint` | Faz lint com o ruff |
| `check-commits` | Verifica os Conventional Commits (consultivo) |
| `check-integrity` | Confirma que os arquivos protegidos não foram editados |
| `clean` | Remove venv, caches e artefatos gerados |

## 4. As regras

- **Implemente os stubs.** Edite apenas os arquivos com `TODO(candidate)`:
  `app/levels/level1.py`, `level2.py`, `level3.py`, `ml/train.py`,
  `ml/evaluate.py`, `ml/registry.py`. Você pode adicionar seus próprios módulos.
- **Não edite os arquivos protegidos** (o contrato + a infraestrutura de teste):
  `app/schemas.py`, `app/main.py`, `app/config.py`, `app/levels/level4.py`,
  `app/levels/level5.py`, `ml/model_loader.py`, `ml/detectors.py`,
  `ml/versioning.py`, tudo em `tests/acceptance/`, `tests/conftest.py`, e
  `scripts/`. O `python dev.py check-integrity` sinaliza qualquer alteração. Se
  achar que um arquivo protegido tem um bug, não o edite — anote no `NOTES.md`.
- **Não enfraqueça os testes.** Adicione seus próprios testes em `tests/candidate/`
  se quiser.
- **Commite conforme avança**, usando Conventional Commits, ~um (ou uma pequena
  série) por nível — ex.: `feat(level1): implement health and metadata endpoints`.
  O tipo (`feat`/`fix`/…) e o escopo `(level1)` ficam em inglês; a descrição pode
  ser em português.
- **Faça a tag do modelo** que você produzir no Nível 4:
  `git tag model/shapes-detector-v1.0.0`.

## 5. Os níveis

Cada nível diz **qual arquivo abrir**, **o que implementar** e **como testar**. Em
cada stub, o que você escreve está marcado com `# TODO(candidate):` dentro de uma
função cujo corpo é `raise NotImplementedError`. A docstring acima do `TODO` é o
contrato detalhado. Você edita apenas os 6 arquivos de stub; o restante é fornecido.

| Nível | Arquivo(s) que você edita | O que implementar |
|---|---|---|
| 1 | `app/levels/level1.py` | `clamp_box`, `health`, `image_metadata` |
| 2 | `app/levels/level2.py` | `Detector.load`, `Detector.detect`, `get_detector`, endpoint `detect` |
| 3 | `app/levels/level3.py` | `analyze_video` |
| 4 | `ml/train.py` + `ml/evaluate.py` | `train`, `save_versioned_model` · `evaluate`, `compute_dataset_hash`, `check_leakage` |
| 5 | `ml/registry.py` + crie `docs/DESIGN.md` | `ModelRegistry` (todos os métodos) + o doc de design |

---

### Nível 1 — Fundamentos & FastAPI
- **Edite:** `app/levels/level1.py`
- **Implemente:** o helper puro `clamp_box`, o endpoint `GET /health` e o endpoint
  `POST /image/metadata` (retorna largura/altura/modo/formato de uma imagem enviada).
- **Teste:** `pytest tests/acceptance/test_level1.py -v`

### Nível 2 — Detecção de objetos (YOLO)
- **Edite:** `app/levels/level2.py`
- **Implemente:** a classe `Detector` (`load` carrega o `yolov8n` uma só vez;
  `detect` roda a inferência e devolve as detecções), o singleton `get_detector` e
  o endpoint `POST /detect`.
- **Teste:** `pytest tests/acceptance/test_level2.py -v`
- `POST /detect` recebe uma imagem (+ `?conf=` opcional) e devolve detecções
  `{label, confidence, box}`, ordenadas por confiança, filtradas pelo threshold,
  com as boxes ajustadas aos limites da imagem.

### Nível 3 — Anomalia em vídeo
- **Edite:** `app/levels/level3.py`
- **Implemente:** a função `analyze_video`.
- **Teste:** `pytest tests/acceptance/test_level3.py -v`
- Percorra os frames, aplique frame-skip, e emita um evento de **zone-intrusion**
  quando um alvo permanece numa zona por `>= min_consecutive` frames processados,
  com flush de um evento ainda aberto ao final do vídeo. O contrato exato está na
  docstring da função.

### Nível 4 — Treinar / avaliar / versionar
- **Edite:** `ml/train.py` e `ml/evaluate.py`
- **Implemente:** em `ml/train.py`: `train` e `save_versioned_model`; em
  `ml/evaluate.py`: `evaluate`, `compute_dataset_hash` e `check_leakage`.
- **Teste:** `pytest tests/acceptance/test_level4_versioning.py -v` (rápido) e
  `pytest tests/acceptance/test_level4_training.py -v` (lento — treina de fato).
- Faça fine-tuning do `yolov8n` no dataset sintético de formas; compute métricas;
  verifique leakage entre treino/validação; e salve um artefato versionado mais um
  `model_card.json`. Respeite os limites da receita (veja
  `GET /level4/recommended-config`).

### Nível 5 — Registro / deploy / design
- **Edite:** `ml/registry.py`. Depois **crie** `docs/DESIGN.md` a partir de
  `docs/DESIGN_TEMPLATE.md`.
- **Implemente:** a classe `ModelRegistry` (todos os métodos) + o doc de design.
- **Teste:** `pytest tests/acceptance/test_level5.py -v`
- O `ModelRegistry` descobre modelos versionados, troca a versão **ativa** em
  runtime (hot-swap, thread-safe) e carrega + faz cache de cada um sob demanda
  (lazy). O `docs/DESIGN.md` cobre escala, rollout, observabilidade, drift e modos
  de falha.

## 6. Versionamento de modelo (Semantic Versioning)

**Semantic Versioning** numera versões como `MAJOR.MINOR.PATCH` (ex.: `2.1.3`).
Cada número tem um significado e você incrementa o número certo conforme o tipo de
mudança:

- **MAJOR** — mudança incompatível;
- **MINOR** — adição compatível;
- **PATCH** — correção sem mudança de comportamento.

Ao subir um número, os menores à direita voltam a zero (ex.: `1.4.2` → MINOR →
`1.5.0`). No Nível 4 você aplica isso a um **modelo**: o artefato é nomeado
`shapes-detector-vMAJOR.MINOR.PATCH.pt`, e o `model_card.json` carrega a mesma
versão. Para um modelo de detecção:

| Mudança | Incremento |
|---|---|
| Retrain de bugfix, mesmo comportamento | **PATCH** (1.0.0 → 1.0.1) |
| Novo treino / mais dados, mesmas classes & I/O | **MINOR** (1.0.0 → 1.1.0) |
| Mudança no conjunto de classes ou no contrato de entrada/saída | **MAJOR** (1.0.0 → 2.0.0) |

## 7. Submetendo

Trabalhe em uma branch com commits reais e incrementais (não faça squash em um
único dump nem envie um zip que perca o histórico do git). Quando terminar:

1. `make test` e cole o resumo no `NOTES.md` (anote quaisquer skips e o porquê).
2. Preencha o `NOTES.md` (níveis tentados, decisões, onde parou).
3. Faça push da sua branch, ou `git bundle create submission.bundle --all` se
   precisar entregar um arquivo.

## 8. Referência

- Glossário de termos: `docs/GLOSSARY.md`.
- Travou no setup (Python errado, sem GPU, offline)? Anote no `NOTES.md` e continue
  no que puder.
