# Simulador da ULA da Mic-1 - Etapa 1

## 📋 Visão Geral

Este projeto implementa um simulador em Python da **Unidade Lógica e Aritmética (ULA)** da máquina virtual Mic-1, correspondente à **Etapa 1 (APS)** do projeto de Arquitetura de Computadores II da UFPB.

A ULA é o componente central do processador, responsável por executar operações lógicas e aritméticas sob controle de sinais de 6 bits.

---

## 🔧 Como a ULA Funciona

### Entradas e Saídas

A ULA recebe:
- **2 operandos** (A e B) de 32 bits cada
- **6 sinais de controle** que determinam a operação a ser executada

E produz:
- **1 resultado** (S) de 32 bits
- **1 bit de carry** (vai-um) indicando overflow

### Estrutura da Instrução (6 bits)

```
Posição:  0   1   2    3    4     5
Sinal:   F0  F1  ENA  ENB  INVA  INC
```

| Sinal | Descrição |
|-------|-----------|
| **F0, F1** | Selecionam a operação (2 bits = 4 operações) |
| **ENA** | Habilita entrada A (se 0, A vira 0) |
| **ENB** | Habilita entrada B (se 0, B vira 0) |
| **INVA** | Inverte A (complemento a 2) |
| **INC** | Força carry-in = 1 (soma + 1) |

### Tabela de Operações

| F0 | F1 | Operação | Descrição |
|----|----|-----------|----|
| 0  | 0  | AND | S = A & B |
| 0  | 1  | OR | S = A \| B |
| 1  | 0  | XOR | S = A ^ B |
| 1  | 1  | SOMA | S = A + B (+ 1 se INC=1) |

### Exemplos de Uso

#### Exemplo 1: Soma Simples
```
Instrução: 111100
F0=1, F1=1 → Soma
ENA=1, ENB=1 → Ambos habilitados
INVA=0 → A não invertido
INC=0 → Sem incremento

Com A=1, B=1:
Resultado: S = 1 + 1 = 2 (0x00000002)
Vai-um: 0 (sem overflow)
```

#### Exemplo 2: AND com Habilitação Seletiva
```
Instrução: 100100
F0=1, F1=0 → XOR
ENA=0 → A desabilitado (= 0)
ENB=0 → B desabilitado (= 0)
INVA=1 → A invertido (mas já é 0)
INC=0 → Sem incremento

Resultado: S = 0 XOR 0 = 0
Vai-um: 0
```

#### Exemplo 3: Soma com Incremento
```
Instrução: 111101
F0=1, F1=1 → Soma
ENA=1, ENB=1 → Ambos habilitados
INVA=0 → A não invertido
INC=1 → Com incremento

Com A=5, B=3:
Resultado: S = 5 + 3 + 1 = 9
Vai-um: 0 (sem overflow)
```

---

## 💻 Implementação em Python

### Arquitetura do Código

O programa consiste em 2 classes principais:

#### 1. Classe `ULA`

Simula a lógica combinatória da Unidade Lógica e Aritmética.

```python
class ULA:
    def executar(self, F0, F1, ENA, ENB, INVA, INC, A, B):
        # Retorna (S, vai_um)
```

**Fluxo interno:**

1. **Aplicar INVA**: Se INVA=1, inverte A (complemento a 2 de 32 bits)
2. **Aplicar habilitações**: Se ENA=0 ou ENB=0, substitui por 0
3. **Selecionar operação**: 
   - AND, OR, XOR → operações bit a bit, sem carry
   - SOMA → soma aritmética com possível carry
4. **Aplicar INC**: Se INC=1 na soma, adiciona 1
5. **Calcular carry**: Detecta se resultado > 2³² - 1

#### 2. Classe `Simulador`

Orquestra a execução do programa e gera relatórios.

```python
class Simulador:
    def executar_programa(self, arquivo_entrada, arquivo_saida):
        # Executa programa e gera log
```

**Métodos principais:**

- `carregar_programa()`: Lê instruções do arquivo
- `extrair_bits()`: Decompõe os 6 bits em seus componentes
- `executar_programa()`: Loop principal de simulação
- `_escrever_log()`: Gera arquivo de saída formatado

---

## 🚀 Como Usar

### 1. Preparar o Arquivo de Entrada

Crie um arquivo `programa_etapa1.txt` com instruções em binário (6 bits por linha):

```
111100
101010
110011
000000
011111
```

**Ou execute o script, que criará um arquivo exemplo automaticamente:**

```bash
python etapa1.py
```

### 2. Executar o Simulador

```bash
python etapa1.py
```

O programa irá:
1. Carregar `programa_etapa1.txt`
2. Executar cada instrução sequencialmente
3. Gerar `saida_etapa1.txt` com o log completo

### 3. Analisar os Resultados

Abra `saida_etapa1.txt`:

```
PC  IR (bin)  IR (dec)  A              B              S              Vai-um  Operação
0   111100    60        1              0              1              0       SOMA
1   101010    42        1              1              0              1       XOR
2   110011    51        0              0              0              0       SOMA (~A)
3   000000    0         0              0              0              0       AND
4   011111    31        0              0              0              0       OR +1
```

Cada coluna representa:
- **PC**: Program Counter (número da instrução)
- **IR (bin)**: Instrução em binário
- **IR (dec)**: Instrução em decimal
- **A**: Valor do operando A
- **B**: Valor do operando B
- **S**: Resultado da operação
- **Vai-um**: Bit de carry (overflow)
- **Operação**: Descrição legível da operação

---

## 🔍 Detalhes Técnicos

### Operações Lógicas (AND, OR, XOR)

Trabalham **bit a bit** sobre os operandos:

- **AND**: S[i] = A[i] & B[i] (1 se ambos forem 1)
- **OR**: S[i] = A[i] | B[i] (1 se qualquer um for 1)
- **XOR**: S[i] = A[i] ^ B[i] (1 se diferentes)

Estas operações **nunca geram carry**.

### Operação de Soma

Realiza soma aritmética de inteiros de 32 bits:

```
S = A + B

Se INC = 1:
    S = A + B + 1
```

**Detecção de Carry:**
- Se resultado > 2³² - 1: vai_um = 1
- Caso contrário: vai_um = 0

O resultado é truncado a 32 bits (máximo 0xFFFFFFFF).

### Inversão (INVA)

Implementa o complemento a 2:
```
~A = NOT(A) = 0xFFFFFFFF - A

Exemplo com A = 5:
A em binário:        00000101
Invertido (~A):      11111010 (representa -6 em complemento a 2)
```

Esta operação é útil para subtração: A - B = A + (~B) + 1

---

## 📊 Exemplo Completo

### Programa

```
111100  (instrução 0)
110011  (instrução 1)
001111  (instrução 2)
```

### Execução Passo a Passo

**Instrução 0: 111100**
- F0=1, F1=1 (SOMA)
- ENA=1, ENB=0 (apenas A habilitado)
- INVA=0, INC=0
- A = 0 (valor inicial), B = 0
- **S = 0 + 0 = 0, vai_um = 0**
- A ← 0 (para próxima instrução)

**Instrução 1: 110011**
- F0=1, F1=0 (XOR)
- ENA=1, ENB=1 (ambos habilitados)
- INVA=1, INC=1
- A = 0, B = 0
- ~A = 0xFFFFFFFF (tudo invertido)
- **S = ~A XOR B = 0xFFFFFFFF, vai_um = 0**
- A ← 0xFFFFFFFF

**Instrução 2: 001111**
- F0=0, F1=1 (OR)
- ENA=0, ENB=1 (apenas B habilitado)
- INVA=1, INC=1
- A = 0xFFFFFFFF, B = 0xFFFFFFFF
- A_efetivo = 0 (desabilitado)
- **S = 0 OR 0xFFFFFFFF = 0xFFFFFFFF, vai_um = 0**

### Saída

```
PC  IR (bin)  A           B           S           Vai-um
0   111100    0           0           0           0
1   110011    0xFFFFFFFF  0           0xFFFFFFFF  0
2   001111    0xFFFFFFFF  0xFFFFFFFF  0xFFFFFFFF  0
```

---

## 📝 Estrutura de Arquivos

```
ArqII/
├── etapa1.py                 # Código principal
├── README.md                 # Este arquivo
├── programa_etapa1.txt       # Entrada: instruções (criado automaticamente)
└── saida_etapa1.txt         # Saída: log de execução
```

---

## 🎯 Próximas Etapas

Esta Etapa 1 é a base para:

- **Etapa 2**: Adiciona deslocadores (SLL8 para shift left, SRA1 para shift right aritmético) e registradores completos (H, OPC, TOS, CPP, LV, SP, PC, MDR, MAR)

- **Etapa 3**: Integra memória de dados e memória de instruções, implementando leitura/escrita (READ/WRITE)

- **Entregável**: Implementação das instruções IJVM (ILOAD, DUP, BIPUSH) que usam sequências de microinstruções

---

## 📚 Referências

- **Projeto**: Segunda Avaliação - Arquitetura de Computadores II
- **Instituição**: UFPB - Centro de Informática - DSC
- **Professora**: Sarah Pontes Madruga
- **Data**: 08 de Junho de 2026
- **Documento**: Projeto_26.1.pdf

---

## 🔬 Testes e Validação

Para validar a implementação:

1. **Teste AND**: `000000` deve produzir S=0
2. **Teste SOMA**: `111100` com A=1, B=1 deve produzir S=2, vai_um=0
3. **Teste SOMA com INC**: `111101` com A=1, B=1 deve produzir S=3, vai_um=0
4. **Teste com INVA**: `110000` com A=5 deve fazer A_efetivo = ~5

---

## 💡 Notas Importantes

- ✅ Todos os valores são 32 bits (compatível com Etapas posteriores)
- ✅ Carry é calculado apenas para soma
- ✅ Operações lógicas (AND, OR, XOR) não geram carry
- ✅ A é atualizado com S para simular um registrador simples
- ✅ Complemento a 2 é usado para negativos
- ✅ Log é formatado para fácil leitura e análise

---

**Implementação da Etapa 1 - APS da Segunda Avaliação de Arquitetura de Computadores II**
