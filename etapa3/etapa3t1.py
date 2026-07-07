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
        self.memoria = []

    def carregar_arquivos(self, arq_reg, arq_inst, arq_dados):
        pasta_script = os.path.dirname(os.path.abspath(__file__))

        caminho_reg = os.path.join(pasta_script, arq_reg)
        caminho_inst = os.path.join(pasta_script, arq_inst)
        caminho_dados = os.path.join(pasta_script, arq_dados)

        # 1. Carrega os Registradores tratando textos como "mar = 0000..."
        if os.path.exists(caminho_reg):
            with open(caminho_reg, 'r', encoding='utf-8') as f:
                linhas = [l.strip() for l in f.readlines() if l.strip()]

            for linha in linhas:
                # Se a linha contiver '=', separa o nome do valor binário
                if '=' in linha:
                    partes = linha.split('=')
                    nome_reg = partes[0].strip().lower()
                    val_bin = partes[1].strip()
                    if nome_reg in self.regs:
                        self.regs[nome_reg] = int(val_bin, 2)
                else:
                    # Caso o arquivo estivesse apenas com binários puros ordenados
                    chaves_ordem = ['mar', 'mdr', 'pc', 'mbr', 'sp', 'lv', 'cpp', 'tos', 'opc', 'h']
                    for i, linha_pura in enumerate(linhas):
                        if i < len(chaves_ordem) and not '=' in linha_pura:
                            self.regs[chaves_ordem[i]] = int(linha_pura, 2)
                    break
        else:
            print(f"Erro crítico: Arquivo {arq_reg} não encontrado!")

        # 2. Carrega as Microinstruções
        with open(caminho_inst, 'r', encoding='utf-8') as f:
            instrucoes = [l.strip() for l in f.readlines() if l.strip()]

        # 3. Carrega a Memória de Dados
        if os.path.exists(caminho_dados):
            with open(caminho_dados, 'r', encoding='utf-8') as f:
                self.memoria = [l.strip() for l in f.readlines() if l.strip()]
        else:
            self.memoria = ["0" * 32 for _ in range(16)]

        return instrucoes

    def formatar_registradores(self):
        linhas = []
        for reg, val in self.regs.items():
            if reg == 'mbr':
                linhas.append(f"{reg} = {val:08b}")
            else:
                linhas.append(f"{reg} = {val:032b}")
        return '\n'.join(linhas)

    def formatar_memoria(self):
        return '\n'.join(self.memoria)

    def decodificar_barramento_b(self, bits_b):
        num = int(bits_b, 2)
        # Decodificador de 4 bits -> 9 registradores possíveis (0..8)
        mapping = {
            0: 'mdr', 1: 'pc', 2: 'mbr', 3: 'mbru',
            4: 'sp', 5: 'lv', 6: 'cpp', 7: 'tos', 8: 'opc'
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
        else:
            return 'none', 0

    def decodificar_barramento_c(self, bits_c):
        # bit 8 = H ... bit 0 = MAR (esquerda -> direita na palavra de 9 bits)
        mapping = ['mar', 'mdr', 'pc', 'sp', 'lv', 'cpp', 'tos', 'opc', 'h']
        dests = []
        for i, bit in enumerate(bits_c):
            if bit == '1':
                dests.append(mapping[8 - i])
        return dests

    def executar(self, arq_regs, arq_inst, arq_dados, arq_saida):
        instrucoes = self.carregar_arquivos(arq_regs, arq_inst, arq_dados)
        saida = []

        # Estado Inicial
        saida.append("=" * 60)
        saida.append("Initial memory state")
        saida.append("*" * 31)
        for mem_linha in self.memoria:
            saida.append(mem_linha)
        saida.append("*" * 31)
        saida.append("Initial register state")
        saida.append("*" * 31)
        saida.append(self.formatar_registradores())
        saida.append("")

        for i, ir_bin in enumerate(instrucoes):
            ciclo = i + 1

            # Fatiamento correto para microinstrução de 23 bits, na ordem
            # definida no enunciado: ULA(8) | Barramento C(9) | Memoria(2) | Barramento B(4)
            alu_ctrl = ir_bin[0:8]
            c_ctrl   = ir_bin[8:17]
            mem_ctrl = ir_bin[17:19]   # WRITE, READ (nessa ordem)
            b_ctrl   = ir_bin[19:23]

            write_flag = mem_ctrl[0]
            read_flag = mem_ctrl[1]
            # Caso especial (usado no Entregável): WRITE e READ altos ao mesmo
            # tempo indica um "fetch puro" (carga direta de MBR em H).
            fetch_especial = (write_flag == '1' and read_flag == '1')

            saida.append(f"Cycle {ciclo}")
            saida.append(f"ir = {alu_ctrl} {c_ctrl} {mem_ctrl} {b_ctrl}")
            saida.append(f"write = {write_flag}")
            saida.append(f"read = {read_flag}")
            if fetch_especial:
                saida.append("fetch_especial = 1")

            nome_b, val_b = self.decodificar_barramento_b(b_ctrl)
            dests_c = self.decodificar_barramento_c(c_ctrl)

            saida.append(f"b_bus = {nome_b}")
            saida.append(f"c_bus = {', '.join(dests_c) if dests_c else 'none'}")
            saida.append("")

            saida.append("> Registers before instruction")
            saida.append("*" * 31)
            saida.append(self.formatar_registradores())
            saida.append("")

            if fetch_especial:
                # Caso especial: os 8 bits de controle da ULA carregam o
                # argumento a ser colocado em MBR, e H = MBR (zero-extended),
                # sem passar pela ULA.
                self.regs['mbr'] = int(alu_ctrl, 2)
                self.regs['h'] = self.regs['mbr'] & 0xFF
            else:
                # Sinais de controle da ULA
                SLL8, SRA1, F0, F1, ENA, ENB, INVA, INC = (int(bit) for bit in alu_ctrl)

                h_val = self.regs['h']
                if INVA == 1:
                    h_val = (~h_val) & 0xFFFFFFFF

                a_val = h_val if ENA == 1 else 0
                b_val = val_b if ENB == 1 else 0

                # Processamento
                s, co = self.ula.executar(F0, F1, INC, a_val, b_val)
                sd = aplicar_deslocador(s, SLL8, SRA1)

                # Barramento C: a saída deslocada Sd sobrescreve os
                # registradores habilitados, ANTES de qualquer acesso à memória.
                for dest in dests_c:
                    if dest == 'mbr':
                        self.regs['mbr'] = sd & 0xFF
                    else:
                        self.regs[dest] = sd & 0xFFFFFFFF

                # Operações de memória ocorrem só depois da escrita no
                # barramento C, e usam os valores já atualizados de MAR/MDR.
                if read_flag == '1':
                    mar_val = self.regs['mar']
                    if 0 <= mar_val < len(self.memoria):
                        self.regs['mdr'] = int(self.memoria[mar_val], 2)

                if write_flag == '1':
                    mar_val = self.regs['mar']
                    if 0 <= mar_val < len(self.memoria):
                        mdr_val = self.regs['mdr']
                        self.memoria[mar_val] = f"{mdr_val:032b}"

            saida.append("> Registers after instruction")
            saida.append("*" * 31)
            saida.append(self.formatar_registradores())
            saida.append("")

            # Requisito do enunciado: valores da memória de dados após a
            # execução de cada microinstrução.
            saida.append("> Memory after instruction")
            saida.append("*" * 31)
            saida.append(self.formatar_memoria())
            saida.append("")

        # Gravação final estável
        pasta_script = os.path.dirname(os.path.abspath(__file__))
        caminho_saida = os.path.join(pasta_script, arq_saida)

        with open(caminho_saida, 'w', encoding='utf-8') as f:
            f.write('\n'.join(saida))

def main():
    simulador = Simulador()
    simulador.executar(
        'registradores.txt',
        'microinstruções_etapa3_tarefa1.txt',
        'dados_etapa3_tarefa1.txt',
        'saída_etapa3_tarefa1.txt'
    )
    print("Simulação concluída com sucesso! Verifique o arquivo 'saída_etapa3_tarefa1.txt'.")

if __name__ == "__main__":
    main()