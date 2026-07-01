class ULA:
    def executar(self, F0, F1, INVA, INC, a_val, b_val):
        if INVA == 1:
            return 0, 1

        if F0 == 0 and F1 == 0:
            resultado = a_val & b_val
        elif F0 == 0 and F1 == 1:
            resultado = a_val | b_val
        elif F0 == 1 and F1 == 0:
            resultado = (~b_val) & 0xFFFFFFFF
        else:
            resultado = a_val + b_val + INC

        S = resultado & 0xFFFFFFFF

        if resultado > 0xFFFFFFFF:
            vai_um = 1
        else:
            vai_um = 0

        return S, vai_um


def aplicar_deslocador(S, SLL8, SRA1):
    if SLL8 == 1:
        Sd = (S << 8) & 0xFFFFFFFF
    elif SRA1 == 1:
        sinal = S & 0x80000000
        Sd = (S >> 1) | sinal
    else:
        Sd = S
    return Sd


class Simulador:
    def __init__(self):
        self.ula = ULA()

    def carregar_arquivos(self, arq_reg, arq_inst):
        with open(arq_reg, 'r') as f:
            linhas = [ln.strip() for ln in f if ln.strip()]
        a = int(linhas[0], 2)
        b = int(linhas[1], 2)

        with open(arq_inst, 'r') as f:
            instrucoes = [ln.strip() for ln in f if ln.strip()]

        return a, b, instrucoes

    def executar(self, arquivo_registradores, arquivo_instrucoes, arquivo_saida):
        a_orig, b_orig, instrucoes = self.carregar_arquivos(arquivo_registradores, arquivo_instrucoes)

        saida = []
        saida.append(f"b = {b_orig:032b}")
        saida.append(f"a = {a_orig:032b}\n")
        saida.append("Start of Program")
        saida.append("=" * 60)

        for i, ir_bin in enumerate(instrucoes):
            pc = i + 1

            SLL8, SRA1, F0, F1, ENA, ENB, INVA, INC = (int(bit) for bit in ir_bin)

            saida.append(f"Cycle {pc}\n")
            saida.append(f"PC = {pc}")
            saida.append(f"IR = {ir_bin}")

            if SLL8 == 1 and SRA1 == 1:
                saida.append("> Error, invalid control signals.")
                if pc < len(instrucoes):
                    saida.append("=" * 60)
                continue

            a_ciclo = a_orig if ENA == 1 else 0
            b_ciclo = b_orig if ENB == 1 else 0

            saida.append(f"b = {b_ciclo:032b}")
            saida.append(f"a = {a_ciclo:032b}")

            s, co = self.ula.executar(F0, F1, INVA, INC, a_ciclo, b_ciclo)

            sd = aplicar_deslocador(s, SLL8, SRA1)

            z = 1 if sd == 0 else 0
            n = 1 if (sd & 0x80000000) != 0 else 0

            saida.append(f"s = {s:032b}")
            saida.append(f"sd = {sd:032b}")
            saida.append(f"n = {n}")
            saida.append(f"z = {z}")
            saida.append(f"co = {co}")

            if pc < len(instrucoes):
                saida.append("=" * 60)

        ciclo_final = len(instrucoes) + 1
        saida.append("=" * 60)
        saida.append(f"Cycle {ciclo_final}\n")
        saida.append(f"PC = {ciclo_final}")
        saida.append("> Line is empty, EOP.")

        with open(arquivo_saida, 'w') as f:
            f.write('\n'.join(saida))


import os


def main():
    pasta_script = os.path.dirname(os.path.abspath(__file__))
    arq_registradores = os.path.join(pasta_script, 'registradores.txt')
    arq_instrucoes = os.path.join(pasta_script, 'instruções.txt')
    arq_saida = os.path.join(pasta_script, 'saida.txt')

    sim = Simulador()
    sim.executar(arq_registradores, arq_instrucoes, arq_saida)


if __name__ == '__main__':
    main()