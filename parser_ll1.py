# Aluno: Gabriel Almeida Fontes - lightlord77
# Grupo: RA1 1
# Disciplina: Linguagens Formais e Autômatos - PUCPR 2026-1
# Professor: Frank de Alcantara

import json
from lexer import Token, TipoToken


class ErroSintatico(Exception):
    def __init__(self, mensagem, token=None):
        self.token = token
        if token:
            super().__init__(f"Erro sintatico na linha {token.linha}, coluna {token.coluna}: {mensagem}")
        else:
            super().__init__(f"Erro sintatico: {mensagem}")


class No:
    def __init__(self, tipo, valor=None, filhos=None, linha=None):
        self.tipo = tipo
        self.valor = valor
        self.filhos = filhos or []
        self.linha = linha

    def to_dict(self):
        d = {"tipo": self.tipo}
        if self.valor is not None:
            d["valor"] = self.valor
        if self.linha is not None:
            d["linha"] = self.linha
        if self.filhos:
            d["filhos"] = [f.to_dict() for f in self.filhos]
        return d

    def __repr__(self):
        return f"No({self.tipo}, {self.valor}, filhos={len(self.filhos)})"

    def to_texto(self, nivel=0):
        indent = "  " * nivel
        resultado = f"{indent}{self.tipo}"
        if self.valor is not None:
            resultado += f": {self.valor}"
        resultado += "\n"
        for filho in self.filhos:
            resultado += filho.to_texto(nivel + 1)
        return resultado


class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def token_atual(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(TipoToken.EOF, "EOF", 0, 0)

    def consumir(self, tipo_esperado=None):
        tok = self.token_atual()
        if tipo_esperado and tok.tipo != tipo_esperado:
            raise ErroSintatico(
                f"Esperava {tipo_esperado.name}, encontrou {tok.tipo.name} ('{tok.valor}')",
                tok
            )
        self.pos += 1
        return tok

    def espiar(self, offset=1):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return Token(TipoToken.EOF, "EOF", 0, 0)

    # === Funcoes recursivas para cada nao-terminal ===

    def parsear(self):
        arvore = self.parse_programa()
        tok = self.token_atual()
        if tok.tipo != TipoToken.EOF:
            raise ErroSintatico(f"Tokens inesperados apos (END): '{tok.valor}'", tok)
        return arvore

    def parse_programa(self):
        self.consumir(TipoToken.LPAREN)
        self.consumir(TipoToken.KW_START)
        self.consumir(TipoToken.RPAREN)
        cmds = self.parse_lista_cmd()
        self.consumir(TipoToken.LPAREN)
        self.consumir(TipoToken.KW_END)
        self.consumir(TipoToken.RPAREN)
        return No("programa", filhos=cmds)

    def parse_lista_cmd(self):
        cmds = []
        while self.token_atual().tipo == TipoToken.LPAREN:
            proximo = self.espiar(1)
            if proximo.tipo == TipoToken.KW_END:
                break
            if proximo.tipo in (TipoToken.KW_ENDIF, TipoToken.KW_ENDWHILE,
                                TipoToken.KW_ELSE):
                break
            cmds.append(self.parse_comando())
        return cmds

    def parse_comando(self):
        self.consumir(TipoToken.LPAREN)
        tok = self.token_atual()

        if tok.tipo == TipoToken.KW_IF:
            no = self.parse_if()
        elif tok.tipo == TipoToken.KW_WHILE:
            no = self.parse_while()
        elif tok.tipo == TipoToken.NUMBER:
            no = self.parse_corpo_numero()
        elif tok.tipo == TipoToken.MEM_ID:
            nome = self.consumir(TipoToken.MEM_ID)
            no = No("mem_load", valor=nome.valor, linha=nome.linha)
        elif tok.tipo == TipoToken.LPAREN:
            no = self.parse_corpo_subexpr()
        else:
            raise ErroSintatico(
                f"Inicio de comando inesperado: '{tok.valor}' ({tok.tipo.name})", tok
            )

        self.consumir(TipoToken.RPAREN)
        return no

    def parse_corpo_numero(self):
        num_tok = self.consumir(TipoToken.NUMBER)
        tok = self.token_atual()

        if tok.tipo == TipoToken.KW_RES:
            self.consumir(TipoToken.KW_RES)
            return No("res", valor=num_tok.valor, linha=num_tok.linha)
        elif tok.tipo == TipoToken.MEM_ID:
            mem_tok = self.consumir(TipoToken.MEM_ID)
            return No("mem_store", valor=mem_tok.valor, linha=num_tok.linha,
                       filhos=[No("number", valor=num_tok.valor, linha=num_tok.linha)])
        else:
            num_no = No("number", valor=num_tok.valor, linha=num_tok.linha)
            return self.parse_resto_expr(num_no)

    def parse_corpo_subexpr(self):
        sub = self.parse_subexpr_como_operando()
        tok = self.token_atual()

        if tok.tipo == TipoToken.MEM_ID:
            mem_tok = self.consumir(TipoToken.MEM_ID)
            return No("mem_store", valor=mem_tok.valor, linha=sub.linha,
                       filhos=[sub])
        elif tok.tipo in (TipoToken.OPERATOR, TipoToken.COMP_OP):
            return self.parse_resto_expr(sub)
        elif tok.tipo in (TipoToken.NUMBER, TipoToken.LPAREN):
            return self.parse_resto_expr(sub)
        elif tok.tipo == TipoToken.RPAREN:
            return sub
        else:
            raise ErroSintatico(
                f"Esperava operador, MEM_ID ou ')' apos sub-expressao, encontrou '{tok.valor}'",
                tok
            )

    def parse_resto_expr(self, primeiro_operando):
        tok = self.token_atual()

        if tok.tipo == TipoToken.OPERATOR:
            op_tok = self.consumir(TipoToken.OPERATOR)
            expr = No("expr_bin", valor=op_tok.valor, linha=op_tok.linha,
                       filhos=[primeiro_operando, No("number", valor="0")])
            return self._check_mem_store_after(expr)
        elif tok.tipo == TipoToken.COMP_OP:
            op_tok = self.consumir(TipoToken.COMP_OP)
            expr = No("expr_cmp", valor=op_tok.valor, linha=op_tok.linha,
                       filhos=[primeiro_operando, No("number", valor="0")])
            return self._check_mem_store_after(expr)

        segundo = self.parse_operando()
        tok = self.token_atual()

        if tok.tipo == TipoToken.OPERATOR:
            op_tok = self.consumir(TipoToken.OPERATOR)
            expr = No("expr_bin", valor=op_tok.valor, linha=op_tok.linha,
                       filhos=[primeiro_operando, segundo])
            return self._check_mem_store_after(expr)
        elif tok.tipo == TipoToken.COMP_OP:
            op_tok = self.consumir(TipoToken.COMP_OP)
            expr = No("expr_cmp", valor=op_tok.valor, linha=op_tok.linha,
                       filhos=[primeiro_operando, segundo])
            return self._check_mem_store_after(expr)
        else:
            raise ErroSintatico(
                f"Esperava operador apos dois operandos, encontrou '{tok.valor}'",
                tok
            )

    def _check_mem_store_after(self, expr):
        tok = self.token_atual()
        if tok.tipo == TipoToken.MEM_ID:
            mem_tok = self.consumir(TipoToken.MEM_ID)
            return No("mem_store", valor=mem_tok.valor, linha=expr.linha,
                       filhos=[expr])
        return expr

    def parse_resto_cmp(self, primeiro_operando):
        segundo = self.parse_operando()
        op_tok = self.consumir(TipoToken.COMP_OP)
        return No("expr_cmp", valor=op_tok.valor, linha=op_tok.linha,
                   filhos=[primeiro_operando, segundo])

    def parse_operando(self):
        tok = self.token_atual()
        if tok.tipo == TipoToken.NUMBER:
            num_tok = self.consumir(TipoToken.NUMBER)
            return No("number", valor=num_tok.valor, linha=num_tok.linha)
        elif tok.tipo == TipoToken.LPAREN:
            return self.parse_subexpr_como_operando()
        else:
            raise ErroSintatico(
                f"Esperava operando (NUMBER ou sub-expressao), encontrou '{tok.valor}'",
                tok
            )

    def parse_subexpr_como_operando(self):
        self.consumir(TipoToken.LPAREN)
        tok = self.token_atual()

        if tok.tipo == TipoToken.MEM_ID:
            nome = self.consumir(TipoToken.MEM_ID)
            self.consumir(TipoToken.RPAREN)
            return No("mem_load", valor=nome.valor, linha=nome.linha)
        elif tok.tipo == TipoToken.NUMBER:
            no = self.parse_corpo_numero()
            self.consumir(TipoToken.RPAREN)
            return no
        elif tok.tipo == TipoToken.LPAREN:
            no = self.parse_corpo_subexpr()
            self.consumir(TipoToken.RPAREN)
            return no
        else:
            raise ErroSintatico(
                f"Conteudo inesperado em sub-expressao: '{tok.valor}'", tok
            )

    def parse_if(self):
        tok_if = self.consumir(TipoToken.KW_IF)
        cond = self.parse_expr_cmp()
        self.consumir(TipoToken.KW_THEN)
        bloco_then = self.parse_lista_cmd()
        tok = self.token_atual()
        if tok.tipo == TipoToken.KW_ELSE:
            self.consumir(TipoToken.KW_ELSE)
            bloco_else = self.parse_lista_cmd()
            self.consumir(TipoToken.KW_ENDIF)
            return No("if_else", linha=tok_if.linha,
                       filhos=[cond,
                               No("bloco_then", filhos=bloco_then),
                               No("bloco_else", filhos=bloco_else)])
        else:
            self.consumir(TipoToken.KW_ENDIF)
            return No("if", linha=tok_if.linha,
                       filhos=[cond,
                               No("bloco_then", filhos=bloco_then)])

    def parse_while(self):
        tok_while = self.consumir(TipoToken.KW_WHILE)
        cond = self.parse_expr_cmp()
        self.consumir(TipoToken.KW_DO)
        bloco = self.parse_lista_cmd()
        self.consumir(TipoToken.KW_ENDWHILE)
        return No("while", linha=tok_while.linha,
                   filhos=[cond, No("bloco_do", filhos=bloco)])

    def parse_expr_cmp(self):
        self.consumir(TipoToken.LPAREN)
        op1 = self.parse_operando()
        op2 = self.parse_operando()
        op_tok = self.consumir(TipoToken.COMP_OP)
        self.consumir(TipoToken.RPAREN)
        return No("expr_cmp", valor=op_tok.valor, linha=op_tok.linha,
                   filhos=[op1, op2])


def gerarArvore(tokens):
    parser = Parser(tokens)
    return parser.parsear()


def parsear(tokens, tabela_ll1=None):
    return gerarArvore(tokens)
