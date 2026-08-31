# NetGuard ML

Classificação de fluxos de tráfego de rede em Normal ou Attack, a partir do subsample CICIoT2023.

## Linguagem

**Fluxo**:
Uma linha do subsample: o CIC já agregou o tráfego em features de fluxo (duração, IAT, flags, indicadores de protocolo). É a unidade que o modelo classifica.
_Avoid_: observação, pacote, evento, janela, sample

**Normal**:
Classe do modelo para tráfego benigno. Corresponde a `label == 0` no subsample.
_Avoid_: benign, BenignTraffic, harmless

**Attack**:
Classe do modelo para qualquer fluxo não benigno. Corresponde a `label == 1`. Agrupa todos os tipos CIC, inclusive floods ICMP.
_Avoid_: malicious, threat, anomalia, “tipo de ataque” como saída do modelo

**label**:
Coluna binária do subsample (`0` / `1`). É o alvo de treino, não o nome da classe na saída.
_Avoid_: usar `label` como se fosse o tipo CIC

**Label**:
Tipo de ataque CICIoT (34 valores, inclusive `BenignTraffic`). Só para EDA e diagnóstico. Não é saída do primeiro modelo.
_Avoid_: Label na predição; confundir com `label`

**attack_class**:
Família do ataque (Benign, DDoS, DoS, Recon, Mirai, Spoofing, Web-based, BruteForce). Só para EDA.
_Avoid_: attack_class na predição

**Split**:
A partição publicada `train` / `validation` / `test`. Não se reembaralha o corpus para criar outra divisão.
_Avoid_: split aleatório novo, misturar validation/test na exploração

**Recorte de EDA**:
Amostra estratificada tirada **somente do train**, para iterar rápido. Decisão que vire regra (dropar coluna, declarar desbalanceamento, afirmar vazamento) confirma-se no train completo.
_Avoid_: tratar o recorte como teste; incluir validation/test no recorte

**Subsample CICIoT**:
O recorte HuggingFace `random_3way` que o projeto treina. Não é um dataset novo; a citação continua sendo o artigo do CIC.
_Avoid_: CICIoT completo (46,7 M linhas); RIPE Atlas como teste do classificador

**Indicador ICMP**:
A coluna `ICMP` do subsample: presença agregada do protocolo no Fluxo. Não é tipo ICMP, código ICMP, taxa de echo nem latência de ping — essas colunas não existem neste fonte.
_Avoid_: tipo ICMP, código ICMP, echo request/reply, latência de ping, captura de pacotes para “completar” o schema

**Vazamento**:
Contaminação entre treino e avaliação: usar `Label` / `Label_orig` / `attack_class` / `label` como feature; tomar decisão de EDA ou preprocessing olhando validation/test; Fluxos duplicados entre Splits; tratar ordem das linhas ou `IAT` como tempo.
_Avoid_: “data leak” sem dizer qual regra foi quebrada

**Janela temporal**:
Não se aplica a este fonte. Sem relógio de captura, janela só poderia usar ordem de linha, que não é tempo. Ver ADR-0001.
_Avoid_: agregar Fluxos em N segundos neste subsample
