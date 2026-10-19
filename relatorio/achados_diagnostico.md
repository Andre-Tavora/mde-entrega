# Achados - Diagnostico de dados (rotulos de origem)

## A1. Rotulo disciplina_origem ruidoso
- 4 grafias para 2 disciplinas: "Penal" / "Direito Penal"; "Processo Penal" / "Direito Processual Penal".
- 1 rotulo vazio (Q0036) e 1 generico ("Disciplina Unificada", Q0014).

## A2. Rotulo errado com conteudo penal (6/359 = 1,7%)
| id | rotulo | conteudo real | decisao |
|---|---|---|---|
| Q0014 | Disciplina Unificada | ECA / HC em internacao | revisar |
| Q0016 | Constitucional | Prisao preventiva de oficio (L. 13.964/19) | revisar |
| Q0036 | (vazio) | Lei Maria da Penha | revisar |
| Q0137 | Civil - Leg. Especial | Investigacao pelo delegado (L. 12.830/13) | revisar |
| Q0218 | Constitucional | Estelionato tentado / falso (auditada C) | publicar |
| Q0277 | Civil - Leg. Especial | Crimes do Estatuto do Idoso | revisar |
| Q0309 | Ambiental | Crime ambiental art. 61 L. 9.605/98 | revisar |

## A3. Unico "fora" verdadeiro
- Q0142: Direito Tributario (isencao de ITCD/PA). Auditada C, conf 0,96.

## Implicacao
- O pipeline classifica pelo conteudo, sem confiar no rotulo: zero falsos "fora".
- Producao: rotulo de origem = feature auxiliar, nunca filtro rigido.
