# Simulador da ULA da Mic-1 - Etapa 1

## Resumo Executivo

Este é um simulador em Python da Unidade Lógica e Aritmética (ULA) da máquina virtual Mic-1, implementando a Etapa 1 (APS) do projeto de Arquitetura de Computadores II.

## Operações da ULA

A ULA executa 4 operações lógico-aritméticas selecionadas por 6 bits de controle:

| F0 | F1 | Operação | Descrição |
|----|----|-----------|----|
| 0  | 0  | AND | Operação E bit a bit |
| 0  | 1  | OR | Operação OU bit a bit |
| 1  | 0  | NOT B | Complementa B |
| 1  | 1  | SOMA | Soma aritmética com carry |

**Sinais de Controle:**
- **ENA**: Habilita entrada A (desabilitado = 0)
- **ENB**: Habilita entrada B (desabilitado = 0)
- **INVA**: Se 1, força saída s=0 e carry=1 (ignora operação)
- **INC**: Incrementa resultado (apenas em SOMA)

## Formato do Arquivo de Entrada

Arquivo `programa_etapa1.txt`:

```
B_inicial (32 bits binários)
A_inicial (32 bits binários)
A_ciclo1 (32 bits binários)
IR1 (6 bits)
A_ciclo2 (32 bits binários)
IR2 (6 bits)
A_ciclo3 (32 bits binários)
IR3 (6 bits)
...
```

## Lógica da ULA

```python
if INVA == 1:
    s = 0
    co = 1
else:
    A_eff = A if ENA else 0
    B_eff = B if ENB else 0
    
    if F0==0, F1==0:    s = A_eff & B_eff
    elif F0==0, F1==1:  s = A_eff | B_eff
    elif F0==1, F1==0:  s = ~B_eff
    else:               s = A_eff + B_eff + INC
    
    co = 1 if s > 0xFFFFFFFF else 0
```

## Execução

```bash
python etapa1.py
```

**Entrada:** `programa_etapa1.txt`  
**Saída:** `saida_etapa1.txt`

Formato da saída:
```
b = [32 bits]
a = [32 bits]

Start of Program
============================================================
Cycle 1

PC = 1
IR = [6 bits]
b = [32 bits]
a = [32 bits]
s = [32 bits]
co = [1 bit]
============================================================
Cycle 2
...
```

## Observações Importantes

- INVA=1 **sempre** força s=0 e co=1, ignorando a operação
- NOT B inverte todos os 32 bits de B
- Carry é detectado quando resultado > 0xFFFFFFFF
- Valores são em complemento a 2 de 32 bits
- PC (Program Counter) começa em 1

## Exemplo

**Entrada:**
```
00000000000000000000000000000001  (B = 1)
11111111111111111111111111111111  (A = -1)
11111111111111111111111111111111  (A ciclo 1 = -1)
111100                            (IR1: SOMA, ENA=1, ENB=1, INVA=1, INC=0)
```

**Saída esperada (Ciclo 1):**
```
PC = 1
IR = 111100
b = 00000000000000000000000000000001
a = 11111111111111111111111111111111
s = 00000000000000000000000000000000  (INVA=1 → s=0)
co = 1                                (INVA=1 → co=1)
```

---

**Status:** ✅ Funcionando corretamente - Etapa 1 implementada
