class ULA:
    def executar(self, F0, F1, ENA, ENB, INVA, INC, A, B):
        if INVA == 1:
            return 0, 1

        a_val = A & 0xFFFFFFFF if ENA == 1 else 0
        b_val = B & 0xFFFFFFFF if ENB == 1 else 0

        operacao = (F0 << 1) | F1

        if operacao == 0:
            resultado = a_val & b_val
        elif operacao == 1:
            resultado = a_val | b_val
        elif operacao == 2:
            resultado = (~b_val) & 0xFFFFFFFF
        else:
            resultado = a_val + b_val + INC

        S = resultado & 0xFFFFFFFF
        vai_um = 1 if resultado > 0xFFFFFFFF else 0

        return S, vai_um


class Simulador:
    def __init__(self):
        self.ula = ULA()

    def extrair_bits(self, instrucao_str):
        if len(instrucao_str) != 6:
            raise ValueError(f"Instrução deve ter 6 bits, recebeu: {instrucao_str}")
        return (int(instrucao_str[0]), int(instrucao_str[1]), int(instrucao_str[2]),
                int(instrucao_str[3]), int(instrucao_str[4]), int(instrucao_str[5]))

    def carregar_registradores(self, arquivo):
        with open(arquivo, 'r') as f:
            linhas = [linha.strip() for linha in f.readlines() if linha.strip()]
        registradores = []
        for i in range(0, len(linhas), 2):
            a = int(linhas[i], 2) if i < len(linhas) else 0
            b = int(linhas[i + 1], 2) if i + 1 < len(linhas) else 0
            registradores.append((a, b))
        return registradores

    def carregar_instrucoes(self, arquivo):
        with open(arquivo, 'r') as f:
            linhas = [linha.strip() for linha in f.readlines() if linha.strip()]
        return linhas

    def executar(self, arquivo_registradores, arquivo_instrucoes, arquivo_saida):
        registradores = self.carregar_registradores(arquivo_registradores)
        instrucoes = self.carregar_instrucoes(arquivo_instrucoes)

        saida = []
        saida.append("Start of Program")
        saida.append("=" * 60)

        for pc, ir_bin in enumerate(instrucoes, 1):
            a, b = registradores[pc - 1] if pc - 1 < len(registradores) else (0, 0)

            saida.append(f"Cycle {pc}\n")
            saida.append(f"PC = {pc}")
            saida.append(f"IR = {ir_bin}")
            saida.append(f"b = {b:032b}")
            saida.append(f"a = {a:032b}")

            F0, F1, ENA, ENB, INVA, INC = self.extrair_bits(ir_bin)
            s, co = self.ula.executar(F0, F1, ENA, ENB, INVA, INC, a, b)

            saida.append(f"s = {s:032b}")
            saida.append(f"co = {co}")
            saida.append("=" * 60)

        saida.append(f"Cycle {len(instrucoes) + 1}\n")
        saida.append(f"PC = {len(instrucoes) + 1}")
        saida.append("> Line is empty, EOP.\n")

        with open(arquivo_saida, 'w') as f:
            f.write('\n'.join(saida))


def main():
    sim = Simulador()
    sim.executar('registradores_etapa1.txt', 'programa_etapa1.txt', 'saida_etapa1.txt')


if __name__ == '__main__':
    main()
