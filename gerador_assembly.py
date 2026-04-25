# Aluno: Gabriel Almeida Fontes - lightlord77
# Grupo: RA1 1
# Disciplina: Linguagens Formais e Autômatos - PUCPR 2026-1
# Professor: Frank de Alcantara

import struct
from lexer import TipoToken

HEX_SEGMENTS = {
    0: 0x3F, 1: 0x06, 2: 0x5B, 3: 0x4F, 4: 0x66,
    5: 0x6D, 6: 0x7D, 7: 0x07, 8: 0x7F, 9: 0x6F,
}


def float_to_ieee754_words(valor):
    packed = struct.pack('<d', valor)
    word_low = struct.unpack('<I', packed[0:4])[0]
    word_high = struct.unpack('<I', packed[4:8])[0]
    return (word_low, word_high)


class GeradorAssembly:

    def __init__(self):
        self.codigo = []
        self.constantes = {}
        self.cont_const = 0
        self.variaveis_mem = set()
        self.cont_label = 0
        self.num_linha_exec = 0
        self.total_linhas = 0

    def _nova_label(self, prefixo="L"):
        self.cont_label += 1
        return f"{prefixo}_{self.cont_label}"

    def _registrar_constante(self, valor_str):
        valor_float = float(valor_str)
        chave = valor_str
        if chave not in self.constantes:
            self.cont_const += 1
            label = f"const_{self.cont_const}"
            self.constantes[chave] = (label, valor_float)
        return self.constantes[chave][0]

    def _emit(self, linha):
        self.codigo.append(linha)

    def _emit_comentario(self, texto):
        self._emit(f"    @ {texto}")

    def _emit_instrucao(self, instrucao, comentario=""):
        if comentario:
            padding = max(1, 45 - len(instrucao) - 4)
            self._emit(f"    {instrucao}{' ' * padding}@ {comentario}")
        else:
            self._emit(f"    {instrucao}")

    def _contar_linhas_exec(self, no):
        count = 0
        if no.tipo == "programa":
            for f in no.filhos:
                count += self._contar_linhas_exec(f)
        elif no.tipo in ("expr_bin", "expr_cmp", "mem_store", "mem_load", "res"):
            count = 1
        elif no.tipo in ("if", "if_else", "while", "bloco_then", "bloco_else", "bloco_do"):
            for f in no.filhos:
                count += self._contar_linhas_exec(f)
        return count

    def _coletar_dados(self, no):
        if no.tipo == "number":
            self._registrar_constante(no.valor)
        elif no.tipo == "mem_store":
            self.variaveis_mem.add(no.valor)
            for f in no.filhos:
                self._coletar_dados(f)
        elif no.tipo == "mem_load":
            self.variaveis_mem.add(no.valor)
        else:
            for f in no.filhos:
                self._coletar_dados(f)

    def _gerar_secao_data(self):
        self._emit("")
        self._emit("@ === SECAO DE DADOS ===")
        self._emit(".data")
        self._emit(".align 3")
        self._emit("")
        self._emit("@ Constantes IEEE 754 (64 bits)")
        for chave, (label, valor_float) in self.constantes.items():
            word_low, word_high = float_to_ieee754_words(valor_float)
            self._emit(f"{label}:")
            self._emit(f"    .word 0x{word_low:08X}        @ {valor_float} (low)")
            self._emit(f"    .word 0x{word_high:08X}        @ {valor_float} (high)")
            self._emit("")
        if self.variaveis_mem:
            self._emit("@ Variaveis de memoria")
            for nome in sorted(self.variaveis_mem):
                self._emit(f"mem_{nome}:")
                self._emit(f"    .word 0x00000000")
                self._emit(f"    .word 0x00000000")
                self._emit("")
        self._emit("@ Array de resultados")
        self._emit("resultados:")
        self._emit(f"    .space {self.total_linhas * 8}")
        self._emit("")
        self._emit("@ Tabela 7 segmentos")
        self._emit("tabela_7seg:")
        for dig, val in sorted(HEX_SEGMENTS.items()):
            self._emit(f"    .byte 0x{val:02X}")
        self._emit("")
        self._emit("@ Strings UART")
        self._emit('str_linha:   .asciz "Linha "')
        self._emit('str_igual:   .asciz " = "')
        self._emit('str_nl:      .asciz "\\n"')
        self._emit('str_ponto:   .asciz "."')
        self._emit('str_menos:   .asciz "-"')
        self._emit("")

    def _gerar_preambulo(self):
        self._emit("")
        self._emit("@ === SECAO DE CODIGO ===")
        self._emit(".text")
        self._emit(".global _start")
        self._emit("")
        self._emit("_start:")
        self._emit_comentario("Habilitar VFP")
        self._emit_instrucao("MRC p15, 0, r0, c1, c0, 2")
        self._emit_instrucao("ORR r0, r0, #0xF00000")
        self._emit_instrucao("MCR p15, 0, r0, c1, c0, 2")
        self._emit_instrucao("MOV r0, #0x40000000")
        self._emit_instrucao("VMSR FPEXC, r0")
        self._emit("")
        self._emit_instrucao("LDR sp, =0x20000", "stack pointer")

    def _gerar_no(self, no):
        if no.tipo == "programa":
            for f in no.filhos:
                self._gerar_no(f)
        elif no.tipo == "expr_bin":
            self._gerar_expr_bin(no)
        elif no.tipo == "expr_cmp":
            self._gerar_expr_cmp(no)
        elif no.tipo == "number":
            self._gerar_number_push(no)
        elif no.tipo == "mem_store":
            self._gerar_mem_store(no)
        elif no.tipo == "mem_load":
            self._gerar_mem_load(no)
        elif no.tipo == "res":
            self._gerar_res(no)
        elif no.tipo == "if":
            self._gerar_if(no)
        elif no.tipo == "if_else":
            self._gerar_if_else(no)
        elif no.tipo == "while":
            self._gerar_while(no)
        elif no.tipo in ("bloco_then", "bloco_else", "bloco_do"):
            for f in no.filhos:
                self._gerar_no(f)

    def _gerar_operando_push(self, no):
        if no.tipo == "number":
            self._gerar_number_push(no)
        elif no.tipo == "mem_load":
            label = f"mem_{no.valor}"
            self._emit_instrucao(f"LDR r0, ={label}")
            self._emit_instrucao(f"VLDR d0, [r0]", f"{no.valor}")
            self._emit_instrucao("VPUSH {d0}")
        elif no.tipo == "expr_bin":
            self._gerar_operando_push(no.filhos[0])
            self._gerar_operando_push(no.filhos[1])
            self._emit_instrucao("VPOP {d1}", "B")
            self._emit_instrucao("VPOP {d0}", "A")
            self._gerar_operacao(no.valor)
            self._emit_instrucao("VPUSH {d0}")
        elif no.tipo == "expr_cmp":
            self._gerar_cmp_push(no)
        elif no.tipo == "res":
            n = int(float(no.valor))
            indice = self.num_linha_exec - 1 - n
            self._emit_instrucao("LDR r0, =resultados")
            offset = indice * 8
            if offset > 0:
                self._emit_instrucao(f"ADD r0, r0, #{offset}")
            self._emit_instrucao("VLDR d0, [r0]")
            self._emit_instrucao("VPUSH {d0}")

    def _gerar_number_push(self, no):
        label = self._registrar_constante(no.valor)
        self._emit_instrucao(f"LDR r0, ={label}")
        self._emit_instrucao(f"VLDR d0, [r0]", f"{no.valor}")
        self._emit_instrucao("VPUSH {d0}")

    def _gerar_operacao(self, operador):
        if operador == '+':
            self._emit_instrucao("VADD.F64 d0, d0, d1", "A + B")
        elif operador == '-':
            self._emit_instrucao("VSUB.F64 d0, d0, d1", "A - B")
        elif operador == '*':
            self._emit_instrucao("VMUL.F64 d0, d0, d1", "A * B")
        elif operador == '|':
            self._emit_instrucao("VDIV.F64 d0, d0, d1", "A | B (div real)")
        elif operador == '/':
            self._emit_instrucao("VDIV.F64 d0, d0, d1", "A / B (div inteira)")
            self._emit_instrucao("VCVT.S32.F64 s0, d0", "truncar")
            self._emit_instrucao("VCVT.F64.S32 d0, s0")
        elif operador == '%':
            self._emit_instrucao("VMOV.F64 d2, d0", "copia A")
            self._emit_instrucao("VDIV.F64 d0, d0, d1")
            self._emit_instrucao("VCVT.S32.F64 s0, d0")
            self._emit_instrucao("VCVT.F64.S32 d0, s0")
            self._emit_instrucao("VMUL.F64 d0, d0, d1")
            self._emit_instrucao("VSUB.F64 d0, d2, d0", "resto")
        elif operador == '^':
            self._emit_instrucao("VCVT.S32.F64 s4, d1")
            self._emit_instrucao("VMOV r1, s4")
            label_um = self._registrar_constante("1.0")
            self._emit_instrucao(f"LDR r0, ={label_um}")
            self._emit_instrucao("VLDR d2, [r0]")
            lp = self._nova_label("pow")
            le = self._nova_label("pow_end")
            self._emit(f"{lp}:")
            self._emit_instrucao("CMP r1, #0")
            self._emit_instrucao(f"BLE {le}")
            self._emit_instrucao("VMUL.F64 d2, d2, d0")
            self._emit_instrucao("SUB r1, r1, #1")
            self._emit_instrucao(f"B {lp}")
            self._emit(f"{le}:")
            self._emit_instrucao("VMOV.F64 d0, d2")

    def _gerar_cmp_push(self, no):
        self._gerar_operando_push(no.filhos[0])
        self._gerar_operando_push(no.filhos[1])
        self._emit_instrucao("VPOP {d1}", "B")
        self._emit_instrucao("VPOP {d0}", "A")
        self._emit_instrucao("VCMP.F64 d0, d1")
        self._emit_instrucao("VMRS APSR_nzcv, FPSCR")
        lt = self._nova_label("ct")
        le = self._nova_label("ce")
        cond_map = {"==": "EQ", "!=": "NE", ">": "GT", "<": "LT", ">=": "GE", "<=": "LE"}
        self._emit_instrucao(f"B{cond_map[no.valor]} {lt}")
        lz = self._registrar_constante("0.0")
        self._emit_instrucao(f"LDR r0, ={lz}")
        self._emit_instrucao("VLDR d0, [r0]")
        self._emit_instrucao(f"B {le}")
        self._emit(f"{lt}:")
        lu = self._registrar_constante("1.0")
        self._emit_instrucao(f"LDR r0, ={lu}")
        self._emit_instrucao("VLDR d0, [r0]")
        self._emit(f"{le}:")
        self._emit_instrucao("VPUSH {d0}")

    def _gerar_expr_bin(self, no):
        self._emit("")
        self.num_linha_exec += 1
        num = self.num_linha_exec
        self._emit(f"@ === LINHA {num} ===")
        self._gerar_operando_push(no.filhos[0])
        self._gerar_operando_push(no.filhos[1])
        self._emit_instrucao("VPOP {d1}", "B")
        self._emit_instrucao("VPOP {d0}", "A")
        self._gerar_operacao(no.valor)
        self._salvar_e_exibir(num)

    def _gerar_expr_cmp(self, no):
        self._emit("")
        self.num_linha_exec += 1
        num = self.num_linha_exec
        self._emit(f"@ === LINHA {num} ===")
        self._gerar_cmp_push(no)
        self._emit_instrucao("VPOP {d0}")
        self._salvar_e_exibir(num)

    def _gerar_mem_store(self, no):
        self._emit("")
        self.num_linha_exec += 1
        num = self.num_linha_exec
        self._emit(f"@ === LINHA {num} (MEM_STORE {no.valor}) ===")
        self._gerar_operando_push(no.filhos[0])
        self._emit_instrucao("VPOP {d0}")
        self._emit_instrucao(f"LDR r0, =mem_{no.valor}")
        self._emit_instrucao("VSTR d0, [r0]", f"salva em {no.valor}")
        self._salvar_e_exibir(num)

    def _gerar_mem_load(self, no):
        self._emit("")
        self.num_linha_exec += 1
        num = self.num_linha_exec
        self._emit(f"@ === LINHA {num} (MEM_LOAD {no.valor}) ===")
        self._emit_instrucao(f"LDR r0, =mem_{no.valor}")
        self._emit_instrucao(f"VLDR d0, [r0]", f"carrega {no.valor}")
        self._salvar_e_exibir(num)

    def _gerar_res(self, no):
        self._emit("")
        self.num_linha_exec += 1
        num = self.num_linha_exec
        n = int(float(no.valor))
        indice = num - 2 - n
        self._emit(f"@ === LINHA {num} (RES {n}) ===")
        self._emit_instrucao("LDR r0, =resultados")
        offset = indice * 8
        if offset > 0:
            self._emit_instrucao(f"ADD r0, r0, #{offset}")
        self._emit_instrucao("VLDR d0, [r0]")
        self._salvar_e_exibir(num)

    def _gerar_if(self, no):
        self._emit("")
        self._emit_comentario("=== IF ===")
        cond = no.filhos[0]
        bloco_then = no.filhos[1]
        lbl_endif = self._nova_label("endif")
        self._gerar_cmp_push(cond)
        self._emit_instrucao("VPOP {d0}")
        lz = self._registrar_constante("0.0")
        self._emit_instrucao(f"LDR r0, ={lz}")
        self._emit_instrucao("VLDR d1, [r0]")
        self._emit_instrucao("VCMP.F64 d0, d1")
        self._emit_instrucao("VMRS APSR_nzcv, FPSCR")
        self._emit_instrucao(f"BEQ {lbl_endif}", "se falso pula")
        for f in bloco_then.filhos:
            self._gerar_no(f)
        self._emit(f"{lbl_endif}:")

    def _gerar_if_else(self, no):
        self._emit("")
        self._emit_comentario("=== IF/ELSE ===")
        cond = no.filhos[0]
        bloco_then = no.filhos[1]
        bloco_else = no.filhos[2]
        lbl_else = self._nova_label("else")
        lbl_endif = self._nova_label("endif")
        self._gerar_cmp_push(cond)
        self._emit_instrucao("VPOP {d0}")
        lz = self._registrar_constante("0.0")
        self._emit_instrucao(f"LDR r0, ={lz}")
        self._emit_instrucao("VLDR d1, [r0]")
        self._emit_instrucao("VCMP.F64 d0, d1")
        self._emit_instrucao("VMRS APSR_nzcv, FPSCR")
        self._emit_instrucao(f"BEQ {lbl_else}", "se falso vai pro else")
        for f in bloco_then.filhos:
            self._gerar_no(f)
        self._emit_instrucao(f"B {lbl_endif}")
        self._emit(f"{lbl_else}:")
        for f in bloco_else.filhos:
            self._gerar_no(f)
        self._emit(f"{lbl_endif}:")

    def _gerar_while(self, no):
        self._emit("")
        self._emit_comentario("=== WHILE ===")
        cond = no.filhos[0]
        bloco = no.filhos[1]
        lbl_ini = self._nova_label("wstart")
        lbl_fim = self._nova_label("wend")
        self._emit(f"{lbl_ini}:")
        self._gerar_cmp_push(cond)
        self._emit_instrucao("VPOP {d0}")
        lz = self._registrar_constante("0.0")
        self._emit_instrucao(f"LDR r0, ={lz}")
        self._emit_instrucao("VLDR d1, [r0]")
        self._emit_instrucao("VCMP.F64 d0, d1")
        self._emit_instrucao("VMRS APSR_nzcv, FPSCR")
        self._emit_instrucao(f"BEQ {lbl_fim}", "se falso sai")
        for f in bloco.filhos:
            self._gerar_no(f)
        self._emit_instrucao(f"B {lbl_ini}")
        self._emit(f"{lbl_fim}:")

    def _salvar_e_exibir(self, num_linha):
        self._emit_instrucao("LDR r0, =resultados")
        offset = (num_linha - 1) * 8
        if offset > 0:
            self._emit_instrucao(f"ADD r0, r0, #{offset}")
        self._emit_instrucao("VSTR d0, [r0]")
        self._emit_instrucao(f"MOV r0, #{num_linha}")
        self._emit_instrucao("BL exibir_resultado_uart")

    def _gerar_fim_programa(self):
        self._emit("")
        self._emit("@ === FIM ===")
        self._emit("fim:")
        self._emit_instrucao("B fim")

    def _gerar_subrotinas_io(self):
        self._emit("")
        self._emit("@ === SUBROTINAS DE IO ===")
        self._emit("")
        self._emit("exibir_resultado_uart:")
        self._emit_instrucao("PUSH {r4, lr}")
        self._emit_instrucao("MOV r4, r0")
        self._emit_instrucao("VPUSH {d0}")
        self._emit_instrucao("LDR r0, =str_linha")
        self._emit_instrucao("BL uart_print_string")
        self._emit_instrucao("MOV r0, r4")
        self._emit_instrucao("BL uart_print_int")
        self._emit_instrucao("LDR r0, =str_igual")
        self._emit_instrucao("BL uart_print_string")
        self._emit_instrucao("VPOP {d0}")
        self._emit_instrucao("VPUSH {d0}")
        self._emit_instrucao("BL uart_print_double")
        self._emit_instrucao("LDR r0, =str_nl")
        self._emit_instrucao("BL uart_print_string")
        self._emit_instrucao("VPOP {d0}")
        self._emit_instrucao("BL exibir_hex_displays")
        self._emit_instrucao("POP {r4, pc}")
        self._emit("")
        self._emit("uart_print_char:")
        self._emit_instrucao("LDR r1, =0xFF201000")
        self._emit_instrucao("STR r0, [r1]")
        self._emit_instrucao("BX lr")
        self._emit("")
        self._emit("uart_print_string:")
        self._emit_instrucao("PUSH {r4, lr}")
        self._emit_instrucao("MOV r4, r0")
        lp = self._nova_label("pstr")
        le = self._nova_label("pstr_e")
        self._emit(f"{lp}:")
        self._emit_instrucao("LDRB r0, [r4]")
        self._emit_instrucao("CMP r0, #0")
        self._emit_instrucao(f"BEQ {le}")
        self._emit_instrucao("BL uart_print_char")
        self._emit_instrucao("ADD r4, r4, #1")
        self._emit_instrucao(f"B {lp}")
        self._emit(f"{le}:")
        self._emit_instrucao("POP {r4, pc}")
        self._emit("")
        self._emit("uart_print_int:")
        self._emit_instrucao("PUSH {r4-r6, lr}")
        self._emit_instrucao("MOV r4, r0")
        self._emit_instrucao("MOV r5, #0")
        self._emit_instrucao("MOV r1, #10")
        ld = self._nova_label("pid")
        lpr = self._nova_label("pip")
        self._emit(f"{ld}:")
        self._emit_instrucao("BL _div_r4_r1")
        self._emit_instrucao("ADD r0, r0, #0x30")
        self._emit_instrucao("PUSH {r0}")
        self._emit_instrucao("ADD r5, r5, #1")
        self._emit_instrucao("CMP r4, #0")
        self._emit_instrucao(f"BNE {ld}")
        self._emit(f"{lpr}:")
        self._emit_instrucao("POP {r0}")
        self._emit_instrucao("BL uart_print_char")
        self._emit_instrucao("SUB r5, r5, #1")
        self._emit_instrucao("CMP r5, #0")
        self._emit_instrucao(f"BNE {lpr}")
        self._emit_instrucao("POP {r4-r6, pc}")
        self._emit("")
        self._emit("uart_print_double:")
        self._emit_instrucao("PUSH {r4-r6, lr}")
        self._emit_instrucao("VPUSH {d0-d2}")
        self._emit_instrucao("VMOV r4, r5, d0")
        self._emit_instrucao("TST r5, #0x80000000")
        lpos = self._nova_label("pos")
        self._emit_instrucao(f"BEQ {lpos}")
        self._emit_instrucao("LDR r0, =str_menos")
        self._emit_instrucao("BL uart_print_string")
        self._emit_instrucao("VNEG.F64 d0, d0")
        self._emit(f"{lpos}:")
        self._emit_instrucao("VCVT.S32.F64 s0, d0")
        self._emit_instrucao("VMOV r0, s0")
        self._emit_instrucao("MOV r4, r0")
        self._emit_instrucao("BL uart_print_int")
        self._emit_instrucao("LDR r0, =str_ponto")
        self._emit_instrucao("BL uart_print_string")
        self._emit_instrucao("VCVT.F64.S32 d1, s0")
        self._emit_instrucao("VSUB.F64 d0, d0, d1")
        ldez = self._registrar_constante("10.0")
        self._emit_instrucao(f"LDR r0, ={ldez}")
        self._emit_instrucao("VLDR d1, [r0]")
        self._emit_instrucao("VMUL.F64 d0, d0, d1")
        lmeio = self._registrar_constante("0.5")
        self._emit_instrucao(f"LDR r0, ={lmeio}")
        self._emit_instrucao("VLDR d1, [r0]")
        self._emit_instrucao("VADD.F64 d0, d0, d1", "arredondar")
        self._emit_instrucao("VCVT.S32.F64 s0, d0")
        self._emit_instrucao("VMOV r0, s0")
        self._emit_instrucao("CMP r0, #0")
        labs = self._nova_label("absd")
        self._emit_instrucao(f"BGE {labs}")
        self._emit_instrucao("RSB r0, r0, #0")
        self._emit(f"{labs}:")
        self._emit_instrucao("ADD r0, r0, #0x30")
        self._emit_instrucao("BL uart_print_char")
        self._emit_instrucao("VPOP {d0-d2}")
        self._emit_instrucao("POP {r4-r6, pc}")
        self._emit("")
        self._emit("_div_r4_r1:")
        self._emit_instrucao("PUSH {lr}")
        self._emit_instrucao("MOV r6, #0")
        ldl = self._nova_label("dl")
        ldd = self._nova_label("dd")
        self._emit(f"{ldl}:")
        self._emit_instrucao("CMP r4, r1")
        self._emit_instrucao(f"BLT {ldd}")
        self._emit_instrucao("SUB r4, r4, r1")
        self._emit_instrucao("ADD r6, r6, #1")
        self._emit_instrucao(f"B {ldl}")
        self._emit(f"{ldd}:")
        self._emit_instrucao("MOV r0, r4", "resto")
        self._emit_instrucao("MOV r4, r6", "quociente")
        self._emit_instrucao("POP {pc}")
        self._emit("")
        self._emit("exibir_hex_displays:")
        self._emit_instrucao("PUSH {r4-r7, lr}")
        self._emit_instrucao("VABS.F64 d0, d0")
        self._emit_instrucao("VCVT.S32.F64 s0, d0")
        self._emit_instrucao("VMOV r4, s0")
        self._emit_instrucao("LDR r5, =tabela_7seg")
        self._emit_instrucao("MOV r7, #0")
        self._emit_instrucao("MOV r1, #10")
        for i in range(4):
            self._emit_instrucao("BL _div_r4_r1")
            self._emit_instrucao("LDRB r0, [r5, r0]")
            if i > 0:
                self._emit_instrucao(f"LSL r0, r0, #{i * 8}")
            self._emit_instrucao("ORR r7, r7, r0")
        self._emit_instrucao("LDR r0, =0xFF200020")
        self._emit_instrucao("STR r7, [r0]")
        self._emit_instrucao("POP {r4-r7, pc}")

    def gerarAssembly(self, arvore):
        self.codigo = []
        self.constantes = {}
        self.cont_const = 0
        self.variaveis_mem = set()
        self.cont_label = 0
        self.num_linha_exec = 0
        self._coletar_dados(arvore)
        self._registrar_constante("0.0")
        self._registrar_constante("1.0")
        self._registrar_constante("10.0")
        self._registrar_constante("0.5")
        self.total_linhas = self._contar_linhas_exec(arvore) + 30
        self._gerar_preambulo()
        self._gerar_no(arvore)
        self._gerar_fim_programa()
        self._gerar_subrotinas_io()
        codigo_text = self.codigo
        self.codigo = []
        self._gerar_secao_data()
        codigo_data = self.codigo
        return "\n".join(codigo_data + [""] + codigo_text)


def gerarAssembly(arvore):
    gerador = GeradorAssembly()
    return gerador.gerarAssembly(arvore)
