# Glossário

Definições curtas e diretas dos termos usados neste desafio.

- **Bounding box (`box`)** — `[x1, y1, x2, y2]` em pixels, origem no canto superior
  esquerdo, com `x1 <= x2` e `y1 <= y2`.
- **Confiança** — a pontuação do modelo para uma detecção, um float em `[0, 1]`.
- **Clamp** — empurrar as coordenadas de volta para dentro da imagem, de modo que
  uma box nunca fique para fora.
- **Frame processado** — um frame de vídeo no qual o detector é de fato executado;
  os demais são pulados conforme `frame_skip`.
- **Debounce** — exigir que uma condição se mantenha por vários frames consecutivos
  antes de reagir, para que um blip de um único frame não dispare um evento.
- **Image mode** — a string de modo de cor do PIL (`"RGB"`, `"L"`, …).
- **Zona / região de interesse** — um retângulo no frame, usado para marcar a
  presença de uma detecção.
- **mAP@0.5 (`map50`)** — mean Average Precision em IoU 0.5; uma métrica padrão de
  acurácia de detecção em `[0, 1]`.
- **IoU** — Intersection-over-Union: área de interseção ÷ área de união de duas boxes.
- **Leakage** — a mesma imagem acabando tanto no treino quanto na validação, o que
  faz suas métricas parecerem melhores do que realmente são.
- **Semantic Versioning (`MAJOR.MINOR.PATCH`)** — esquema de versionamento em três números.
- **Model card** — um pequeno JSON ao lado dos pesos registrando versão, métricas,
  configuração de treino, hash do dataset, etc. — o "rótulo" do modelo.
- **Versão ativa** — a versão do modelo que o serviço está servindo no momento.
- **Hot-swap** — trocar a versão ativa em tempo de execução, sem reiniciar.
- **Conventional Commits** — padrão de mensagem `tipo(escopo): resumo`, ex.
  `feat(level2): adiciona o endpoint /detect`. O tipo (`feat`, `fix`, `refactor`,
  `docs`, …) fica em inglês; a descrição pode ser em português.
- **Bump (de versão)** — incrementar um número da versão (ver Semantic Versioning).
- **Stub** — função/método fornecido só com a assinatura e a docstring, cujo
  corpo é `raise NotImplementedError` — é o que você implementa.
- **Arquivo protegido / não-editar** — código fornecido que você não deve modificar (o
  contrato + a infraestrutura de teste). Implemente os STUBS em vez disso.
- **Fine-tuning** — re-treinar um modelo já pré-treinado nos seus próprios dados,
  em vez de treinar do zero.
- **Drift** — degradação do modelo ao longo do tempo, conforme os dados de produção
  vão se afastando dos dados de treino.
- **Rollout** — liberação gradual de uma nova versão para produção.
- **Shadow / Canary** — estratégias de rollout gradual. No *shadow*, a nova versão roda
  em paralelo recebendo o mesmo tráfego, mas suas saídas não são usadas (só comparadas).
  No *canary*, a nova versão atende a uma fração pequena do tráfego real antes de ir a 100%.
- **Rollback** — voltar para a versão anterior depois de detectar um problema.
- **Throughput** — vazão/desempenho: quantos itens (frames, requisições) o sistema
  processa por unidade de tempo.
- **Thread-safe** — seguro sob acesso concorrente de várias threads ao mesmo tempo.
- **Singleton** — uma única instância compartilhada no processo inteiro.
- **Lazy** — carregar/inicializar algo só na primeira vez que ele é de fato necessário.
