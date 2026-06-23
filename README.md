# Face Guard — Desafio de Engenharia de AI/ML

Boas-vindas! O Face Guard é um sistema de gerenciamento de vídeo que detecta
**faces, placas de veículos, objetos, sons e anomalias comportamentais** em
streams de câmeras, e treina e serve os modelos por trás disso. Este desafio
espelha esse trabalho.

Você vai progredir por **cinco níveis**, de uma API simples até treinar e fazer
deploy de um modelo. Cada nível já vem com uma estrutura base pronta (o
"scaffolding": imports, assinaturas de função, modelos de dados) e deixa algumas
funções para você implementar (marcadas com `TODO(candidate)`), além de um teste
automatizado que verifica seu trabalho.

> **Faça quantos níveis conseguir — qualidade acima de quantidade.**
> Um Nível 1–3 limpo e correto é um resultado forte. **Não** corra para o Nível 5
> às custas de níveis anteriores malfeitos. Valorizamos código correto, legível e
> bem commitado acima de abrangência.

---

## 1. O que avaliamos

- **Python** — código limpo, tipado e legível; estrutura sensata.
- **APIs** — endpoints FastAPI que respeitam um contrato.
- **Modelos** — consumir um detector pré-treinado (YOLO) e ler sua saída.
- **Vídeo & anomalias** — processamento de frames e lógica temporal (com debounce — exigir que a condição se mantenha por vários frames consecutivos antes de reagir).
- **Treino** — fine-tuning (re-treinar um modelo pré-treinado nos seus próprios dados), métricas de avaliação e **versionamento de modelo**.
- **Deploy** — um registro de modelos com hot-swap (trocar o modelo ativo em tempo de execução, sem reiniciar), mais um doc de design curto.
- **Higiene de engenharia** — Conventional Commits, versionamento semântico, testes.

Isso mapeia para o trabalho real. Usamos **formas sintéticas** (em vez de
faces/placas) e um cenário de **zone-intrusion** (em vez de comportamentos
específicos) de propósito: eles não precisam de dados sensíveis e são totalmente
reproduzíveis, ao mesmo tempo em que exercitam as mesmas habilidades
transferíveis — inferência load-once (carregar o modelo uma única vez), debounce temporal, treino/versão/serviço.

## 2. Requisitos

- **Python 3.11 ou 3.12** (obrigatório — `torch`/`ultralytics` não têm wheels
  fora dessa faixa; o `make setup` verifica isso para você).
- ~5 GB de disco livre, ~8 GB de RAM, e internet para o setup **único** (ele
  baixa o build CPU do PyTorch e os pesos `yolov8n.pt`). Sem GPU necessária.
- `make`, `git`.

> Tempo: **o setup não faz parte do seu trabalho cronometrado** — faça-o primeiro.
> Depois reserve algumas horas focadas. Se algo genuinamente não rodar na sua
> máquina, diga isso no `NOTES.md` e descreva como você *implementaria* — damos
> crédito parcial.

## 3. Início rápido (60 segundos)

```bash
make setup PYTHON=python3.12     # venv + deps + pesos + datasets (uma vez)
make test-fast                   # testes rápidos (sem treino); a maioria FALHA até você implementar
make run                         # sobe a API em http://127.0.0.1:8000/docs
```

O `make setup` roda uma verificação de preflight, instala as dependências
fixadas, baixa os pesos pré-treinados e gera os datasets. Depois abra os níveis
abaixo em ordem.

Comandos úteis:

| Comando | O que faz |
|---|---|
| `make test` | Suíte completa, **incluindo** os testes lentos de treino |
| `make test-fast` | Tudo exceto os testes lentos de torch/treino |
| `make run` | Roda a API (Swagger UI em `/docs`) |
| `make lint` | Faz lint com o ruff |
| `make check-commits` | Verifica seus Conventional Commits (consultivo — não reprova; é só aviso) |
| `make check-integrity` | Confirma que você não editou um arquivo protegido |

## 4. As regras

- **Implemente os stubs** (funções fornecidas só com assinatura e docstring, com o corpo a implementar). Edite apenas os arquivos com `TODO(candidate)`:
  `app/levels/level1.py`, `level2.py`, `level3.py`, `ml/train.py`,
  `ml/evaluate.py`, `ml/registry.py`. Você pode adicionar seus próprios arquivos/módulos.
- **Não edite arquivos protegidos** (o contrato + a maquinaria do avaliador):
  `app/schemas.py`, `app/main.py`, `app/config.py`, `app/levels/level4.py`,
  `app/levels/level5.py`, `ml/model_loader.py`, `ml/detectors.py`,
  `ml/versioning.py`, tudo em `tests/acceptance/`, `tests/conftest.py`,
  e `scripts/`. O `make check-integrity` te avisa se você escorregou.
  Acha que um arquivo protegido tem um bug? Não o edite — anote no `NOTES.md`.
- **Não enfraqueça os testes.** Adicione seus próprios testes em `tests/candidate/`
  se quiser. A execução oficial usa uma cópia intacta da suíte.
- **Commite conforme avança**, usando Conventional Commits, ~um (ou uma pequena
  série) por nível — ex.: `feat(level1): implementa endpoints de health e metadata`.
  (O tipo `feat`/`fix`/… e o escopo `(level1)` ficam em inglês; a descrição pode
  ser em português.)
- **Faça a tag do modelo** que você produzir no Nível 4: `git tag model/shapes-detector-v1.0.0`.

## 5. Os níveis

Cada nível abaixo diz **exatamente qual arquivo abrir**, **o que implementar
nele** e **como testar**. Em todo arquivo de stub, o que você precisa escrever
está marcado com um comentário `# TODO(candidate):` dentro de uma função cujo
corpo é `raise NotImplementedError` — substitua esse corpo pela sua
implementação. A docstring logo acima do `TODO` é o **contrato detalhado** (leia
com atenção; vários têm exemplos resolvidos). Você só edita os 6 arquivos de
stub listados; tudo o mais é fornecido (veja a seção 4).

Resumo de onde mexer:

| Nível | 📂 Arquivo(s) que VOCÊ edita | ✏️ O que implementar |
|---|---|---|
| 1 | `app/levels/level1.py` | `clamp_box`, `health`, `image_metadata` |
| 2 | `app/levels/level2.py` | `Detector.load`, `Detector.detect`, `get_detector`, endpoint `detect` |
| 3 | `app/levels/level3.py` | `analyze_video` |
| 4 | `ml/train.py` + `ml/evaluate.py` | `train`, `save_versioned_model` · `evaluate`, `compute_dataset_hash`, `check_leakage` |
| 5 | `ml/registry.py` + crie `docs/DESIGN.md` | `ModelRegistry` (todos os métodos) + o doc de design |

---

### Nível 1 — Fundamentos & FastAPI
- 📂 **Abra e edite:** `app/levels/level1.py`
- ✏️ **Implemente:** o helper puro `clamp_box`, o endpoint `GET /health` e o
  endpoint `POST /image/metadata` (retorna largura/altura/modo/formato de uma
  imagem enviada).
- ✅ **Teste:** `pytest tests/acceptance/test_level1.py -v`
- *Exemplo:* `POST /image/metadata` com um PNG 320×200 → `{"width":320,
  "height":200,"mode":"RGB","format":"PNG"}`.

### Nível 2 — Detecção de objetos (YOLO)
- 📂 **Abra e edite:** `app/levels/level2.py`
- ✏️ **Implemente:** a classe `Detector` (`load` carrega o `yolov8n` **uma só
  vez**; `detect` roda a inferência e devolve as detecções), o singleton
  (uma única instância compartilhada no processo todo) `get_detector` e o endpoint `POST /detect`.
- ✅ **Teste:** `pytest tests/acceptance/test_level2.py -v`
- O `POST /detect` recebe uma imagem (+ `?conf=` opcional) e devolve detecções
  `{label, confidence, box}`, ordenadas por confiança, filtradas pelo threshold,
  com as boxes ajustadas (clamp) aos limites da imagem.
- *Exemplo:* `POST /detect?conf=0.5` com uma foto → `{"model_id":"yolov8n",
  "count":2,"detections":[{"label":"person","confidence":0.91,"box":[…]}, …]}`.

### Nível 3 — Anomalia em vídeo
- 📂 **Abra e edite:** `app/levels/level3.py`
- ✏️ **Implemente:** a função `analyze_video`.
- ✅ **Teste:** `pytest tests/acceptance/test_level3.py -v`
- Percorra os frames, pule frames (frame-skip — pular frames para ganhar
  desempenho) para ganhar throughput (vazão/desempenho), e emita um evento de
  **zone-intrusion** quando um alvo permanece numa zona por `>= min_consecutive`
  frames processados (debounce — um blip de um único frame não pode disparar; e
  faça o flush — fechar/emitir o que está pendente — de um evento ainda aberto ao final do vídeo). **O contrato exato
  (com exemplo resolvido) está na docstring da função** — leia antes de codar.

### Nível 4 — Treinar / avaliar / versionar
- 📂 **Abra e edite:** `ml/train.py` e `ml/evaluate.py`
- ✏️ **Implemente:** em `ml/train.py`: `train` (fine-tuning) e
  `save_versioned_model`; em `ml/evaluate.py`: `evaluate` (métricas),
  `compute_dataset_hash` e `check_leakage`.
- ✅ **Teste:** `pytest tests/acceptance/test_level4_versioning.py -v` (rápido) e
  `pytest tests/acceptance/test_level4_training.py -v` (lento — treina de fato).
- Faça fine-tuning do `yolov8n` no dataset sintético de formas fornecido; compute
  métricas; verifique se há **leakage** (vazamento) entre treino/validação; e
  salve um artefato **versionado** mais um `model_card.json`. Fique dentro dos
  limites da receita (veja `GET /level4/recommended-config`). Avaliamos o seu
  pipeline e o seu *raciocínio* sobre as métricas, não uma pontuação de
  leaderboard.

### Nível 5 — Registro / deploy / design
- 📂 **Abra e edite:** `ml/registry.py`. Depois **crie** `docs/DESIGN.md`
  copiando o template `docs/DESIGN_TEMPLATE.md` e preenchendo-o.
- ✏️ **Implemente:** a classe `ModelRegistry` (todos os métodos) + escreva o doc
  de design.
- ✅ **Teste:** `pytest tests/acceptance/test_level5.py -v`
- O `ModelRegistry` descobre modelos versionados, troca a versão **ativa** em
  runtime (**hot-swap**, seguro sob concorrência — thread-safe) e carrega + faz cache de cada
  um sob demanda (lazy — carregar só na primeira vez que é preciso). O `docs/DESIGN.md` cobre escala, rollout (liberação gradual de uma nova versão),
  observabilidade, drift (degradação do modelo ao longo do tempo) e modos de falha — é aqui que entram as decisões de
  arquitetura e operação em produção.

## 6. Versionamento de modelo (SemVer)

**SemVer** (*Semantic Versioning*, ou Versionamento Semântico) é a convenção de
numerar versões como `MAJOR.MINOR.PATCH` — três números, por exemplo `2.1.3`.
Cada número tem um significado e você "incrementa" (em inglês, *bump*) o número
certo conforme o tipo de mudança:

- **MAJOR** — mudança incompatível (quem usava a versão antiga pode quebrar);
- **MINOR** — adição compatível (nada quebra);
- **PATCH** — correção/ajuste sem mudança de comportamento.

Ao subir um número, os menores à direita voltam a zero (ex.: `1.4.2` → MINOR →
`1.5.0`). No Nível 4 você aplica essa ideia a um **modelo**: seu artefato é
nomeado `shapes-detector-vMAJOR.MINOR.PATCH.pt` (use os helpers de
`ml/versioning.py`, ex.: `model_filename(...)` e `bump(...)`), e o `model_card.json`
carrega a mesma versão. A regra para um modelo de detecção:

| Mudança | Bump |
|---|---|
| Retrain de bugfix, mesmo comportamento | **PATCH** (1.0.0 → 1.0.1) |
| Novo treino / mais dados, mesmas classes & I/O | **MINOR** (1.0.0 → 1.1.0) |
| Mudança no conjunto de classes ou no contrato de entrada/saída | **MAJOR** (1.0.0 → 2.0.0) |

## 7. Submetendo

Trabalhe em uma branch com **commits reais e incrementais** (nós olhamos seu
histórico — por favor não faça squash em um único dump, e não envie um zip que
perca o histórico do git). Quando terminar:

1. `make test` e cole o resumo no `NOTES.md` (anote quaisquer skips e o porquê).
2. Preencha o `NOTES.md` (níveis tentados, decisões, onde parou).
3. Faça push da sua branch e compartilhe o acesso (seu recrutador dirá onde), ou
   `git bundle create submission.bundle --all` se precisar entregar um arquivo.

Um walkthrough ao vivo curto (conversa ao vivo de revisão do código com o candidato) do seu código pode vir depois — esteja pronto para
explicar e estender suas escolhas.

## 8. Precisa de ajuda?

- Glossário de termos: `docs/GLOSSARY.md`.
- Travou no setup (Python errado, sem GPU, offline)? Escreva no `NOTES.md` e
  continue no que você puder — crédito parcial é real.

Boa sorte — estamos animados para ver como você pensa.
