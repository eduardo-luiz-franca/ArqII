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

def montar_palavra(ula, c, mem, b):
    return ula + c + mem + b

MICROINSTRUCOES = {
    'H = LV':              montar_palavra('00110100', '100000000', '00', '0101'),
    'H = H+1':             montar_palavra('00111001', '100000000', '00', '0000'),
    'MAR = H; rd':         montar_palavra('00111000', '000000001', '01', '0000'),
    'MAR = SP = SP+1; wr': montar_palavra('00110101', '000001001', '10', '0100'),
    'TOS = MDR':           montar_palavra('00110100', '001000000', '00', '0000'),
    'MAR = SP = SP+1':     montar_palavra('00110101', '000001001', '00', '0100'),
    'MDR = TOS; wr':       montar_palavra('00110100', '000000010', '10', '0111'),
    'SP = MAR = SP+1':     montar_palavra('00110101', '000001001', '00', '0100'),
    'MDR = TOS = H; wr':   montar_palavra('00111000', '001000010', '10', '0000'),
}

def traduzir_instrucao(linha):
    partes = linha.split()
    nome = partes[0].upper()

    if nome == 'ILOAD':
        x = int(partes[1])
        micro = [('H = LV', MICROINSTRUCOES['H = LV'])]
        for _ in range(x):
            micro.append(('H = H+1', MICROINSTRUCOES['H = H+1']))
        micro.append(('MAR = H; rd', MICROINSTRUCOES['MAR = H; rd']))
        micro.append(('MAR = SP = SP+1; wr', MICROINSTRUCOES['MAR = SP = SP+1; wr']))
        micro.append(('TOS = MDR', MICROINSTRUCOES['TOS = MDR']))
        return micro

    if nome == 'DUP':
        return [
            ('MAR = SP = SP+1', MICROINSTRUCOES['MAR = SP = SP+1']),
            ('MDR = TOS; wr', MICROINSTRUCOES['MDR = TOS; wr']),
        ]

    if nome == 'BIPUSH':
        arg = partes[1]
        if len(arg) == 8 and set(arg) <= {'0', '1'}:
            byte = arg
        else:
            byte = f"{int(arg) & 0xFF:08b}"
        return [
            ('SP = MAR = SP+1', MICROINSTRUCOES['SP = MAR = SP+1']),
            ('fetch', montar_palavra(byte, '000000000', '11', '0000')),
            ('MDR = TOS = H; wr', MICROINSTRUCOES['MDR = TOS = H; wr']),
        ]

    raise ValueError(f"Instrucao desconhecida: {linha}")

class Simulador:
    def __init__(self):
        self.ula = ULA()
        self.regs = {
            'mar': 0, 'mdr': 0, 'pc': 0, 'mbr': 0, 'sp': 0,
            'lv': 0, 'cpp': 0, 'tos': 0, 'opc': 0, 'h': 0
        }
        self.memoria = []

    def carregar_arquivos(self, arq_reg, arq_inst, arq_dados):
        with open(arq_reg, 'r', encoding='utf-8') as f:
            linhas = [l.strip() for l in f if l.strip()]

        if any('=' in l for l in linhas):
            for linha in linhas:
                partes = linha.split('=')
                nome_reg = partes[0].strip().lower()
                if nome_reg in self.regs:
                    self.regs[nome_reg] = int(partes[1].strip(), 2)
        else:
            chaves = ['mar', 'mdr', 'pc', 'mbr', 'sp', 'lv', 'cpp', 'tos', 'opc', 'h']
            for i, chave in enumerate(chaves):
                if i < len(linhas):
                    self.regs[chave] = int(linhas[i], 2)

        with open(arq_dados, 'r', encoding='utf-8') as f:
            self.memoria = [l.strip() for l in f if l.strip()]

        with open(arq_inst, 'r', encoding='utf-8') as f:
            instrucoes = [l.strip() for l in f if l.strip()]

        return instrucoes

    def formatar_registradores(self):
        saida = []
        for reg in ['mar', 'mdr', 'pc']:
            saida.append(f"{reg} = {self.regs[reg]:032b}")
        saida.append(f"mbr = {self.regs['mbr']:08b}")
        for reg in ['sp', 'lv', 'cpp', 'tos', 'opc', 'h']:
            saida.append(f"{reg} = {self.regs[reg]:032b}")
        return '\n'.join(saida)

    def formatar_memoria(self):
        return '\n'.join(f"{i}: {palavra}" for i, palavra in enumerate(self.memoria))

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

        if reg_b == 'mbru':
            return 'mbru', self.regs['mbr'] & 0xFFFFFFFF

        if reg_b != 'none':
            return reg_b, self.regs[reg_b]

        return 'none', 0

    def decodificar_barramento_c(self, bits_c):
        mapping = ['mar', 'mdr', 'pc', 'sp', 'lv', 'cpp', 'tos', 'opc', 'h']
        dests = []
        for i, bit in enumerate(bits_c):
            if bit == '1':
                dests.append(mapping[8 - i])
        return dests

    def executar_microinstrucao(self, palavra):
        alu_ctrl = palavra[0:8]
        c_ctrl = palavra[8:17]
        mem_ctrl = palavra[17:19]
        b_ctrl = palavra[19:23]

        write_flag = mem_ctrl[0] == '1'
        read_flag = mem_ctrl[1] == '1'
        fetch_especial = write_flag and read_flag

        if fetch_especial:
            self.regs['mbr'] = int(alu_ctrl, 2)
            self.regs['h'] = self.regs['mbr'] & 0xFF
            return 'none', ['mbr', 'h'], write_flag, read_flag

        nome_b, val_b = self.decodificar_barramento_b(b_ctrl)
        dests_c = self.decodificar_barramento_c(c_ctrl)

        SLL8, SRA1, F0, F1, ENA, ENB, INVA, INC = (int(bit) for bit in alu_ctrl)

        h_val = self.regs['h']
        if INVA == 1:
            h_val = (~h_val) & 0xFFFFFFFF
        a_val = h_val if ENA == 1 else 0
        b_val = val_b if ENB == 1 else 0

        s, co = self.ula.executar(F0, F1, INC, a_val, b_val)
        sd = aplicar_deslocador(s, SLL8, SRA1)

        for dest in dests_c:
            self.regs[dest] = sd & 0xFFFFFFFF

        if read_flag:
            mar_val = self.regs['mar']
            if 0 <= mar_val < len(self.memoria):
                self.regs['mdr'] = int(self.memoria[mar_val], 2)

        if write_flag:
            mar_val = self.regs['mar']
            if 0 <= mar_val < len(self.memoria):
                self.memoria[mar_val] = f"{self.regs['mdr']:032b}"

        return nome_b, dests_c, write_flag, read_flag

    def executar(self, arq_regs, arq_inst, arq_dados, arq_saida):
        instrucoes = self.carregar_arquivos(arq_regs, arq_inst, arq_dados)
        saida = []

        saida.append("=" * 53)
        saida.append("> Initial data memory")
        saida.append(self.formatar_memoria())
        saida.append("")
        saida.append("> Initial register states")
        saida.append(self.formatar_registradores())
        saida.append("")
        saida.append("=" * 53)
        saida.append("Start of program")
        saida.append("=" * 53)

        ciclo = 0
        for num, instrucao in enumerate(instrucoes, start=1):
            micro_seq = traduzir_instrucao(instrucao)

            saida.append(f"Instruction {num}: {instrucao}")
            saida.append("Microinstructions:")
            for nome, palavra in micro_seq:
                saida.append(f"  {nome:<22} {palavra}")
            saida.append("-" * 53)

            for nome, palavra in micro_seq:
                ciclo += 1

                saida.append(f"Cycle {ciclo}: {nome}")
                saida.append(f"ir = {palavra[0:8]} {palavra[8:17]} {palavra[17:19]} {palavra[19:23]}")

                saida.append("")
                saida.append("> Registers before microinstruction")
                saida.append(self.formatar_registradores())
                saida.append("")

                nome_b, dests_c, w, r = self.executar_microinstrucao(palavra)

                saida.append(f"b_bus = {nome_b}")
                saida.append(f"c_bus = {', '.join(dests_c) if dests_c else 'none'}")
                saida.append(f"write = {int(w)} | read = {int(r)}")
                saida.append("")

                saida.append("> Registers after microinstruction")
                saida.append(self.formatar_registradores())
                saida.append("-" * 53)

            saida.append("> Data memory after instruction")
            saida.append(self.formatar_memoria())
            saida.append("=" * 53)

        saida.append("End of program")

        with open(arq_saida, 'w', encoding='utf-8') as f:
            f.write('\n'.join(saida))

def main():
    pasta_script = os.path.dirname(os.path.abspath(__file__))
    arq_registradores = os.path.join(pasta_script, 'registradores.txt')
    arq_instrucoes = os.path.join(pasta_script, 'instruções.txt')
    arq_dados = os.path.join(pasta_script, 'dados.txt')
    arq_saida = os.path.join(pasta_script, 'saida.txt')

    sim = Simulador()
    sim.executar(arq_registradores, arq_instrucoes, arq_dados, arq_saida)
    print("Simulacao concluida. Verifique o arquivo saida.txt")

if __name__ == '__main__':
    main()
