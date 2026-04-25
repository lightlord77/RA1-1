# Aluno: Gabriel Almeida Fontes - lightlord77
# Grupo: RA1 1
# Disciplina: Linguagens Formais e Autômatos - PUCPR 2026-1
# Professor: Frank de Alcantara

from lexer import parseExpressao, ErroLexico, TipoToken, Token
from parser_ll1 import parsear, gerarArvore, ErroSintatico


def tokenizar_programa(texto):
    linhas = texto.strip().split('\n')
    todos = []
    for i, linha in enumerate(linhas, 1):
        linha = linha.strip()
        if not linha:
            continue
        tokens = parseExpressao(linha, linha_num=i)
        todos.extend(tokens)
    todos.append(Token(tipo=TipoToken.EOF, valor="EOF", linha=0, coluna=0))
    return todos


def teste_expressao_simples():
    prog = "(START)\n(3.0 2.0 +)\n(END)"
    tokens = tokenizar_programa(prog)
    arvore = parsear(tokens)
    assert arvore.tipo == "programa"
    assert len(arvore.filhos) == 1
    assert arvore.filhos[0].tipo == "expr_bin"
    assert arvore.filhos[0].valor == "+"
    print("  [OK] Expressao simples")


def teste_expressao_aninhada():
    prog = "(START)\n((3.0 2.0 +) (4.0 1.0 -) *)\n(END)"
    tokens = tokenizar_programa(prog)
    arvore = parsear(tokens)
    assert arvore.filhos[0].tipo == "expr_bin"
    assert arvore.filhos[0].valor == "*"
    assert arvore.filhos[0].filhos[0].tipo == "expr_bin"
    assert arvore.filhos[0].filhos[0].valor == "+"
    print("  [OK] Expressao aninhada")


def teste_mem_store():
    prog = "(START)\n(42.0 X)\n(END)"
    tokens = tokenizar_programa(prog)
    arvore = parsear(tokens)
    assert arvore.filhos[0].tipo == "mem_store"
    assert arvore.filhos[0].valor == "X"
    print("  [OK] MEM_STORE")


def teste_mem_load():
    prog = "(START)\n(42.0 X)\n(X)\n(END)"
    tokens = tokenizar_programa(prog)
    arvore = parsear(tokens)
    assert arvore.filhos[1].tipo == "mem_load"
    assert arvore.filhos[1].valor == "X"
    print("  [OK] MEM_LOAD")


def teste_res():
    prog = "(START)\n(3.0 2.0 +)\n(0 RES)\n(END)"
    tokens = tokenizar_programa(prog)
    arvore = parsear(tokens)
    assert arvore.filhos[1].tipo == "res"
    assert arvore.filhos[1].valor == "0"
    print("  [OK] RES")


def teste_if_simples():
    prog = "(START)\n(IF (5.0 3.0 >) THEN (10.0 2.0 +) ENDIF)\n(END)"
    tokens = tokenizar_programa(prog)
    arvore = parsear(tokens)
    assert arvore.filhos[0].tipo == "if"
    assert arvore.filhos[0].filhos[0].tipo == "expr_cmp"
    print("  [OK] IF simples")


def teste_if_else():
    prog = "(START)\n(IF (5.0 3.0 >) THEN (10.0 2.0 +) ELSE (10.0 2.0 -) ENDIF)\n(END)"
    tokens = tokenizar_programa(prog)
    arvore = parsear(tokens)
    assert arvore.filhos[0].tipo == "if_else"
    assert len(arvore.filhos[0].filhos) == 3
    print("  [OK] IF/ELSE")


def teste_while():
    prog = "(START)\n(1.0 X)\n(WHILE ((X) 5.0 <) DO ((X) 1.0 + X) ENDWHILE)\n(END)"
    tokens = tokenizar_programa(prog)
    arvore = parsear(tokens)
    assert arvore.filhos[1].tipo == "while"
    print("  [OK] WHILE")


def teste_todos_operadores():
    prog = "(START)\n(10.0 3.0 +)\n(10.0 3.0 -)\n(10.0 3.0 *)\n(10.0 3.0 |)\n(10 3 /)\n(10 3 %)\n(2.0 3 ^)\n(END)"
    tokens = tokenizar_programa(prog)
    arvore = parsear(tokens)
    ops = [f.valor for f in arvore.filhos]
    assert ops == ['+', '-', '*', '|', '/', '%', '^']
    print("  [OK] Todos os operadores")


def teste_comparacoes():
    prog = "(START)\n(IF (5.0 3.0 >) THEN (1.0 2.0 +) ENDIF)\n(IF (5.0 3.0 <) THEN (1.0 2.0 +) ENDIF)\n(IF (5.0 5.0 ==) THEN (1.0 2.0 +) ENDIF)\n(IF (5.0 3.0 !=) THEN (1.0 2.0 +) ENDIF)\n(IF (5.0 3.0 >=) THEN (1.0 2.0 +) ENDIF)\n(IF (5.0 3.0 <=) THEN (1.0 2.0 +) ENDIF)\n(END)"
    tokens = tokenizar_programa(prog)
    arvore = parsear(tokens)
    cmps = [f.filhos[0].valor for f in arvore.filhos]
    assert cmps == ['>', '<', '==', '!=', '>=', '<=']
    print("  [OK] Todos operadores de comparacao")


def teste_erro_falta_start():
    prog = "(3.0 2.0 +)\n(END)"
    tokens = tokenizar_programa(prog)
    try:
        parsear(tokens)
        print("  [FALHA] Deveria dar erro: falta START")
    except ErroSintatico:
        print("  [OK] Erro detectado: falta START")


def teste_erro_falta_end():
    prog = "(START)\n(3.0 2.0 +)"
    tokens = tokenizar_programa(prog)
    try:
        parsear(tokens)
        print("  [FALHA] Deveria dar erro: falta END")
    except ErroSintatico:
        print("  [OK] Erro detectado: falta END")


def teste_erro_parentese_faltando():
    prog = "(START)\n(3.0 2.0 +\n(END)"
    tokens = tokenizar_programa(prog)
    try:
        parsear(tokens)
        print("  [FALHA] Deveria dar erro: parentese faltando")
    except ErroSintatico:
        print("  [OK] Erro detectado: parentese faltando")


def teste_erro_operador_faltando():
    prog = "(START)\n(3.0 2.0)\n(END)"
    tokens = tokenizar_programa(prog)
    try:
        parsear(tokens)
        print("  [FALHA] Deveria dar erro: operador faltando")
    except ErroSintatico:
        print("  [OK] Erro detectado: operador faltando")


def teste_erro_if_sem_endif():
    prog = "(START)\n(IF (5.0 3.0 >) THEN (1.0 2.0 +))\n(END)"
    tokens = tokenizar_programa(prog)
    try:
        parsear(tokens)
        print("  [FALHA] Deveria dar erro: IF sem ENDIF")
    except ErroSintatico:
        print("  [OK] Erro detectado: IF sem ENDIF")


def teste_erro_while_sem_endwhile():
    prog = "(START)\n(WHILE (1.0 5.0 <) DO (1.0 2.0 +))\n(END)"
    tokens = tokenizar_programa(prog)
    try:
        parsear(tokens)
        print("  [FALHA] Deveria dar erro: WHILE sem ENDWHILE")
    except ErroSintatico:
        print("  [OK] Erro detectado: WHILE sem ENDWHILE")


def teste_erro_lexico():
    prog = "(START)\n(3.0 & 2.0)\n(END)"
    try:
        tokens = tokenizar_programa(prog)
        print("  [FALHA] Deveria dar erro lexico")
    except ErroLexico:
        print("  [OK] Erro lexico detectado: caractere invalido")


if __name__ == "__main__":
    print("=== Testes do Parser LL(1) ===")
    print()
    print("Testes validos:")
    teste_expressao_simples()
    teste_expressao_aninhada()
    teste_mem_store()
    teste_mem_load()
    teste_res()
    teste_if_simples()
    teste_if_else()
    teste_while()
    teste_todos_operadores()
    teste_comparacoes()
    print()
    print("Testes de erro:")
    teste_erro_falta_start()
    teste_erro_falta_end()
    teste_erro_parentese_faltando()
    teste_erro_operador_faltando()
    teste_erro_if_sem_endif()
    teste_erro_while_sem_endwhile()
    teste_erro_lexico()
    print()
    print("Todos os testes concluidos!")
