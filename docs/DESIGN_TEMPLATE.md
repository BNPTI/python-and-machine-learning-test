# Design de Deployment — <seu nome>

> Entregável do nível 5. Copie este arquivo para `docs/DESIGN.md` e preencha-o.
> Mantenha concreto: **3–6 bullets por seção**, números/trade-offs específicos no
> lugar de boas práticas genéricas. Avaliamos a especificidade *deste* sistema, não a
> cobertura de buzzwords. ~1–2 páginas no total.
>
> Contexto: o Face Guard roda muitas câmeras em **servidores on-premise** (um único
> tenant pode ter vários). Cada servidor puxa RTSP (protocolo de streaming de vídeo das
> câmeras), roda detecção (faces / placas /
> objetos) e serve alertas. Os modelos são artefatos versionados (nível 4) servidos por
> um registry (registro central de modelos) com hot-swap (trocar o modelo ativo em tempo
> de execução, sem reiniciar) (nível 5). Assuma um mix de CPU+GPU (GPU: placa de vídeo
> usada para acelerar a inferência), redes não confiáveis,
> e que uma troca de modelo não pode derrubar detecções ao vivo.

## 1. Serving em escala (N câmeras, M servidores)
- Como um servidor serve detecção para, digamos, 16–64 câmeras? Batching (agrupar
  vários frames numa única passada de inferência para ganhar desempenho)? Uma
  instância de modelo ou várias? Onde está o gargalo (decode / inferência / I/O)?
- Como as câmeras mapeiam para os servidores, e o que acontece quando um servidor morre?

## 2. Segurança do rollout / hot-swap de modelo
- Como você faz o rollout (liberação gradual de uma nova versão) de uma nova versão de
  modelo sem derrubar detecções?
- Shadow vs canary (estratégias de rollout gradual): qual, para quê, e como você decide
  promover/fazer rollback (voltar à versão anterior)?
- Qual é o gatilho de rollback e quão rápido ele é?

## 3. Observabilidade (capacidade de enxergar o estado interno do sistema via métricas e logs)
- As 3–5 métricas que você observaria (com thresholds de alerta aproximados).
- Como é uma linha de log estruturado para uma detecção/inferência?

## 4. Drift & retraining
- Como você perceberia que o modelo está sofrendo drift (degradação ao longo do tempo) /
  degradando em produção (faces/placas)?
- Qual sinal dispara um retrain (re-treino), e como o novo modelo chega ao passo 2?

## 5. Modos de falha & degradação graciosa
- Liste ≥3 modos de falha concretos (ex. pesos corrompidos, GPU OOM (memória da GPU
  esgotada), câmera offline,
  registry vazio) e, para CADA um: como você o detecta e o que o sistema faz
  em vez de crashar.

## 6. Thread-safety (segurança sob acesso concorrente de várias threads) do hot-swap (amarre ao seu código)
- Por que o seu `ModelRegistry.set_active` é seguro sob tráfego concorrente de `/detect`?
- Qual exatamente é o passo atômico, e o que quebraria sem o lock?

## 7. (Opcional) O que muda para faces vs placas vs áudio
- ex. faces precisam de embeddings (vetores numéricos que representam o rosto) + uma
  história de privacidade/retenção; áudio precisa de windowing (fatiar o sinal em janelas
  de tempo).
