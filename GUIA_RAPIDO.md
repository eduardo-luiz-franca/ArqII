# Guia Rápido - Simulador ULA Etapa 1

## Como Começar

### 1. Executar o Simulador
```bash
python etapa1.py
```

### 2. Editar Programa
Abra `programa_etapa1.txt` e adicione suas instruções (6 bits por linha):

```
111100
101010
110011
```

### 3. Visualizar Resultados
Abra `saida_etapa1.txt` para ver o log de execução formatado.

---

## Formato da Instrução (6 bits)

```
Posição:  0   1   2    3    4     5
          F0  F1  ENA  ENB  INVA  INC
```

### Seleção de Operação (F0, F1)
- `00` = AND
- `01` = OR
- `10` = XOR
- `11` = SOMA

### Exemplos

**Soma: 5 + 3**
```
111100
```
- F0=1, F1=1 (SOMA)
- ENA=1, ENB=1 (ambos habilitados)
- INVA=0 (A normal)
- INC=0 (sem incremento)

**AND desabilitado**
```
000001
```
- F0=0, F1=0 (AND)
- ENA=0 (A = 0)
- ENB=0 (B = 0)
- INVA=0, INC=1

---

## Saída Gerada

Arquivo `saida_etapa1.txt`:

| Campo | Significado |
|-------|-------------|
| PC | Número da instrução |
| IR (bin) | Instrução em binário |
| IR (dec) | Instrução em decimal |
| A | Operando A (entrada) |
| B | Operando B (entrada) |
| S | Resultado da operação |
| Vai-um | Bit de carry/overflow |
| Operação | Descrição legível |

---

## Testes

Execute o arquivo de testes para validar:

```bash
python teste_exemplo_pdf.py
```

Valida:
- Soma (1 + 1 = 2)
- AND, OR, XOR
- Habilitação seletiva de operandos
- Inversão de operandos

---

## Documentação Completa

Abra `README.md` para:
- Explicação detalhada da ULA
- Lógica interna
- Exemplos passo a passo
- Notas técnicas

---

## Estrutura de Arquivos

```
ArqII/
├── etapa1.py                 ← Código principal
├── README.md                 ← Documentação completa
├── GUIA_RAPIDO.md           ← Este arquivo
├── teste_exemplo_pdf.py      ← Testes unitários
├── programa_etapa1.txt       ← Entrada (edite aqui)
├── programa_teste_pdf.txt    ← Exemplo para teste
└── saida_etapa1.txt         ← Saída (gerado automaticamente)
```

---

## Dicas

✓ Cada instrução é **uma única linha** com **6 caracteres** (0 ou 1)
✓ O simulador **atualiza A com a saída S** após cada instrução
✓ O log é **formatado para fácil leitura**
✓ Todos os valores são **32 bits**

---

**Pronto para usar! Execute `python etapa1.py` para começar.**
