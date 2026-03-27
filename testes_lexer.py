# Aluno: Gabriel Almeida Fontes - lightlord77
# Testes do analisador léxico: entradas válidas e inválidas

from lexer import AnalisadorLexico, ErroLexico, parseExpressao, TipoToken


def teste_numeros_inteiros():
    tokens = parseExpressao("(3 2 +)")
    tipos = [t.tipo for t in tokens]
    assert tipos == [TipoToken.LPAREN, TipoToken.NUMBER, TipoToken.NUMBER,
                     TipoToken.OPERATOR, TipoToken.RPAREN], f"Falhou: {tokens}"
    assert tokens[1].valor == "3"
    assert tokens[2].valor == "2"
    print("[OK] Números inteiros")


def teste_numeros_reais():
    tokens = parseExpressao("(3.14 2.0 +)")
    assert tokens[1].valor == "3.14"
    assert tokens[2].valor == "2.0"
    assert tokens[1].tipo == TipoToken.NUMBER
    print("[OK] Números reais")


def teste_todos_operadores():
    for op in ['+', '-', '*', '/', '%', '^']:
        tokens = parseExpressao(f"(1 2 {op})")
        op_token = [t for t in tokens if t.tipo == TipoToken.OPERATOR]
        assert len(op_token) == 1, f"Operador '{op}' não reconhecido"
        assert op_token[0].valor == op
    print("[OK] Todos os operadores simples")


def teste_divisao_inteira():
    tokens = parseExpressao("(10 3 //)")
    tipos = [t.tipo for t in tokens]
    assert TipoToken.INTDIV in tipos, f"INTDIV não encontrado: {tokens}"
    intdiv = [t for t in tokens if t.tipo == TipoToken.INTDIV][0]
    assert intdiv.valor == "//"
    print("[OK] Divisão inteira //")


def teste_keyword_res():
    tokens = parseExpressao("(5 RES)")
    tipos = [t.tipo for t in tokens]
    assert TipoToken.KW_RES in tipos, f"KW_RES não encontrado: {tokens}"
    print("[OK] Keyword RES")


def teste_mem_id():
    tokens = parseExpressao("(10.5 CONTADOR)")
    mem_tokens = [t for t in tokens if t.tipo == TipoToken.MEM_ID]
    assert len(mem_tokens) == 1
    assert mem_tokens[0].valor == "CONTADOR"
    print("[OK] Identificador de memória MEM_ID")


def teste_mem_id_curto():
    tokens = parseExpressao("(X)")
    mem_tokens = [t for t in tokens if t.tipo == TipoToken.MEM_ID]
    assert len(mem_tokens) == 1
    assert mem_tokens[0].valor == "X"
    print("[OK] MEM_ID curto (uma letra)")


def teste_expressao_aninhada():
    tokens = parseExpressao("((1.5 2.0 *) (3.0 4.0 *) /)")
    tipos = [t.tipo for t in tokens]
    assert tipos[0] == TipoToken.LPAREN
    assert tipos[1] == TipoToken.LPAREN
    print("[OK] Expressão aninhada")


def teste_expressao_complexa():
    tokens = parseExpressao("((3.14 (2.0 1.0 +) *) 7.0 -)")
    assert len(tokens) > 0
    lparens = sum(1 for t in tokens if t.tipo == TipoToken.LPAREN)
    rparens = sum(1 for t in tokens if t.tipo == TipoToken.RPAREN)
    assert lparens == rparens, f"Parênteses desbalanceados: {lparens} ( vs {rparens} )"
    print("[OK] Expressão complexa com múltiplos aninhamentos")


# --- Entradas INVÁLIDAS ---

def teste_erro_caractere_invalido():
    try:
        parseExpressao("(3.14 2.0 &)")
        assert False, "Deveria ter lançado ErroLexico"
    except ErroLexico as e:
        assert "&" in str(e)
        print(f"[OK] Erro detectado: {e}")


def teste_erro_numero_dois_pontos():
    try:
        parseExpressao("(3.14.5 2.0 +)")
        assert False, "Deveria ter lançado ErroLexico"
    except ErroLexico as e:
        assert "malformado" in str(e).lower() or "ponto" in str(e).lower()
        print(f"[OK] Erro detectado: {e}")


def teste_erro_ponto_sem_decimal():
    try:
        parseExpressao("(3. 2 +)")
        assert False, "Deveria ter lançado ErroLexico"
    except ErroLexico as e:
        print(f"[OK] Erro detectado: {e}")


def teste_erro_virgula():
    try:
        parseExpressao("(3,45 2.0 +)")
        assert False, "Deveria ter lançado ErroLexico"
    except ErroLexico as e:
        print(f"[OK] Erro detectado (vírgula): {e}")


def executar_todos_os_testes():
    print("=" * 60)
    print("TESTES DO ANALISADOR LÉXICO")
    print("=" * 60)

    print("\n--- Entradas VÁLIDAS ---")
    teste_numeros_inteiros()
    teste_numeros_reais()
    teste_todos_operadores()
    teste_divisao_inteira()
    teste_keyword_res()
    teste_mem_id()
    teste_mem_id_curto()
    teste_expressao_aninhada()
    teste_expressao_complexa()

    print("\n--- Entradas INVÁLIDAS ---")
    teste_erro_caractere_invalido()
    teste_erro_numero_dois_pontos()
    teste_erro_ponto_sem_decimal()
    teste_erro_virgula()

    print("\n" + "=" * 60)
    print("TODOS OS TESTES PASSARAM!")
    print("=" * 60)


if __name__ == "__main__":
    executar_todos_os_testes()
