# Design de Deployment — <seu nome>

> Entregável do nível 5. Copie este arquivo para `docs/DESIGN.md` e preencha-o.
> Mantenha concreto: **3–6 bullets por seção**, com números e trade-offs
> específicos no lugar de boas práticas genéricas. ~1–2 páginas no total.
>
> Contexto: o sistema roda muitas câmeras em **servidores on-premise** (um único
> tenant pode ter vários). Cada servidor puxa RTSP, roda detecção e serve alertas.
> Os modelos são artefatos versionados (nível 4) servidos por um registry com
> hot-swap (nível 5). Assuma um mix de CPU+GPU, redes não confiáveis, e que uma
> troca de modelo não pode derrubar detecções ao vivo.

## 1. Serving em escala (N câmeras, M servidores)
- Como um servidor serve detecção para, digamos, 16–64 câmeras? Batching? Uma
  instância de modelo ou várias? Onde está o gargalo (decode / inferência / I/O)?
- Como as câmeras mapeiam para os servidores, e o que acontece quando um servidor
  morre?

## 2. Segurança do rollout / hot-swap de modelo
- Como você faz o rollout de uma nova versão de modelo sem derrubar detecções?
- Shadow vs canary: qual, para quê, e como você decide promover/fazer rollback?
- Qual é o gatilho de rollback e quão rápido ele é?

## 3. Observabilidade
- As 3–5 métricas que você observaria (com thresholds de alerta aproximados).
- Como é uma linha de log estruturado para uma detecção/inferência?

## 4. Drift & retraining
- Como você perceberia que o modelo está sofrendo drift / degradando em produção?
- Qual sinal dispara um retrain, e como o novo modelo chega ao passo 2?

## 5. Modos de falha & degradação graciosa
- Liste ≥3 modos de falha concretos (ex.: pesos corrompidos, GPU OOM, câmera
  offline, registry vazio) e, para CADA um: como você o detecta e o que o sistema
  faz em vez de crashar.

## 6. Thread-safety do hot-swap (amarre ao seu código)
- Por que o seu `ModelRegistry.set_active` é seguro quando chamado em paralelo com
  leituras de `/detect`?
- O que poderia dar errado sob concorrência, e como o seu design evita isso?

## 7. (Opcional) O que muda para diferentes domínios (faces, placas, áudio)
- ex.: faces precisam de embeddings + uma história de privacidade/retenção; áudio
  precisa de windowing.
