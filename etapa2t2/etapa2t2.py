import os

class ULA:
    def executar(self, F0, F1, INC, a_val, b_val):
        if F0 == 0 and F1 == 0:
            resultado = a_val & b_val
        elif F0 == 0 and F1 == 1:
            resultado = a_val | b_val
        elif F0 == 1 and F1 == 0:
            resultado = (~b_val) & 0xFFFFFFFF
        else:
            resultado = a_val + b_val + INC

        S = resultado & 0xFFFFFFFF
        vai_um = 1 if resultado > 0xFFFFFFFF else 0
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
        self.regs = {
            'mar': 0, 'mdr': 0, 'pc': 0, 'mbr': 0, 'sp': 0,
            'lv': 0, 'cpp': 0, 'tos': 0, 'opc': 0, 'h': 0
        }

    def carregar_arquivos(self, arq_reg, arq_inst):
        with open(arq_reg, 'r') as f:
            linhas = [ln.strip() for ln in f if ln.strip()]
        
        chaves = ['mar', 'mdr', 'pc', 'mbr', 'sp', 'lv', 'cpp', 'tos', 'opc', 'h']
        for i, chave in enumerate(chaves):
            if i < len(linhas):
                self.regs[chave] = int(linhas[i], 2)

        with open(arq_inst, 'r') as f:
            instrucoes = [ln.strip() for ln in f if ln.strip()]

        return instrucoes

    def formatar_registradores(self):
        saida = []
        for reg in ['mar', 'mdr', 'pc']:
            saida.append(f"{reg} = {self.regs[reg]:032b}")
        
        saida.append(f"mbr = {self.regs['mbr']:08b}")
        
        for reg in ['sp', 'lv', 'cpp', 'tos', 'opc', 'h']:
            saida.append(f"{reg} = {self.regs[reg]:032b}")
            
        return '\n'.join(saida)

    def decodificar_barramento_b(self, bits_b):
        num = int(bits_b, 2)
        mapping = {
            8: 'opc', 7: 'tos', 6: 'cpp', 5: 'lv', 4: 'sp',
            3: 'mbru', 2: 'mbr', 1: 'pc', 0: 'mdr'
        }
        reg_b = mapping.get(num, 'none')

        if reg_b == 'mbr':
            val = self.regs['mbr']
            if val & 0x80:
                val |= 0xFFFFFF00
            return 'mbr', val & 0xFFFFFFFF

        elif reg_b == 'mbru':
            val = self.regs['mbr']
            return 'mbru', val & 0xFFFFFFFF
            
        elif reg_b != 'none':
            return reg_b, self.regs[reg_b]
            
        return 'none', 0

    def decodificar_barramento_c(self, bits_c):
        mapping = ['mar', 'mdr', 'pc', 'sp', 'lv', 'cpp', 'tos', 'opc', 'h']
        dests = []
        for i, bit in enumerate(bits_c):
            if bit == '1':
                dests.append(mapping[8-i])
        return dests

    def executar(self, arq_regs, arq_instrucoes, arq_saida):
        instrucoes = self.carregar_arquivos(arq_regs, arq_instrucoes)
        saida = []

        for inst in instrucoes:
            saida.append(inst)
            
        saida.append("")
        saida.append("=" * 53)
        saida.append("> Initial register states")
        saida.append(self.formatar_registradores())
        saida.append("")
        saida.append("=" * 53)
        saida.append("Start of program")
        saida.append("=" * 53)

        for i, ir_bin in enumerate(instrucoes):
            pc = i + 1
            
            alu_ctrl = ir_bin[0:8]
            c_ctrl = ir_bin[8:17]
            b_ctrl = ir_bin[17:21]

            saida.append(f"Cycle {pc}")
            saida.append(f"ir = {alu_ctrl} {c_ctrl} {b_ctrl}\n")

            nome_b, val_b = self.decodificar_barramento_b(b_ctrl)
            dests_c = self.decodificar_barramento_c(c_ctrl)

            saida.append(f"b_bus = {nome_b}")
            saida.append(f"c_bus = {', '.join(dests_c) if dests_c else 'none'}\n")
            
            saida.append("> Registers before instruction")
            saida.append(self.formatar_registradores())
            saida.append("")

            SLL8, SRA1, F0, F1, ENA, ENB, INVA, INC = (int(bit) for bit in alu_ctrl)
            h_val = self.regs['h']
            if INVA == 1:
                h_val = (~h_val) & 0xFFFFFFFF
            a_val = h_val if ENA == 1 else 0
            b_val = val_b if ENB == 1 else 0

            s, co = self.ula.executar(F0, F1, INC, a_val, b_val)
            sd = aplicar_deslocador(s, SLL8, SRA1)

            for dest in dests_c:
                if dest == 'mbr':
                    self.regs['mbr'] = sd & 0xFF
                else:
                    self.regs[dest] = sd & 0xFFFFFFFF

            saida.append("> Registers after instruction")
            saida.append(self.formatar_registradores())
            saida.append("=" * 53)

        saida.append(f"Cycle {len(instrucoes) + 1}")
        saida.append("No more lines, EOP.")

        with open(arq_saida, 'w') as f:
            f.write('\n'.join(saida))

def main():
    pasta_script = os.path.dirname(os.path.abspath(__file__))
    arq_registradores = os.path.join(pasta_script, 'registradores.txt')
    arq_instrucoes = os.path.join(pasta_script, 'instruções.txt')
    arq_saida = os.path.join(pasta_script, 'saida.txt')

    sim = Simulador()
    sim.executar(arq_registradores, arq_instrucoes, arq_saida)

if __name__ == '__main__':
    main()