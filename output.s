
@ === SECAO DE DADOS ===
.data
.align 3

@ Constantes IEEE 754 (64 bits)
const_1:
    .word 0x51EB851F        @ 9.81 (low)
    .word 0x40239EB8        @ 9.81 (high)

const_2:
    .word 0x00000000        @ 72.0 (low)
    .word 0x40520000        @ 72.0 (high)

const_3:
    .word 0x00000000        @ 100.0 (low)
    .word 0x40590000        @ 100.0 (high)

const_4:
    .word 0x00000000        @ 50.0 (low)
    .word 0x40490000        @ 50.0 (high)

const_5:
    .word 0x00000000        @ 0.0 (low)
    .word 0x00000000        @ 0.0 (high)

const_6:
    .word 0x00000000        @ 1.0 (low)
    .word 0x3FF00000        @ 1.0 (high)

const_7:
    .word 0x00000000        @ 3.0 (low)
    .word 0x40080000        @ 3.0 (high)

const_8:
    .word 0x00000000        @ 2.5 (low)
    .word 0x40040000        @ 2.5 (high)

const_9:
    .word 0x00000000        @ 4.0 (low)
    .word 0x40100000        @ 4.0 (high)

const_10:
    .word 0x00000000        @ 10.0 (low)
    .word 0x40240000        @ 10.0 (high)

const_11:
    .word 0x00000000        @ 45.0 (low)
    .word 0x40468000        @ 45.0 (high)

const_12:
    .word 0x00000000        @ 7.0 (low)
    .word 0x401C0000        @ 7.0 (high)

const_13:
    .word 0x00000000        @ 17.0 (low)
    .word 0x40310000        @ 17.0 (high)

const_14:
    .word 0x00000000        @ 5.0 (low)
    .word 0x40140000        @ 5.0 (high)

const_15:
    .word 0x00000000        @ 0.5 (low)
    .word 0x3FE00000        @ 0.5 (high)

@ Variaveis de memoria
mem_CONT:
    .word 0x00000000
    .word 0x00000000

mem_GRAVIDADE:
    .word 0x00000000
    .word 0x00000000

mem_MASSA:
    .word 0x00000000
    .word 0x00000000

mem_SALDO:
    .word 0x00000000
    .word 0x00000000

@ Array de resultados
resultados:
    .space 376

@ Tabela 7 segmentos
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

@ Strings UART
str_linha:   .asciz "Linha "
str_igual:   .asciz " = "
str_nl:      .asciz "\n"
str_ponto:   .asciz "."
str_menos:   .asciz "-"



@ === SECAO DE CODIGO ===
.text
.global _start

_start:
    @ Habilitar VFP
    MRC p15, 0, r0, c1, c0, 2
    ORR r0, r0, #0xF00000
    MCR p15, 0, r0, c1, c0, 2
    MOV r0, #0x40000000
    VMSR FPEXC, r0

    LDR sp, =0x20000                         @ stack pointer

@ === LINHA 1 (MEM_STORE GRAVIDADE) ===
    LDR r0, =const_1
    VLDR d0, [r0]                            @ 9.81
    VPUSH {d0}
    VPOP {d0}
    LDR r0, =mem_GRAVIDADE
    VSTR d0, [r0]                            @ salva em GRAVIDADE
    LDR r0, =resultados
    VSTR d0, [r0]
    MOV r0, #1
    BL exibir_resultado_uart

@ === LINHA 2 (MEM_STORE MASSA) ===
    LDR r0, =const_2
    VLDR d0, [r0]                            @ 72.0
    VPUSH {d0}
    VPOP {d0}
    LDR r0, =mem_MASSA
    VSTR d0, [r0]                            @ salva em MASSA
    LDR r0, =resultados
    ADD r0, r0, #8
    VSTR d0, [r0]
    MOV r0, #2
    BL exibir_resultado_uart

@ === LINHA 3 ===
    LDR r0, =mem_MASSA
    VLDR d0, [r0]                            @ MASSA
    VPUSH {d0}
    LDR r0, =mem_GRAVIDADE
    VLDR d0, [r0]                            @ GRAVIDADE
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VMUL.F64 d0, d0, d1                      @ A * B
    LDR r0, =resultados
    ADD r0, r0, #16
    VSTR d0, [r0]
    MOV r0, #3
    BL exibir_resultado_uart

@ === LINHA 4 (RES 1) ===
    LDR r0, =resultados
    ADD r0, r0, #8
    VLDR d0, [r0]
    LDR r0, =resultados
    ADD r0, r0, #24
    VSTR d0, [r0]
    MOV r0, #4
    BL exibir_resultado_uart

@ === LINHA 5 (MEM_STORE SALDO) ===
    LDR r0, =const_3
    VLDR d0, [r0]                            @ 100.0
    VPUSH {d0}
    VPOP {d0}
    LDR r0, =mem_SALDO
    VSTR d0, [r0]                            @ salva em SALDO
    LDR r0, =resultados
    ADD r0, r0, #32
    VSTR d0, [r0]
    MOV r0, #5
    BL exibir_resultado_uart

    @ === IF/ELSE ===
    LDR r0, =mem_SALDO
    VLDR d0, [r0]                            @ SALDO
    VPUSH {d0}
    LDR r0, =const_4
    VLDR d0, [r0]                            @ 50.0
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VCMP.F64 d0, d1
    VMRS APSR_nzcv, FPSCR
    BGE ct_3
    LDR r0, =const_5
    VLDR d0, [r0]
    B ce_4
ct_3:
    LDR r0, =const_6
    VLDR d0, [r0]
ce_4:
    VPUSH {d0}
    VPOP {d0}
    LDR r0, =const_5
    VLDR d1, [r0]
    VCMP.F64 d0, d1
    VMRS APSR_nzcv, FPSCR
    BEQ else_1                               @ se falso vai pro else

@ === LINHA 6 (MEM_STORE SALDO) ===
    LDR r0, =mem_SALDO
    VLDR d0, [r0]                            @ SALDO
    VPUSH {d0}
    LDR r0, =const_4
    VLDR d0, [r0]                            @ 50.0
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VSUB.F64 d0, d0, d1                      @ A - B
    VPUSH {d0}
    VPOP {d0}
    LDR r0, =mem_SALDO
    VSTR d0, [r0]                            @ salva em SALDO
    LDR r0, =resultados
    ADD r0, r0, #40
    VSTR d0, [r0]
    MOV r0, #6
    BL exibir_resultado_uart
    B endif_2
else_1:

@ === LINHA 7 (MEM_STORE SALDO) ===
    LDR r0, =const_5
    VLDR d0, [r0]                            @ 0.0
    VPUSH {d0}
    VPOP {d0}
    LDR r0, =mem_SALDO
    VSTR d0, [r0]                            @ salva em SALDO
    LDR r0, =resultados
    ADD r0, r0, #48
    VSTR d0, [r0]
    MOV r0, #7
    BL exibir_resultado_uart
endif_2:

@ === LINHA 8 (MEM_LOAD SALDO) ===
    LDR r0, =mem_SALDO
    VLDR d0, [r0]                            @ carrega SALDO
    LDR r0, =resultados
    ADD r0, r0, #56
    VSTR d0, [r0]
    MOV r0, #8
    BL exibir_resultado_uart

@ === LINHA 9 (MEM_STORE CONT) ===
    LDR r0, =const_6
    VLDR d0, [r0]                            @ 1.0
    VPUSH {d0}
    VPOP {d0}
    LDR r0, =mem_CONT
    VSTR d0, [r0]                            @ salva em CONT
    LDR r0, =resultados
    ADD r0, r0, #64
    VSTR d0, [r0]
    MOV r0, #9
    BL exibir_resultado_uart

    @ === WHILE ===
wstart_5:
    LDR r0, =mem_CONT
    VLDR d0, [r0]                            @ CONT
    VPUSH {d0}
    LDR r0, =const_7
    VLDR d0, [r0]                            @ 3.0
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VCMP.F64 d0, d1
    VMRS APSR_nzcv, FPSCR
    BLT ct_7
    LDR r0, =const_5
    VLDR d0, [r0]
    B ce_8
ct_7:
    LDR r0, =const_6
    VLDR d0, [r0]
ce_8:
    VPUSH {d0}
    VPOP {d0}
    LDR r0, =const_5
    VLDR d1, [r0]
    VCMP.F64 d0, d1
    VMRS APSR_nzcv, FPSCR
    BEQ wend_6                               @ se falso sai

@ === LINHA 10 (MEM_STORE CONT) ===
    LDR r0, =mem_CONT
    VLDR d0, [r0]                            @ CONT
    VPUSH {d0}
    LDR r0, =mem_CONT
    VLDR d0, [r0]                            @ CONT
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VMUL.F64 d0, d0, d1                      @ A * B
    VPUSH {d0}
    VPOP {d0}
    LDR r0, =mem_CONT
    VSTR d0, [r0]                            @ salva em CONT
    LDR r0, =resultados
    ADD r0, r0, #72
    VSTR d0, [r0]
    MOV r0, #10
    BL exibir_resultado_uart

@ === LINHA 11 (MEM_STORE CONT) ===
    LDR r0, =mem_CONT
    VLDR d0, [r0]                            @ CONT
    VPUSH {d0}
    LDR r0, =const_6
    VLDR d0, [r0]                            @ 1.0
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VADD.F64 d0, d0, d1                      @ A + B
    VPUSH {d0}
    VPOP {d0}
    LDR r0, =mem_CONT
    VSTR d0, [r0]                            @ salva em CONT
    LDR r0, =resultados
    ADD r0, r0, #80
    VSTR d0, [r0]
    MOV r0, #11
    BL exibir_resultado_uart
    B wstart_5
wend_6:

@ === LINHA 12 (MEM_LOAD CONT) ===
    LDR r0, =mem_CONT
    VLDR d0, [r0]                            @ carrega CONT
    LDR r0, =resultados
    ADD r0, r0, #88
    VSTR d0, [r0]
    MOV r0, #12
    BL exibir_resultado_uart

@ === LINHA 13 ===
    LDR r0, =const_8
    VLDR d0, [r0]                            @ 2.5
    VPUSH {d0}
    LDR r0, =const_9
    VLDR d0, [r0]                            @ 4.0
    VPUSH {d0}
    LDR r0, =const_6
    VLDR d0, [r0]                            @ 1.0
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VSUB.F64 d0, d0, d1                      @ A - B
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VCVT.S32.F64 s4, d1
    VMOV r1, s4
    LDR r0, =const_6
    VLDR d2, [r0]
pow_9:
    CMP r1, #0
    BLE pow_end_10
    VMUL.F64 d2, d2, d0
    SUB r1, r1, #1
    B pow_9
pow_end_10:
    VMOV.F64 d0, d2
    VPUSH {d0}
    LDR r0, =const_10
    VLDR d0, [r0]                            @ 10.0
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VADD.F64 d0, d0, d1                      @ A + B
    LDR r0, =resultados
    ADD r0, r0, #96
    VSTR d0, [r0]
    MOV r0, #13
    BL exibir_resultado_uart

@ === LINHA 14 ===
    LDR r0, =const_11
    VLDR d0, [r0]                            @ 45
    VPUSH {d0}
    LDR r0, =const_12
    VLDR d0, [r0]                            @ 7
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VDIV.F64 d0, d0, d1                      @ A / B (div inteira)
    VCVT.S32.F64 s0, d0                      @ truncar
    VCVT.F64.S32 d0, s0
    LDR r0, =resultados
    ADD r0, r0, #104
    VSTR d0, [r0]
    MOV r0, #14
    BL exibir_resultado_uart

@ === LINHA 15 ===
    LDR r0, =const_13
    VLDR d0, [r0]                            @ 17
    VPUSH {d0}
    LDR r0, =const_14
    VLDR d0, [r0]                            @ 5
    VPUSH {d0}
    VPOP {d1}                                @ B
    VPOP {d0}                                @ A
    VMOV.F64 d2, d0                          @ copia A
    VDIV.F64 d0, d0, d1
    VCVT.S32.F64 s0, d0
    VCVT.F64.S32 d0, s0
    VMUL.F64 d0, d0, d1
    VSUB.F64 d0, d2, d0                      @ resto
    LDR r0, =resultados
    ADD r0, r0, #112
    VSTR d0, [r0]
    MOV r0, #15
    BL exibir_resultado_uart

@ === FIM ===
fim:
    B fim

@ === SUBROTINAS DE IO ===

exibir_resultado_uart:
    PUSH {r4, lr}
    MOV r4, r0
    VPUSH {d0}
    LDR r0, =str_linha
    BL uart_print_string
    MOV r0, r4
    BL uart_print_int
    LDR r0, =str_igual
    BL uart_print_string
    VPOP {d0}
    VPUSH {d0}
    BL uart_print_double
    LDR r0, =str_nl
    BL uart_print_string
    VPOP {d0}
    BL exibir_hex_displays
    POP {r4, pc}

uart_print_char:
    LDR r1, =0xFF201000
    STR r0, [r1]
    BX lr

uart_print_string:
    PUSH {r4, lr}
    MOV r4, r0
pstr_11:
    LDRB r0, [r4]
    CMP r0, #0
    BEQ pstr_e_12
    BL uart_print_char
    ADD r4, r4, #1
    B pstr_11
pstr_e_12:
    POP {r4, pc}

uart_print_int:
    PUSH {r4-r6, lr}
    MOV r4, r0
    MOV r5, #0
    MOV r1, #10
pid_13:
    BL _div_r4_r1
    ADD r0, r0, #0x30
    PUSH {r0}
    ADD r5, r5, #1
    CMP r4, #0
    BNE pid_13
pip_14:
    POP {r0}
    BL uart_print_char
    SUB r5, r5, #1
    CMP r5, #0
    BNE pip_14
    POP {r4-r6, pc}

uart_print_double:
    PUSH {r4-r6, lr}
    VPUSH {d0-d2}
    VMOV r4, r5, d0
    TST r5, #0x80000000
    BEQ pos_15
    LDR r0, =str_menos
    BL uart_print_string
    VNEG.F64 d0, d0
pos_15:
    VCVT.S32.F64 s0, d0
    VMOV r0, s0
    MOV r4, r0
    BL uart_print_int
    LDR r0, =str_ponto
    BL uart_print_string
    VCVT.F64.S32 d1, s0
    VSUB.F64 d0, d0, d1
    LDR r0, =const_10
    VLDR d1, [r0]
    VMUL.F64 d0, d0, d1
    LDR r0, =const_15
    VLDR d1, [r0]
    VADD.F64 d0, d0, d1                      @ arredondar
    VCVT.S32.F64 s0, d0
    VMOV r0, s0
    CMP r0, #0
    BGE absd_16
    RSB r0, r0, #0
absd_16:
    ADD r0, r0, #0x30
    BL uart_print_char
    VPOP {d0-d2}
    POP {r4-r6, pc}

_div_r4_r1:
    PUSH {lr}
    MOV r6, #0
dl_17:
    CMP r4, r1
    BLT dd_18
    SUB r4, r4, r1
    ADD r6, r6, #1
    B dl_17
dd_18:
    MOV r0, r4                               @ resto
    MOV r4, r6                               @ quociente
    POP {pc}

exibir_hex_displays:
    PUSH {r4-r7, lr}
    VABS.F64 d0, d0
    VCVT.S32.F64 s0, d0
    VMOV r4, s0
    LDR r5, =tabela_7seg
    MOV r7, #0
    MOV r1, #10
    BL _div_r4_r1
    LDRB r0, [r5, r0]
    ORR r7, r7, r0
    BL _div_r4_r1
    LDRB r0, [r5, r0]
    LSL r0, r0, #8
    ORR r7, r7, r0
    BL _div_r4_r1
    LDRB r0, [r5, r0]
    LSL r0, r0, #16
    ORR r7, r7, r0
    BL _div_r4_r1
    LDRB r0, [r5, r0]
    LSL r0, r0, #24
    ORR r7, r7, r0
    LDR r0, =0xFF200020
    STR r7, [r0]
    POP {r4-r7, pc}