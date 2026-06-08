# CLAUDE.md — Jutsu de Invocação (Kuchiyose no Jutsu) — Pose Estimation

## Contexto do Projeto

Projeto acadêmico de **Processamento de Imagens** (T4 da P1).

**Objetivo:** Implementar um sistema de reconhecimento do **Jutsu de Invocação (Kuchiyose no Jutsu)** do anime Naruto, detectando em tempo real via webcam a sequência correta de 7 gestos de mão usando **MediaPipe Hands**.

**Modelo utilizado:** MediaPipe Hands (BlazePalm + Hand Landmark Model — 21 keypoints 3D por mão)

**Entrega:** Vídeo demonstração + explicação da fundamentação matemática + métricas de avaliação. Post no Instagram marcando `@profharoldogomes`.

---

## Ambiente

- **OS:** WSL2 com Ubuntu (Windows)
- **Webcam:** Acessada via `/dev/video0` através do WSL2
- **Python:** 3.10+
- **Display:** GUI via X11 forwarding ou `cv2.imshow` nativo do WSL2

### Atenção WSL2 + Webcam

O WSL2 por padrão não expõe dispositivos USB. Para acessar a webcam é necessário:
1. Usar **usbipd-win** no Windows para fazer attach da webcam ao WSL2
2. OU gravar o vídeo no Windows e processar no WSL2 (alternativa mais simples)
3. OU rodar o script Python diretamente no **Windows nativo** (fora do WSL2) usando o Python do Windows

**Recomendação:** Rodar o projeto no **Python do Windows nativo** (não dentro do WSL2) para evitar problemas com webcam e display. Usar o terminal do WSL2 apenas para edição de arquivos se preferir.

---

## Estrutura do Projeto

```
kuchiyose/
├── CLAUDE.md               # este arquivo
├── requirements.txt
├── main.py                 # entry point — loop principal webcam
├── detector.py             # wrapper MediaPipe Hands
├── seals.py                # lógica de detecção de cada selo
├── state_machine.py        # máquina de estados da sequência
├── overlay.py              # efeito visual / overlay no frame
├── metrics.py              # coleta e exibe métricas
└── assets/
    └── (imagens opcionais para overlay)
```

---

## Dependências

```
mediapipe
opencv-python
numpy
```

Instalar com:
```bash
pip install mediapipe opencv-python numpy
```

---

## Fundamentação Matemática (para apresentação)

### MediaPipe Hands — Pipeline em dois estágios

**Estágio 1 — BlazePalm (detector de palma):**
- CNN leve treinada para detectar a **bounding box da palma**
- Usa âncoras em múltiplas escalas
- Retorna região de interesse (ROI) da mão

**Estágio 2 — Hand Landmark Model:**
- Recebe o crop da palma do BlazePalm
- Regride **21 keypoints 3D** `(x, y, z)` diretamente (regressão, não heatmap)
- `x, y` são coordenadas normalizadas [0,1] em relação ao frame
- `z` representa profundidade relativa ao pulso (negativo = mais próximo da câmera)

### Mapa dos 21 Landmarks

```
0  = Pulso (WRIST)
1  = Polegar CMC       2  = Polegar MCP      3  = Polegar IP       4  = Polegar TIP
5  = Indicador MCP     6  = Indicador PIP     7  = Indicador DIP    8  = Indicador TIP
9  = Médio MCP        10  = Médio PIP        11  = Médio DIP       12  = Médio TIP
13 = Anelar MCP       14  = Anelar PIP       15  = Anelar DIP      16  = Anelar TIP
17 = Mindinho MCP     18  = Mindinho PIP     19  = Mindinho DIP    20  = Mindinho TIP
```

### Lógica de dedo estendido vs dobrado

Um dedo está **estendido** quando a ponta (TIP) está mais distante do pulso do que a articulação intermediária (PIP) no eixo Y (ou distância euclidiana).

```
dedo_estendido = landmark[TIP].y < landmark[PIP].y  # y cresce para baixo
```

Para o polegar, a lógica usa o eixo X devido à orientação diferente.

---

## Sequência do Jutsu de Invocação

A sequência deve ser detectada **em ordem**. A máquina de estados só avança quando o gesto atual for confirmado.

| Estado | Gesto | Índice |
|--------|-------|--------|
| 0 | Morder o dedo (indicador próximo ao rosto) | `BITE` |
| 1 | Selo do Porco (I) — punho fechado | `PIG` |
| 2 | Selo do Cachorro (Inu) — indicador e mindinho estendidos | `DOG` |
| 3 | Selo do Galo (Tori) — polegar, indicador e médio estendidos | `ROOSTER` |
| 4 | Selo do Macaco (Saru) — todos estendidos exceto anelar | `MONKEY` |
| 5 | Selo da Ovelha (Hitsuji) — apenas médio e anelar estendidos | `RAM` |
| 6 | Palma no chão — mão plana horizontal, todos estendidos | `GROUND` |

---

## Estratégia de Detecção por Gesto

### Estado 0 — Morder o dedo (BITE)
- Indicador estendido (ponta landmarks 8)
- Posição Y do landmark 8 está na metade superior do frame (`landmark[8].y < 0.4`)
- Aproximação: mão elevada no frame

### Estado 1 — Porco (PIG) — punho fechado
- Todos os 4 dedos dobrados: TIP.y > PIP.y para indicador, médio, anelar e mindinho
- Polegar dobrado: TIP.x próximo do landmark 2 (base do polegar)

### Estado 2 — Cachorro (DOG)
- Indicador estendido (8.y < 6.y)
- Mindinho estendido (20.y < 18.y)
- Médio dobrado (12.y > 10.y)
- Anelar dobrado (16.y > 14.y)

### Estado 3 — Galo (ROOSTER)
- Polegar estendido
- Indicador estendido
- Médio estendido
- Anelar dobrado
- Mindinho dobrado

### Estado 4 — Macaco (MONKEY)
- Todos os dedos estendidos exceto anelar dobrado
- Polegar, indicador, médio e mindinho: estendidos
- Anelar: dobrado (16.y > 14.y)

### Estado 5 — Ovelha (RAM)
- Apenas médio e anelar estendidos
- Indicador dobrado, mindinho dobrado, polegar dobrado

### Estado 6 — Palma no chão (GROUND)
- Todos os dedos estendidos
- Mão orientada horizontalmente: diferença entre landmark[0].y e landmark[12].y pequena
- OU: landmark[0].y e landmark[9].y com diferença mínima (pulso e base do médio no mesmo nível)

---

## Máquina de Estados

```
IDLE (aguardando início)
  ↓ detectou BITE
ESTADO 1 — aguarda PIG
  ↓ detectou PIG
ESTADO 2 — aguarda DOG
  ...
  ↓ detectou GROUND
INVOCAÇÃO! (overlay de efeito + mensagem)
  ↓ após 3 segundos
IDLE (reset)
```

**Regras:**
- Cada gesto deve ser mantido por **N frames consecutivos** (ex: 15 frames) para confirmar — evita falsos positivos
- Se ficar mais de **X segundos** sem avançar no estado atual, reseta para IDLE
- Exibir na tela o estado atual e o próximo gesto esperado

---

## Overlay Visual

- Desenhar os 21 landmarks e conexões da mão no frame
- Exibir barra de progresso da sequência (ex: `[■■■□□□□]`)
- Exibir nome do gesto atual detectado
- Ao completar: efeito de texto animado `"KUCHIYOSE NO JUTSU!"` + tint vermelho no frame
- Exibir métricas no canto: FPS, confiança dos landmarks, estado atual

---

## Métricas de Avaliação

Coletar e exibir ao final:

| Métrica | Descrição |
|---------|-----------|
| FPS médio | `frames_processados / tempo_total` |
| Confiança média | Média do score de detecção do MediaPipe por frame |
| Tempo por gesto | Quantos segundos levou para confirmar cada selo |
| Taxa de acerto | % de frames em que o gesto correto foi detectado no estado certo |
| Frames totais | Total processado |

---

## Orientações de Implementação

- Usar `mp.solutions.hands.Hands(max_num_hands=1)` para simplificar
- Threshold de confiança recomendado: `min_detection_confidence=0.7`, `min_tracking_confidence=0.5`
- Processar sempre em **RGB** para o MediaPipe (converter de BGR do OpenCV com `cv2.cvtColor`)
- Para `cv2.imshow` funcionar no Windows nativo, não precisa de configuração extra
- Salvar o vídeo de saída com `cv2.VideoWriter` para entrega

---

## Notas Acadêmicas

- O projeto argumenta conceitualmente que **estimação de pose das mãos** é um subproblema de estimação de pose, com maior granularidade necessária para detecção de selos
- O MediaPipe Hands usa **regressão direta de landmarks** (diferente de abordagens baseadas em heatmap como MoveNet), o que é um diferencial arquitetural relevante para apresentar
- A máquina de estados sequencial demonstra aplicação prática de reconhecimento de gestos em tempo real

---

## Comandos úteis

```bash
# Instalar dependências
pip install mediapipe opencv-python numpy

# Rodar projeto
python main.py

# Testar acesso à webcam
python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
```
