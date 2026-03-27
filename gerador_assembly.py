# Aluno: Gabriel Almeida Fontes - lightlord77
# Grupo: RA1 1
# Disciplina: Linguagens Formais e Automatos - PUCPR 2026-1
# Professor: Frank de Alcantara

import struct
from lexer import Token, TipoToken

HEX_SEGMENTS = {
    0: 0x3F, 1: 0x06, 2: 0x5B, 3: 0x4F, 4: 0x66,
    5: 0x6D, 6: 0x7D, 7: 0x07, 8: 0x7F, 9: 0x6F,
}
HEX_MINUS = 0x40


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
        self.num_linhas = 0
        self.cont_label = 0

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
            self._emit(f"    {instrucao:<40s} @ {comentario}")
        else:
            self._emit(f"    {instrucao}")

    def _gerar_secao_data(self, tokens_todas_linhas):
        for linha_tokens in tokens_todas_linhas:
            for token in linha_tokens:
                if token.tipo == TipoToken.NUMBER:
                    self._registrar_constante(token.valor)
                elif token.tipo == TipoToken.MEM_ID:
                    self.variaveis_mem.add(token.valor)

        self._registrar_constante("1.0")
        self._registrar_constante("0.0")

        self._emit("")
        self._emit("@ === SECAO DE DADOS ===")
        self._emit(".data")
        self._emit(".align 3")
        self._emit("")

        self._emit("@ Constantes IEEE 754 (64 bits)")
        for chave, (label, valor_float) in self.constantes.items():
            word_low, word_high = float_to_ieee754_words(valor_float)
            self._emit(f"{label}:")
            self._emit(f"    .word 0x{word_low:08X}        @ {chave} (low)")
            self._emit(f"    .word 0x{word_high:08X}        @ {chave} (high)")
            self._emit("")

        if self.variaveis_mem:
            self._emit("@ Variaveis MEM")
            for nome in sorted(self.variaveis_mem):
                self._emit(f"mem_{nome}:")
                self._emit(f"    .word 0x00000000")
                self._emit(f"    .word 0x00000000")
                self._emit("")

        self._emit("@ Resultados por linha")
        self._emit(f"resultados:")
        for i in range(self.num_linhas):
            self._emit(f"    .word 0x00000000")
            self._emit(f"    .word 0x00000000")
        self._emit("")

        self._emit("tabela_7seg:")
        for d in range(10):
            self._emit(f"    .byte 0x{HEX_SEGMENTS[d]:02X}")
        self._emit("")

        self._emit("str_linha:")
        self._emit('    .asciz "Linha "')
        self._emit("str_igual:")
        self._emit('    .asciz " = "')
        self._emit("str_newline:")
        self._emit('    .asciz "\\n"')
        self._emit("str_ponto:")
        self._emit('    .asciz "."')
        self._emit("str_menos:")
        self._emit('    .asciz "-"')
        self._emit("")

    def _gerar_preambulo(self):
        self._emit("@ === Compilador RPN -> Assembly ARMv7 ===")
        self._emit("@ PUCPR 2026-1 - Linguagens Formais e Automatos")
        self._emit("")
        self._emit(".text")
        self._emit(".global _start")
        self._emit("")
        self._emit("_start:")
        self._emit("")
        self._emit_comentario("Habilitar VFP")
        self._emit_instrucao("MRC p15, #0, r0, c1, c0, #2")
        self._emit_instrucao("ORR r0, r0, #0x300000", "CP10")
        self._emit_instrucao("ORR r0, r0, #0xC00000", "CP11")
        self._emit_instrucao("MCR p15, #0, r0, c1, c0, #2")
        self._emit_instrucao("MOV r0, #0x40000000")
        self._emit_instrucao("VMSR FPEXC, r0", "ativar VFP")
        self._emit("")
        self._emit_instrucao("LDR sp, =0x20000", "stack pointer")
        self._emit("")

    def _gerar_expressao(self, tokens, num_linha):
        self._emit("")
        self._emit(f"@ === LINHA {num_linha} ===")

        tipo_cmd = self._classificar_linha(tokens)

        if tipo_cmd == "MEM_STORE":
            self._gerar_mem_store(tokens, num_linha)
        elif tipo_cmd == "MEM_LOAD":
            self._gerar_mem_load(tokens, num_linha)
        elif tipo_cmd == "RES":
            self._gerar_res(tokens, num_linha)
        else:
            self._gerar_expressao_aritmetica(tokens, num_linha)

        self._emit_instrucao(f"LDR r0, =resultados")
        offset = (num_linha - 1) * 8
        if offset > 0:
            self._emit_instrucao(f"ADD r0, r0, #{offset}")
        self._emit_instrucao(f"VSTR d0, [r0]")
        self._emit("")

        self._emit_instrucao(f"MOV r0, #{num_linha}")
        self._emit_instrucao("BL exibir_resultado_uart")
        self._emit("")

    def _classificar_linha(self, tokens):
        internos = [t for t in tokens if t.tipo not in (TipoToken.LPAREN, TipoToken.RPAREN)]

        if len(internos) == 2 and internos[0].tipo == TipoToken.NUMBER \
                and internos[1].tipo == TipoToken.MEM_ID:
            return "MEM_STORE"
        if len(internos) == 1 and internos[0].tipo == TipoToken.MEM_ID:
            return "MEM_LOAD"
        if len(internos) == 2 and internos[0].tipo == TipoToken.NUMBER \
                and internos[1].tipo == TipoToken.KW_RES:
            return "RES"
        return "EXPR"

    def _gerar_mem_store(self, tokens, num_linha):
        internos = [t for t in tokens if t.tipo not in (TipoToken.LPAREN, TipoToken.RPAREN)]
        valor_str = internos[0].valor
        nome_mem = internos[1].valor
        label_const = self._registrar_constante(valor_str)

        self._emit_comentario(f"MEM_STORE: {nome_mem} = {valor_str}")
        self._emit_instrucao(f"LDR r0, ={label_const}")
        self._emit_instrucao(f"VLDR d0, [r0]")
        self._emit_instrucao(f"LDR r0, =mem_{nome_mem}")
        self._emit_instrucao(f"VSTR d0, [r0]")

    def _gerar_mem_load(self, tokens, num_linha):
        internos = [t for t in tokens if t.tipo not in (TipoToken.LPAREN, TipoToken.RPAREN)]
        nome_mem = internos[0].valor

        self._emit_comentario(f"MEM_LOAD: {nome_mem}")
        self._emit_instrucao(f"LDR r0, =mem_{nome_mem}")
        self._emit_instrucao(f"VLDR d0, [r0]")

    def _gerar_res(self, tokens, num_linha):
        internos = [t for t in tokens if t.tipo not in (TipoToken.LPAREN, TipoToken.RPAREN)]
        n = int(float(internos[0].valor))
        # (N RES) retorna resultado de N linhas anteriores
        # (0 RES) = linha anterior, (1 RES) = duas linhas atras, etc.
        indice = num_linha - 2 - n

        self._emit_comentario(f"RES: resultado de {n} linhas atras (linha {indice + 1})")
        self._emit_instrucao(f"LDR r0, =resultados")
        offset = indice * 8
        if offset > 0:
            self._emit_instrucao(f"ADD r0, r0, #{offset}")
        elif offset < 0:
            self._emit_instrucao(f"SUB r0, r0, #{-offset}")
        self._emit_instrucao(f"VLDR d0, [r0]")

    def _gerar_expressao_aritmetica(self, tokens, num_linha):
        self._emit_comentario("Avaliacao RPN com pilha VFP")
        profundidade_pilha = 0

        for token in tokens:
            if token.tipo in (TipoToken.LPAREN, TipoToken.RPAREN):
                continue

            elif token.tipo == TipoToken.NUMBER:
                label = self._registrar_constante(token.valor)
                self._emit_instrucao(f"LDR r0, ={label}")
                self._emit_instrucao(f"VLDR d0, [r0]", f"{token.valor}")
                self._emit_instrucao(f"VPUSH {{d0}}")
                profundidade_pilha += 1

            elif token.tipo == TipoToken.MEM_ID:
                self._emit_instrucao(f"LDR r0, =mem_{token.valor}")
                self._emit_instrucao(f"VLDR d0, [r0]", f"{token.valor}")
                self._emit_instrucao(f"VPUSH {{d0}}")
                profundidade_pilha += 1

            elif token.tipo == TipoToken.KW_RES:
                self._emit_instrucao(f"VPOP {{d0}}")
                profundidade_pilha -= 1
                self._emit_instrucao("VCVT.S32.F64 s0, d0")
                self._emit_instrucao("VMOV r1, s0")
                self._emit_instrucao(f"MOV r2, #{num_linha - 2}")
                self._emit_instrucao("SUB r2, r2, r1")
                self._emit_instrucao("LSL r2, r2, #3")
                self._emit_instrucao("LDR r0, =resultados")
                self._emit_instrucao("ADD r0, r0, r2")
                self._emit_instrucao("VLDR d0, [r0]")
                self._emit_instrucao("VPUSH {d0}")
                profundidade_pilha += 1

            elif token.tipo == TipoToken.OPERATOR:
                self._gerar_operacao(token.valor)
                profundidade_pilha -= 1

            elif token.tipo == TipoToken.INTDIV:
                self._gerar_divisao_inteira()
                profundidade_pilha -= 1

        if profundidade_pilha > 0:
            self._emit_instrucao("VPOP {d0}")

    def _gerar_operacao(self, operador):
        self._emit_instrucao("VPOP {d1}", "B")
        self._emit_instrucao("VPOP {d0}", "A")

        if operador == '+':
            self._emit_instrucao("VADD.F64 d0, d0, d1", "A + B")
        elif operador == '-':
            self._emit_instrucao("VSUB.F64 d0, d0, d1", "A - B")
        elif operador == '*':
            self._emit_instrucao("VMUL.F64 d0, d0, d1", "A * B")
        elif operador == '/':
            self._emit_instrucao("VDIV.F64 d0, d0, d1", "A / B")
        elif operador == '%':
            self._emit_instrucao("VDIV.F64 d2, d0, d1")
            self._emit_instrucao("VCVT.S32.F64 s4, d2")
            self._emit_instrucao("VCVT.F64.S32 d2, s4")
            self._emit_instrucao("VMUL.F64 d2, d2, d1")
            self._emit_instrucao("VSUB.F64 d0, d0, d2", "A % B")
        elif operador == '^':
            label_loop = self._nova_label("pot_loop")
            label_fim = self._nova_label("pot_fim")
            self._emit_instrucao("VCVT.S32.F64 s4, d1")
            self._emit_instrucao("VMOV r1, s4", "expoente inteiro")
            label_um = self._registrar_constante("1.0")
            self._emit_instrucao(f"LDR r0, ={label_um}")
            self._emit_instrucao("VLDR d2, [r0]", "acumulador = 1.0")
            self._emit_instrucao(f"CMP r1, #0")
            self._emit_instrucao(f"BLE {label_fim}")
            self._emit(f"{label_loop}:")
            self._emit_instrucao("VMUL.F64 d2, d2, d0", "acum *= base")
            self._emit_instrucao("SUBS r1, r1, #1")
            self._emit_instrucao(f"BGT {label_loop}")
            self._emit(f"{label_fim}:")
            self._emit_instrucao("VMOV.F64 d0, d2")

        self._emit_instrucao("VPUSH {d0}")

    def _gerar_divisao_inteira(self):
        self._emit_instrucao("VPOP {d1}", "B")
        self._emit_instrucao("VPOP {d0}", "A")
        self._emit_instrucao("VDIV.F64 d0, d0, d1", "A / B")
        self._emit_instrucao("VCVT.S32.F64 s0, d0", "truncar")
        self._emit_instrucao("VCVT.F64.S32 d0, s0")
        self._emit_instrucao("VPUSH {d0}")

    def _gerar_subrotinas_io(self):
        self._emit("")
        self._emit("@ === SUBROTINAS DE SAIDA ===")
        self._emit("")

        self._emit("exibir_resultado_uart:")
        self._emit_instrucao("PUSH {r4-r8, lr}")
        self._emit_instrucao("VPUSH {d0-d3}")
        self._emit_instrucao("MOV r4, r0")
        self._emit_instrucao("VMOV.F64 d3, d0")
        self._emit_instrucao("LDR r0, =str_linha")
        self._emit_instrucao("BL uart_print_string")
        self._emit_instrucao("MOV r0, r4")
        self._emit_instrucao("BL uart_print_int")
        self._emit_instrucao("LDR r0, =str_igual")
        self._emit_instrucao("BL uart_print_string")
        self._emit_instrucao("VMOV.F64 d0, d3")
        self._emit_instrucao("BL uart_print_double")
        self._emit_instrucao("LDR r0, =str_newline")
        self._emit_instrucao("BL uart_print_string")
        self._emit_instrucao("VMOV.F64 d0, d3")
        self._emit_instrucao("BL exibir_hex_displays")
        self._emit_instrucao("VPOP {d0-d3}")
        self._emit_instrucao("POP {r4-r8, pc}")
        self._emit("")

        self._emit("uart_print_char:")
        self._emit_instrucao("PUSH {r1-r2, lr}")
        self._emit_instrucao("LDR r1, =0xFF201000")
        label_wait = self._nova_label("uart_wait")
        self._emit(f"{label_wait}:")
        self._emit_instrucao("LDR r2, [r1, #4]")
        self._emit_instrucao("LSR r2, r2, #16")
        self._emit_instrucao("CMP r2, #0")
        self._emit_instrucao(f"BEQ {label_wait}")
        self._emit_instrucao("STR r0, [r1]")
        self._emit_instrucao("POP {r1-r2, pc}")
        self._emit("")

        self._emit("uart_print_string:")
        self._emit_instrucao("PUSH {r4, lr}")
        self._emit_instrucao("MOV r4, r0")
        label_loop = self._nova_label("str_loop")
        label_fim = self._nova_label("str_fim")
        self._emit(f"{label_loop}:")
        self._emit_instrucao("LDRB r0, [r4], #1")
        self._emit_instrucao("CMP r0, #0")
        self._emit_instrucao(f"BEQ {label_fim}")
        self._emit_instrucao("BL uart_print_char")
        self._emit_instrucao(f"B {label_loop}")
        self._emit(f"{label_fim}:")
        self._emit_instrucao("POP {r4, pc}")
        self._emit("")

        self._emit("uart_print_int:")
        self._emit_instrucao("PUSH {r4-r6, lr}")
        self._emit_instrucao("MOV r4, r0")
        self._emit_instrucao("MOV r5, #0")
        self._emit_instrucao("MOV r6, #100")
        self._emit_instrucao("BL _print_digito")
        self._emit_instrucao("MOV r6, #10")
        self._emit_instrucao("BL _print_digito")
        self._emit_instrucao("ADD r0, r4, #0x30")
        self._emit_instrucao("BL uart_print_char")
        self._emit_instrucao("POP {r4-r6, pc}")
        self._emit("")

        self._emit("_print_digito:")
        self._emit_instrucao("PUSH {lr}")
        self._emit_instrucao("MOV r0, #0")
        label_div = self._nova_label("div_loop")
        self._emit(f"{label_div}:")
        self._emit_instrucao("CMP r4, r6")
        label_div_fim = self._nova_label("div_fim")
        self._emit_instrucao(f"BLT {label_div_fim}")
        self._emit_instrucao("SUB r4, r4, r6")
        self._emit_instrucao("ADD r0, r0, #1")
        self._emit_instrucao(f"B {label_div}")
        self._emit(f"{label_div_fim}:")
        self._emit_instrucao("CMP r0, #0")
        label_skip = self._nova_label("skip_dig")
        self._emit_instrucao(f"BEQ {label_skip}")
        self._emit_instrucao("MOV r5, #1")
        self._emit_instrucao("ADD r0, r0, #0x30")
        self._emit_instrucao("BL uart_print_char")
        self._emit_instrucao(f"POP {{pc}}")
        self._emit(f"{label_skip}:")
        self._emit_instrucao("CMP r5, #0")
        label_skip2 = self._nova_label("skip_dig2")
        self._emit_instrucao(f"BEQ {label_skip2}")
        self._emit_instrucao("MOV r0, #0x30")
        self._emit_instrucao("BL uart_print_char")
        self._emit(f"{label_skip2}:")
        self._emit_instrucao("POP {pc}")
        self._emit("")

        self._emit("uart_print_double:")
        self._emit_instrucao("PUSH {r4-r6, lr}")
        self._emit_instrucao("VPUSH {d0-d2}")

        self._emit_instrucao("VMOV r4, r5, d0")
        self._emit_instrucao("TST r5, #0x80000000")
        label_pos = self._nova_label("pos")
        self._emit_instrucao(f"BEQ {label_pos}")
        self._emit_instrucao("LDR r0, =str_menos")
        self._emit_instrucao("BL uart_print_string")
        self._emit_instrucao("VNEG.F64 d0, d0")
        self._emit(f"{label_pos}:")

        self._emit_instrucao("VCVT.S32.F64 s0, d0")
        self._emit_instrucao("VMOV r0, s0")
        self._emit_instrucao("MOV r4, r0")
        self._emit_instrucao("BL uart_print_int")

        self._emit_instrucao("LDR r0, =str_ponto")
        self._emit_instrucao("BL uart_print_string")

        self._emit_instrucao("VCVT.F64.S32 d1, s0")
        self._emit_instrucao("VSUB.F64 d0, d0, d1")
        self._registrar_constante("10.0")
        label_dez = self._registrar_constante("10.0")
        self._emit_instrucao(f"LDR r0, ={label_dez}")
        self._emit_instrucao("VLDR d1, [r0]")
        self._emit_instrucao("VMUL.F64 d0, d0, d1")
        # Arredondar: somar 0.5 antes de truncar
        self._registrar_constante("0.5")
        label_meio = self._registrar_constante("0.5")
        self._emit_instrucao(f"LDR r0, ={label_meio}")
        self._emit_instrucao("VLDR d1, [r0]")
        self._emit_instrucao("VADD.F64 d0, d0, d1", "arredondar")
        self._emit_instrucao("VCVT.S32.F64 s0, d0")
        self._emit_instrucao("VMOV r0, s0")
        self._emit_instrucao("CMP r0, #0")
        label_abs = self._nova_label("abs_dec")
        self._emit_instrucao(f"BGE {label_abs}")
        self._emit_instrucao("RSB r0, r0, #0")
        self._emit(f"{label_abs}:")
        self._emit_instrucao("ADD r0, r0, #0x30")
        self._emit_instrucao("BL uart_print_char")

        self._emit_instrucao("VPOP {d0-d2}")
        self._emit_instrucao("POP {r4-r6, pc}")
        self._emit("")

        # Subrotina de divisao inteira por subtracao (r4/r1 -> r6=quociente, r0=resto)
        self._emit("_div_r4_r1:")
        self._emit_instrucao("PUSH {lr}")
        self._emit_instrucao("MOV r6, #0")
        label_dloop = self._nova_label("dloop")
        label_ddone = self._nova_label("ddone")
        self._emit(f"{label_dloop}:")
        self._emit_instrucao("CMP r4, r1")
        self._emit_instrucao(f"BLT {label_ddone}")
        self._emit_instrucao("SUB r4, r4, r1")
        self._emit_instrucao("ADD r6, r6, #1")
        self._emit_instrucao(f"B {label_dloop}")
        self._emit(f"{label_ddone}:")
        self._emit_instrucao("MOV r0, r4", "resto")
        self._emit_instrucao("MOV r4, r6", "quociente vira proximo dividendo")
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

        for i, nome in enumerate(["HEX0", "HEX1", "HEX2", "HEX3"]):
            self._emit_instrucao("BL _div_r4_r1", f"r4/10 -> r6=quot, r0=resto")
            self._emit_instrucao("LDRB r0, [r5, r0]")
            if i > 0:
                self._emit_instrucao(f"LSL r0, r0, #{i * 8}")
            self._emit_instrucao("ORR r7, r7, r0")

        self._emit_instrucao("LDR r0, =0xFF200020")
        self._emit_instrucao("STR r7, [r0]")
        self._emit_instrucao("POP {r4-r7, pc}")
        self._emit("")

    def _gerar_fim_programa(self):
        self._emit("")
        self._emit("@ === FIM ===")
        self._emit("fim:")
        self._emit_instrucao("B fim")
        self._emit("")

    def gerarAssembly(self, tokens_todas_linhas):
        self.num_linhas = len(tokens_todas_linhas)
        self.codigo = []
        self.constantes = {}
        self.cont_const = 0
        self.variaveis_mem = set()
        self.cont_label = 0

        texto_buffer = self.codigo
        self.codigo = []

        self._gerar_preambulo()

        for i, tokens_linha in enumerate(tokens_todas_linhas, 1):
            if tokens_linha:
                self._gerar_expressao(tokens_linha, i)

        self._gerar_fim_programa()
        self._gerar_subrotinas_io()

        codigo_text = self.codigo

        self.codigo = []
        self._gerar_secao_data(tokens_todas_linhas)
        codigo_data = self.codigo

        programa_final = codigo_data + [""] + codigo_text
        return "\n".join(programa_final)


def gerarAssembly(tokens_todas_linhas):
    gerador = GeradorAssembly()
    return gerador.gerarAssembly(tokens_todas_linhas)
