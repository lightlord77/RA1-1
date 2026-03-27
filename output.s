
@ === SECAO DE DADOS ===
.data
.align 3

@ Constantes IEEE 754 (64 bits)
const_1:
    .word 0x00000000        @ 1.0 (low)
    .word 0x3FF00000        @ 1.0 (high)

const_2:
    .word 0x9999999A        @ 99.9 (low)
    .word 0x4058F999        @ 99.9 (high)

const_3:
    .word 0x9999999A        @ 0.1 (low)
    .word 0x3FB99999        @ 0.1 (high)

const_4:
    .word 0x00000000        @ 0.5 (low)
    .word 0x3FE00000        @ 0.5 (high)

const_5:
    .word 0x00000000        @ 8.0 (low)
    .word 0x40200000        @ 8.0 (high)

const_6:
    .word 0x00000000        @ 7.0 (low)
    .word 0x401C0000        @ 7.0 (high)

const_7:
    .word 0x00000000        @ 3.0 (low)
    .word 0x40080000        @ 3.0 (high)

const_8:
    .word 0x00000000        @ 43 (low)
    .word 0x40458000        @ 43 (high)

const_9:
    .word 0x00000000        @ 5 (low)
    .word 0x40140000        @ 5 (high)

const_10:
    .word 0x00000000        @ 2.0 (low)
    .word 0x40000000        @ 2.0 (high)

const_11:
    .word 0x00000000        @ 8 (low)
    .word 0x40200000        @ 8 (high)

const_12:
    .word 0x51EB851F        @ 9.81 (low)
    .word 0x40239EB8        @ 9.81 (high)

const_13:
    .word 0x00000000        @ 72.0 (low)
    .word 0x40520000        @ 72.0 (high)

const_14:
    .word 0x00000000        @ 100.0 (low)
    .word 0x40590000        @ 100.0 (high)

const_15:
    .word 0x00000000        @ 10.0 (low)
    .word 0x40240000        @ 10.0 (high)

const_16:
    .word 0x00000000        @ 0 (low)
    .word 0x00000000        @ 0 (high)

const_17:
    .word 0x00000000        @ 0.0 (low)
    .word 0x00000000        @ 0.0 (high)

@ Variaveis MEM
mem_GRAVIDADE:
    .word 0x00000000
    .word 0x00000000

mem_MASSA:
    .word 0x00000000
    .word 0x00000000

@ Resultados por linha
resultados:
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000

tabela_7seg:
    .byte 0x3F
    .byte 0x06
    .byte 0x5B
    .byte 0x4F
    .byte 0x66
    .byte 0x6D
    .byte 0x7D
    .byte 0x07
    .byte 0x7F
    .byte 0x6F

str_linha:
    .asciz "Linha "
str_igual:
    .asciz " = "
str_newline:
    .asciz "\n"
str_ponto:
    .asciz "."
str_menos:
    .asciz "-"


@ === Compilador RPN -> Assembly ARMv7 ===
@ PUCPR 2026-1 - Linguagens Formais e Automatos

.text
.global _start

_start:

    @ Habilitar VFP
    MRC p15, #0, r0, c1, c0, #2
    ORR r0, r0, #0x300000                    @ CP10
    ORR r0, r0, #0xC00000                    @ CP11
    MCR p15, #0, r0, c1, c0, #2
    MOV r0, #0x40000000
    VMSR FPEXC, r0                           @ ativar VFP

    LDR sp, =0x20000                         @ stack pointer


@ === LINHA 1 ===
    @ Avaliacao RPN com pilha VFP
    LDR r0, =const_1
    VLDR d0, [r0]                            @ 1.0
    VPUSH {d0}
    LDR r0, =const_1
    VLDR d0, [r0]                            @ 1.0
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VADD.F64 d0, d0, d1                      @ A + B
    VPUSH {d0}
    VPOP {d0}
    LDR r0, =resultados
    VSTR d0, [r0]

    MOV r0, #1
    BL exibir_resultado_uart


@ === LINHA 2 ===
    @ Avaliacao RPN com pilha VFP
    LDR r0, =const_2
    VLDR d0, [r0]                            @ 99.9
    VPUSH {d0}
    LDR r0, =const_3
    VLDR d0, [r0]                            @ 0.1
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VSUB.F64 d0, d0, d1                      @ A - B
    VPUSH {d0}
    VPOP {d0}
    LDR r0, =resultados
    ADD r0, r0, #8
    VSTR d0, [r0]

    MOV r0, #2
    BL exibir_resultado_uart


@ === LINHA 3 ===
    @ Avaliacao RPN com pilha VFP
    LDR r0, =const_4
    VLDR d0, [r0]                            @ 0.5
    VPUSH {d0}
    LDR r0, =const_5
    VLDR d0, [r0]                            @ 8.0
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VMUL.F64 d0, d0, d1                      @ A * B
    VPUSH {d0}
    VPOP {d0}
    LDR r0, =resultados
    ADD r0, r0, #16
    VSTR d0, [r0]

    MOV r0, #3
    BL exibir_resultado_uart


@ === LINHA 4 ===
    @ Avaliacao RPN com pilha VFP
    LDR r0, =const_6
    VLDR d0, [r0]                            @ 7.0
    VPUSH {d0}
    LDR r0, =const_7
    VLDR d0, [r0]                            @ 3.0
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VDIV.F64 d0, d0, d1                      @ A / B
    VPUSH {d0}
    VPOP {d0}
    LDR r0, =resultados
    ADD r0, r0, #24
    VSTR d0, [r0]

    MOV r0, #4
    BL exibir_resultado_uart


@ === LINHA 5 ===
    @ Avaliacao RPN com pilha VFP
    LDR r0, =const_8
    VLDR d0, [r0]                            @ 43
    VPUSH {d0}
    LDR r0, =const_9
    VLDR d0, [r0]                            @ 5
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VDIV.F64 d0, d0, d1                      @ A / B
    VCVT.S32.F64 s0, d0                      @ truncar
    VCVT.F64.S32 d0, s0
    VPUSH {d0}
    VPOP {d0}
    LDR r0, =resultados
    ADD r0, r0, #32
    VSTR d0, [r0]

    MOV r0, #5
    BL exibir_resultado_uart


@ === LINHA 6 ===
    @ Avaliacao RPN com pilha VFP
    LDR r0, =const_8
    VLDR d0, [r0]                            @ 43
    VPUSH {d0}
    LDR r0, =const_9
    VLDR d0, [r0]                            @ 5
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VDIV.F64 d2, d0, d1
    VCVT.S32.F64 s4, d2
    VCVT.F64.S32 d2, s4
    VMUL.F64 d2, d2, d1
    VSUB.F64 d0, d0, d2                      @ A % B
    VPUSH {d0}
    VPOP {d0}
    LDR r0, =resultados
    ADD r0, r0, #40
    VSTR d0, [r0]

    MOV r0, #6
    BL exibir_resultado_uart


@ === LINHA 7 ===
    @ Avaliacao RPN com pilha VFP
    LDR r0, =const_10
    VLDR d0, [r0]                            @ 2.0
    VPUSH {d0}
    LDR r0, =const_11
    VLDR d0, [r0]                            @ 8
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VCVT.S32.F64 s4, d1
    VMOV r1, s4                              @ expoente inteiro
    LDR r0, =const_1
    VLDR d2, [r0]                            @ acumulador = 1.0
    CMP r1, #0
    BLE pot_fim_2
pot_loop_1:
    VMUL.F64 d2, d2, d0                      @ acum *= base
    SUBS r1, r1, #1
    BGT pot_loop_1
pot_fim_2:
    VMOV.F64 d0, d2
    VPUSH {d0}
    VPOP {d0}
    LDR r0, =resultados
    ADD r0, r0, #48
    VSTR d0, [r0]

    MOV r0, #7
    BL exibir_resultado_uart


@ === LINHA 8 ===
    @ MEM_STORE: GRAVIDADE = 9.81
    LDR r0, =const_12
    VLDR d0, [r0]
    LDR r0, =mem_GRAVIDADE
    VSTR d0, [r0]
    LDR r0, =resultados
    ADD r0, r0, #56
    VSTR d0, [r0]

    MOV r0, #8
    BL exibir_resultado_uart


@ === LINHA 9 ===
    @ MEM_STORE: MASSA = 72.0
    LDR r0, =const_13
    VLDR d0, [r0]
    LDR r0, =mem_MASSA
    VSTR d0, [r0]
    LDR r0, =resultados
    ADD r0, r0, #64
    VSTR d0, [r0]

    MOV r0, #9
    BL exibir_resultado_uart


@ === LINHA 10 ===
    @ Avaliacao RPN com pilha VFP
    LDR r0, =mem_MASSA
    VLDR d0, [r0]                            @ MASSA
    VPUSH {d0}
    LDR r0, =mem_GRAVIDADE
    VLDR d0, [r0]                            @ GRAVIDADE
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VMUL.F64 d0, d0, d1                      @ A * B
    VPUSH {d0}
    VPOP {d0}
    LDR r0, =resultados
    ADD r0, r0, #72
    VSTR d0, [r0]

    MOV r0, #10
    BL exibir_resultado_uart


@ === LINHA 11 ===
    @ RES: resultado de 0 linhas atras (linha 10)
    LDR r0, =resultados
    ADD r0, r0, #72
    VLDR d0, [r0]
    LDR r0, =resultados
    ADD r0, r0, #80
    VSTR d0, [r0]

    MOV r0, #11
    BL exibir_resultado_uart


@ === LINHA 12 ===
    @ Avaliacao RPN com pilha VFP
    LDR r0, =const_14
    VLDR d0, [r0]                            @ 100.0
    VPUSH {d0}
    LDR r0, =const_7
    VLDR d0, [r0]                            @ 3.0
    VPUSH {d0}
    LDR r0, =const_10
    VLDR d0, [r0]                            @ 2.0
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VADD.F64 d0, d0, d1                      @ A + B
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VDIV.F64 d0, d0, d1                      @ A / B
    VPUSH {d0}
    LDR r0, =mem_MASSA
    VLDR d0, [r0]                            @ MASSA
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VADD.F64 d0, d0, d1                      @ A + B
    VPUSH {d0}
    VPOP {d0}
    LDR r0, =resultados
    ADD r0, r0, #88
    VSTR d0, [r0]

    MOV r0, #12
    BL exibir_resultado_uart


@ === LINHA 13 ===
    @ Avaliacao RPN com pilha VFP
    LDR r0, =mem_GRAVIDADE
    VLDR d0, [r0]                            @ GRAVIDADE
    VPUSH {d0}
    LDR r0, =const_10
    VLDR d0, [r0]                            @ 2.0
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VCVT.S32.F64 s4, d1
    VMOV r1, s4                              @ expoente inteiro
    LDR r0, =const_1
    VLDR d2, [r0]                            @ acumulador = 1.0
    CMP r1, #0
    BLE pot_fim_4
pot_loop_3:
    VMUL.F64 d2, d2, d0                      @ acum *= base
    SUBS r1, r1, #1
    BGT pot_loop_3
pot_fim_4:
    VMOV.F64 d0, d2
    VPUSH {d0}
    LDR r0, =mem_MASSA
    VLDR d0, [r0]                            @ MASSA
    VPUSH {d0}
    LDR r0, =const_15
    VLDR d0, [r0]                            @ 10.0
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VDIV.F64 d0, d0, d1                      @ A / B
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VSUB.F64 d0, d0, d1                      @ A - B
    VPUSH {d0}
    VPOP {d0}
    LDR r0, =resultados
    ADD r0, r0, #96
    VSTR d0, [r0]

    MOV r0, #13
    BL exibir_resultado_uart


@ === FIM ===
fim:
    B fim


@ === SUBROTINAS DE SAIDA ===

exibir_resultado_uart:
    PUSH {r4-r8, lr}
    VPUSH {d0-d3}
    MOV r4, r0
    VMOV.F64 d3, d0
    LDR r0, =str_linha
    BL uart_print_string
    MOV r0, r4
    BL uart_print_int
    LDR r0, =str_igual
    BL uart_print_string
    VMOV.F64 d0, d3
    BL uart_print_double
    LDR r0, =str_newline
    BL uart_print_string
    VMOV.F64 d0, d3
    BL exibir_hex_displays
    VPOP {d0-d3}
    POP {r4-r8, pc}

uart_print_char:
    PUSH {r1-r2, lr}
    LDR r1, =0xFF201000
uart_wait_5:
    LDR r2, [r1, #4]
    LSR r2, r2, #16
    CMP r2, #0
    BEQ uart_wait_5
    STR r0, [r1]
    POP {r1-r2, pc}

uart_print_string:
    PUSH {r4, lr}
    MOV r4, r0
str_loop_6:
    LDRB r0, [r4], #1
    CMP r0, #0
    BEQ str_fim_7
    BL uart_print_char
    B str_loop_6
str_fim_7:
    POP {r4, pc}

uart_print_int:
    PUSH {r4-r6, lr}
    MOV r4, r0
    MOV r5, #0
    MOV r6, #100
    BL _print_digito
    MOV r6, #10
    BL _print_digito
    ADD r0, r4, #0x30
    BL uart_print_char
    POP {r4-r6, pc}

_print_digito:
    PUSH {lr}
    MOV r0, #0
div_loop_8:
    CMP r4, r6
    BLT div_fim_9
    SUB r4, r4, r6
    ADD r0, r0, #1
    B div_loop_8
div_fim_9:
    CMP r0, #0
    BEQ skip_dig_10
    MOV r5, #1
    ADD r0, r0, #0x30
    BL uart_print_char
    POP {pc}
skip_dig_10:
    CMP r5, #0
    BEQ skip_dig2_11
    MOV r0, #0x30
    BL uart_print_char
skip_dig2_11:
    POP {pc}

uart_print_double:
    PUSH {r4-r6, lr}
    VPUSH {d0-d2}
    VMOV r4, r5, d0
    TST r5, #0x80000000
    BEQ pos_12
    LDR r0, =str_menos
    BL uart_print_string
    VNEG.F64 d0, d0
pos_12:
    VCVT.S32.F64 s0, d0
    VMOV r0, s0
    MOV r4, r0
    BL uart_print_int
    LDR r0, =str_ponto
    BL uart_print_string
    VCVT.F64.S32 d1, s0
    VSUB.F64 d0, d0, d1
    LDR r0, =const_15
    VLDR d1, [r0]
    VMUL.F64 d0, d0, d1
    LDR r0, =const_4
    VLDR d1, [r0]
    VADD.F64 d0, d0, d1                      @ arredondar
    VCVT.S32.F64 s0, d0
    VMOV r0, s0
    CMP r0, #0
    BGE abs_dec_13
    RSB r0, r0, #0
abs_dec_13:
    ADD r0, r0, #0x30
    BL uart_print_char
    VPOP {d0-d2}
    POP {r4-r6, pc}

_div_r4_r1:
    PUSH {lr}
    MOV r6, #0
dloop_14:
    CMP r4, r1
    BLT ddone_15
    SUB r4, r4, r1
    ADD r6, r6, #1
    B dloop_14
ddone_15:
    MOV r0, r4                               @ resto
    MOV r4, r6                               @ quociente vira proximo dividendo
    POP {pc}

exibir_hex_displays:
    PUSH {r4-r7, lr}
    VABS.F64 d0, d0
    VCVT.S32.F64 s0, d0
    VMOV r4, s0
    LDR r5, =tabela_7seg
    MOV r7, #0
    MOV r1, #10
    BL _div_r4_r1                            @ r4/10 -> r6=quot, r0=resto
    LDRB r0, [r5, r0]
    ORR r7, r7, r0
    BL _div_r4_r1                            @ r4/10 -> r6=quot, r0=resto
    LDRB r0, [r5, r0]
    LSL r0, r0, #8
    ORR r7, r7, r0
    BL _div_r4_r1                            @ r4/10 -> r6=quot, r0=resto
    LDRB r0, [r5, r0]
    LSL r0, r0, #16
    ORR r7, r7, r0
    BL _div_r4_r1                            @ r4/10 -> r6=quot, r0=resto
    LDRB r0, [r5, r0]
    LSL r0, r0, #24
    ORR r7, r7, r0
    LDR r0, =0xFF200020
    STR r7, [r0]
    POP {r4-r7, pc}
