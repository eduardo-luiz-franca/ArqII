# Simulador da ULA da Mic-1
O projeto é um simulador da ULA (Unidade Lógica e Aritmética) da arquitetura Mic-1, feito em Python como trabalho prático de **Arquitetura de Computadores II**.
A Mic-1 é uma máquina virtual didática descrita no livro do Tanenbaum, usada para ensinar como funciona o nível de microprogramação de um processador. A ULA é o componente que executa as operações matemáticas e lógicas(AND, OR, NOT, soma) e este simulador reproduz exatamente esse comportamento.
O funcionamento é simples: você fornece dois registradores de 32 bits (A e B) e uma sequência de instruções de 6 bits cada. A cada "ciclo de clock", o simulador lê uma instrução, decodifica os sinais de controle (F0, F1, ENA, ENB, INVA, INC) e calcula o resultado da ULA, gravando tudo num arquivo de saída.

## Integrantes
- Leandro Cipriano
- Luiz Eduardo dos Santos
- Rickison de Lima Paula
- Ryan Costa Sobreira

---

# Funcionamento dos Registradores e Entradas
Este simulador opera com valores de registradores estáticos fornecidos no arquivo de configuração inicial.

O arquivo `registradores.txt` deve conter exatamente **duas linhas**, cada uma com **32 bits binários**:

1. A primeira linha define o valor do registrador **A**.
2. A segunda linha define o valor do registrador **B**.

Após serem carregados no início da execução, esses valores permanecem inalterados durante toda a simulação. A cada ciclo de clock, a ULA reutiliza os mesmos valores de **A** e **B**, alterando apenas a instrução executada a partir do arquivo `instruções.txt`.

---

# Arquivo de Instruções
O arquivo `instruções.txt` representa a memória de programa do simulador.
Cada linha corresponde a uma instrução executada em um ciclo de clock.

## Regras
- Cada linha representa uma única instrução.
- Cada instrução deve conter **exatamente 6 bits binários**.
- Apenas os caracteres `0` e `1` são permitidos.
- Não devem existir espaços ou separadores.

A ordem dos bits deve seguir exatamente o padrão da Mic-1:

```text
F0 F1 ENA ENB INVA INC
```

---

# Sinais de Controle da ULA
Os seis bits controlam o comportamento da ULA.

## F0 e F1
Selecionam a operação executada.

| F0 | F1 | Operação |
|----|----|----------|
| 0  | 0  | AND (A AND B) |
| 0  | 1  | OR (A OR B) |
| 1  | 0  | NOT B |
| 1  | 1  | SOMA (A + B + INC) |

## ENA
Habilita a entrada A.
- `1` → utiliza o valor de A.
- `0` → força `A_eff = 0`.

## ENB
Habilita a entrada B.
- `1` → utiliza o valor de B.
- `0` → força `B_eff = 0`.

## INVA
Quando este bit é igual a `1`, a ULA ignora completamente a operação selecionada e força:
- `s = 0`
- `co = 1`

## INC
Bit de incremento.
É utilizado apenas na operação de soma, adicionando `1` ao resultado final.

---

# Execução
Execute o simulador utilizando:

```bash
python etapa1.py
```

Durante a execução, o programa:

1. Lê os registradores em `registradores.txt`;
2. Lê todas as instruções de `instruções.txt`;
3. Executa uma instrução por ciclo de clock;
4. Gera o arquivo `saida.txt`.

- Caso o arquivo de saída não exista, ele será criado automaticamente.
- Caso já exista, seu conteúdo será completamente sobrescrito.

---

# Exemplo do Arquivo de Registradores

`registradores.txt`
```text
11111111111111111111111111111111
00000000000000000000000000000001
```

---

# Exemplo do Arquivo de Instruções

`instruções.txt`
```text
111100
001100
011100
```

---

# Exemplo de Saída

`saida.txt`
```text
Start of Program
============================================================
Cycle 1
PC = 1
IR = 111100
b  = 00000000000000000000000000000001
a  = 11111111111111111111111111111111
s  = 00000000000000000000000000000000
co = 1
============================================================
Cycle 2
PC = 2
IR = 001100
...
```

Cada ciclo apresenta:

- **PC** (Program Counter)
- **IR** (Instruction Register)
- Valor do registrador **A**
- Valor do registrador **B**
- Saída da ULA (**s**)
- **Carry Out** (co)

Todos os valores são exibidos em binário utilizando representação em **complemento de dois de 32 bits**.
