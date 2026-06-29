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
- **Higiene de engenharia** — testes e organização do trabalho.

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
- **Implemente:** `clamp_box`, `GET /health`, `POST /image/metadata`.
- **Teste:** `pytest tests/acceptance/test_level1.py -v`

### Nível 2 — Detecção de objetos (YOLO)
- **Edite:** `app/levels/level2.py`
- **Implemente:** a classe `Detector`, `get_detector` e o endpoint `POST /detect`.
- **Teste:** `pytest tests/acceptance/test_level2.py -v`

### Nível 3 — Anomalia em vídeo
- **Edite:** `app/levels/level3.py`
- **Implemente:** a função `analyze_video`.
- **Teste:** `pytest tests/acceptance/test_level3.py -v`

### Nível 4 — Treinar / avaliar / versionar
- **Edite:** `ml/train.py` e `ml/evaluate.py`
- **Implemente:** `train`, `save_versioned_model`, `evaluate`, `compute_dataset_hash`,
  `check_leakage`. A receita recomendada está em `GET /level4/recommended-config`.
- **Teste:** `pytest tests/acceptance/test_level4_versioning.py -v` (rápido) e
  `pytest tests/acceptance/test_level4_training.py -v` (lento — treina de fato).

### Nível 5 — Registro / deploy / design
- **Edite:** `ml/registry.py`. Depois **crie** `docs/DESIGN.md` a partir de
  `docs/DESIGN_TEMPLATE.md`.
- **Implemente:** a classe `ModelRegistry` (todos os métodos) + o doc de design.
- **Teste:** `pytest tests/acceptance/test_level5.py -v`
- O `ModelRegistry` descobre modelos versionados, troca a versão **ativa** em
  runtime (hot-swap, thread-safe) e carrega + faz cache de cada um sob demanda
  (lazy). O `docs/DESIGN.md` cobre escala, rollout, observabilidade, drift e modos
  de falha.

## 6. Entrega

1. **Publique sua solução em um repositório no seu GitHub pessoal.** Clone este
   desafio, trabalhe localmente e suba o resultado para um repositório **privado**
   na sua conta. Mantenha-o privado — **não** o torne público (veja a `LICENSE`) —
   e **compartilhe o acesso** com a equipe de recrutamento.
2. **Entregue como um repositório git**, não um arquivo `.zip`.
3. Rode `python dev.py test`, cole o resumo no `NOTES.md` e preencha o restante do
   `NOTES.md` (níveis tentados, decisões, onde parou; anote skips e o porquê).
4. **Avise a equipe de recrutamento quando finalizar** — inclusive se terminar
   antes do prazo.
5. **Prazo:** respeite o prazo combinado com o seu recrutador. Trabalho enviado
   após o prazo não é considerado na avaliação.

## 7. Referência

- Glossário de termos: `docs/GLOSSARY.md`.
- Travou no setup (Python errado, sem GPU, offline)? Anote no `NOTES.md` e continue
  no que puder.
