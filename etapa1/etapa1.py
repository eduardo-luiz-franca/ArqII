class ULA:
    def executar(self, F0, F1, INVA, INC, a_val, b_val):
        if INVA == 1:
            return 0, 1

        # Descobre a operação combinando F0 e F1
        if F0 == 0 and F1 == 0:
            resultado = a_val & b_val  # AND
        elif F0 == 0 and F1 == 1:
            resultado = a_val | b_val  # OR
        elif F0 == 1 and F1 == 0:
            resultado = (~b_val) & 0xFFFFFFFF  # NOT B
        else:
            resultado = a_val + b_val + INC  # SOMA

        # Aplica a máscara de 32 bits e calcula o carry out
        S = resultado & 0xFFFFFFFF
        
        if resultado > 0xFFFFFFFF:
            vai_um = 1
        else:
            vai_um = 0

        return S, vai_um


class Simulador:
    def __init__(self):
        self.ula = ULA()

    def carregar_arquivos(self, arq_reg, arq_inst):
        # Lê registradores
        with open(arq_reg, 'r') as f:
            linhas = [ln.strip() for ln in f if ln.strip()]
        a = int(linhas[0], 2)
        b = int(linhas[1], 2)

        # Lê instruções
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

            # Extrai os bits diretamente por indexação da string
            F0, F1, ENA, ENB, INVA, INC = (int(bit) for bit in ir_bin)
            
            # Aplica os sinais de controle de habilitação (ENA / ENB) uma única vez
            a_ciclo = a_orig if ENA == 1 else 0
            b_ciclo = b_orig if ENB == 1 else 0

            saida.append(f"Cycle {pc}\n")
            saida.append(f"PC = {pc}")
            saida.append(f"IR = {ir_bin}")
            saida.append(f"b = {b_ciclo:032b}")
            saida.append(f"a = {a_ciclo:032b}")

            # Passa os valores já validados para a ULA
            s, co = self.ula.executar(F0, F1, INVA, INC, a_ciclo, b_ciclo)

            saida.append(f"s = {s:032b}")
            saida.append(f"co = {co}")
            
            if pc < len(instrucoes):
                saida.append("=" * 60)

        # Ciclo de fim de programa (EOP)
        ciclo_final = len(instrucoes) + 1
        saida.append("=" * 60)
        saida.append(f"Cycle {ciclo_final}\n")
        saida.append(f"PC = {ciclo_final}")
        saida.append("> Line is empty, EOP.")

        with open(arquivo_saida, 'w') as f:
            f.write('\n'.join(saida))


def main():
    sim = Simulador()
    sim.executar('registradores.txt', 'instruções.txt', 'saida.txt')


if __name__ == '__main__':
    main()