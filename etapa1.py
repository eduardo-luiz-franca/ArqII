import os


class ULA:
    """Unidade Lógica e Aritmética da Mic-1"""

    def executar(self, F0, F1, ENA, ENB, INVA, INC, A, B):
        """
        Executa uma operação da ULA.

        Args:
            F0, F1: Bits de seleção de operação
            ENA: Habilita entrada A (se 0, A=0)
            ENB: Habilita entrada B (se 0, B=0)
            INVA: Inverte A (complemento a 2) se 1
            INC: Força o carry-in a 1 (soma + 1) se 1
            A, B: Operandos de 32 bits

        Returns:
            (S, vai_um): Saída de 32 bits e bit de carry
        """
        # Aplicar inversão de A
        a_val = (~A) & 0xFFFFFFFF if INVA == 1 else A & 0xFFFFFFFF

        # Aplicar habilitação de A e B (desabilita = 0)
        a_val = a_val if ENA == 1 else 0
        b_val = B & 0xFFFFFFFF if ENB == 1 else 0

        # Selecionar operação baseado em F0 e F1
        operacao = (F0 << 1) | F1

        if operacao == 0:  # F0=0, F1=0: AND
            S = a_val & b_val
            vai_um = 0
        elif operacao == 1:  # F0=0, F1=1: OR
            S = a_val | b_val
            vai_um = 0
        elif operacao == 2:  # F0=1, F1=0: XOR
            S = (~b_val) & 0xFFFFFFFF
            vai_um = 0
        else:  # operacao == 3: F0=1, F1=1: Soma (full adder)
            # Implementar somador completo de 32 bits
            carry_in = 1 if INC == 1 else 0
            resultado = a_val + b_val + carry_in
            # Carry out é 1 se resultado ultrapassar 32 bits
            vai_um = 1 if resultado > 0xFFFFFFFF else 0
            S = resultado & 0xFFFFFFFF

        return S, vai_um


class Simulador:
    """Simulador da Mic-1 para a Etapa 1"""

    def __init__(self):
        self.ula = ULA()
        self.A = 0
        self.B = 0
        self.IR = 0  # Registrador de Instrução
        self.PC = 0  # Contador de Programa
        self.log = []

    def carregar_programa(self, arquivo):
        """Carrega instruções de um arquivo"""
        if not os.path.exists(arquivo):
            raise FileNotFoundError(f"Arquivo {arquivo} não encontrado!")

        with open(arquivo, 'r') as f:
            linhas = [linha.strip() for linha in f.readlines() if linha.strip()]

        return linhas

    def extrair_bits(self, instrucao_str):
        """
        Extrai os 6 bits de uma instrução.
        Formato: F0 F1 ENA ENB INVA INC
        """
        if len(instrucao_str) != 6:
            raise ValueError(f"Instrução deve ter 6 bits, recebeu: {instrucao_str}")

        F0 = int(instrucao_str[0])
        F1 = int(instrucao_str[1])
        ENA = int(instrucao_str[2])
        ENB = int(instrucao_str[3])
        INVA = int(instrucao_str[4])
        INC = int(instrucao_str[5])

        return F0, F1, ENA, ENB, INVA, INC

    def executar_programa(self, arquivo_entrada, arquivo_saida):
        """Executa um programa e gera log de execução"""
        print(f"Carregando programa de: {arquivo_entrada}")
        linhas = self.carregar_programa(arquivo_entrada)
        self.log = []

        print(f"Executando {len(linhas)} instrução(ões)...")

        for self.PC, linha in enumerate(linhas):
            self.IR = int(linha, 2)  # Converter de binário para decimal

            # Extrair bits de controle
            F0, F1, ENA, ENB, INVA, INC = self.extrair_bits(linha)

            # Executar instrução na ULA
            S, vai_um = self.ula.executar(F0, F1, ENA, ENB, INVA, INC, self.A, self.B)

            # Atualizar A com a saída S (simula registrador)
            self.A = S

            # Registrar no log
            self.log.append({
                'PC': self.PC,
                'IR': self.IR,
                'IR_bin': linha,
                'A': self.A,
                'B': self.B,
                'S': S,
                'vai_um': vai_um,
                'operacao': self._descrever_operacao(F0, F1, ENA, ENB, INVA, INC)
            })

        # Escrever log
        self._escrever_log(arquivo_saida)
        print(f"Execução concluída! Log salvo em: {arquivo_saida}")

    def _descrever_operacao(self, F0, F1, ENA, ENB, INVA, INC):
        """Descreve a operação para fins de debug"""
        ops = {
            0: "AND",
            1: "OR",
            2: "XOR",
            3: "SOMA"
        }
        operacao = (F0 << 1) | F1
        desc = ops[operacao]
        if INVA:
            desc += " (~A)"
        if INC and operacao == 3:
            desc += " +1"
        return desc

    def _escrever_log(self, arquivo_saida):
        """Escreve o log em arquivo com formatação clara"""
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            # Cabeçalho
            f.write("=" * 100 + "\n")
            f.write("SIMULAÇÃO DA ULA DA MIC-1 - ETAPA 1\n")
            f.write("=" * 100 + "\n\n")

            # Tabela de resultados
            f.write(f"{'PC':<5} {'IR (bin)':<10} {'IR (dec)':<10} {'A':<15} {'B':<15} {'S':<15} {'Vai-um':<10} {'Operação':<20}\n")
            f.write("-" * 100 + "\n")

            for entrada in self.log:
                f.write(f"{entrada['PC']:<5} {entrada['IR_bin']:<10} {entrada['IR']:<10} "
                       f"{entrada['A']:<15} {entrada['B']:<15} {entrada['S']:<15} "
                       f"{entrada['vai_um']:<10} {entrada['operacao']:<20}\n")

            f.write("-" * 100 + "\n\n")

            # Resumo final
            f.write("RESUMO DA EXECUÇÃO:\n")
            f.write(f"Total de instruções: {len(self.log)}\n")
            f.write(f"Valor final de A: {self.log[-1]['A'] if self.log else 0}\n")
            f.write(f"Última saída (S): {self.log[-1]['S'] if self.log else 0}\n")


def criar_programa_exemplo():
    """Cria um arquivo de programa exemplo para testes"""
    exemplo = """111100
101010
110011
000000
011111"""

    with open('programa_etapa1.txt', 'w') as f:
        f.write(exemplo)

    print("Arquivo 'programa_etapa1.txt' criado com instruções de exemplo.")
    print("\nInstruções de exemplo:")
    print("111100 - Soma com ambos operandos habilitados")
    print("101010 - XOR com habilitação invertida")
    print("110011 - Soma com A invertido")
    print("000000 - AND sem operandos")
    print("011111 - OR com INC")


def main():
    import sys

    print("=" * 60)
    print("SIMULADOR DA ULA DA MIC-1 - ETAPA 1")
    print("=" * 60 + "\n")

    # Se não existir arquivo de programa, criar exemplo
    if not os.path.exists('programa_etapa1.txt'):
        print("Arquivo 'programa_etapa1.txt' não encontrado!")
        print("Criando arquivo de exemplo...\n")
        criar_programa_exemplo()
        print("\nEdite o arquivo 'programa_etapa1.txt' com suas instruções.")
        print("Cada linha deve conter 6 bits: F0 F1 ENA ENB INVA INC")
        return

    # Executar simulador
    simulador = Simulador()
    try:
        simulador.executar_programa('programa_etapa1.txt', 'saida_etapa1.txt')
    except Exception as e:
        print(f"Erro durante execução: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
