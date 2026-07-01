# Simulador da Mic-1 Modificada

Projeto da disciplina **Arquitetura de Computadores II** (UFPB-CI-DSC, Profª. Sarah Pontes Madruga), que implementa em Python, de forma incremental, uma microarquitetura baseada na máquina Mic-1 apresentada por Tanenbaum, capaz de interpretar instruções da ISA da IJVM.

O projeto é dividido em etapas, cada uma em sua própria pasta, construindo progressivamente a ULA, o caminho de dados e, por fim, o acesso à memória e a tradução de instruções da IJVM em microinstruções.

## Integrantes

- Leandro Cipriano
- Luiz Eduardo dos Santos
- Rickison de Lima Paula
- Ryan Costa Sobreira

---

## Etapas

### Etapa 1 — ULA da Mic-1 (6 bits)

Implementação da ULA da Mic-1 com sinais de controle de 6 bits (`F0 F1 ENA ENB INVA INC`), lendo uma sequência de instruções de um arquivo `.txt` e gerando um log com IR, PC, A, B, S e Vai-um a cada ciclo.


### Etapa 2, Tarefa 1 — ULA de 8 bits com deslocador

Pasta: [`etapa2t1/`](etapa2t1/)

Extensão da ULA da Etapa 1 para uma palavra de controle de 8 bits (`SLL8 SRA1 F0 F1 ENA ENB INVA INC`), adicionando o deslocador (lógico à esquerda em 8 bits ou aritmético à direita em 1 bit) e as saídas N (negativo) e Z (zero).

### Etapa 2, Tarefa 2 — Caminho de dados completo

Pasta: [`etapa2t2/`](etapa2t2/)

Implementação dos dez registradores da Mic-1 (H, OPC, TOS, CPP, LV, SP, PC, MDR, MAR e MBR), do decodificador de 4 bits do barramento B e do seletor de 9 bits do barramento C. O código passa a interpretar instruções de 21 bits (`ULA[8] C[9] B[4]`), conectando a ULA aos registradores conforme o caminho de dados da Mic-1, e gera um log completo do estado dos registradores antes/depois de cada ciclo.

---

## Execução

Cada etapa é independente e é executada a partir de sua própria pasta:

```bash
cd etapa1
python etapa1.py

cd etapa2t1
python etapa2t1.py

cd etapa2t2
python etapa2t2.py
```

Os arquivos de entrada (registradores/instruções) e o arquivo de saída gerado ficam dentro da pasta de cada etapa.
