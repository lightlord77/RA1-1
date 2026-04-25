# Aluno: Gabriel Almeida Fontes - lightlord77
# Grupo: RA1 1
# Disciplina: Linguagens Formais e Autômatos - PUCPR 2026-1
# Professor: Frank de Alcantara

from enum import Enum, auto
from dataclasses import dataclass


class TipoToken(Enum):
    NUMBER = auto()
    OPERATOR = auto()
    COMP_OP = auto()
    LPAREN = auto()
    RPAREN = auto()
    KW_RES = auto()
    KW_IF = auto()
    KW_THEN = auto()
    KW_ELSE = auto()
    KW_ENDIF = auto()
    KW_WHILE = auto()
    KW_DO = auto()
    KW_ENDWHILE = auto()
    KW_START = auto()
    KW_END = auto()
    MEM_ID = auto()
    EOF = auto()


KEYWORDS = {
    "RES": TipoToken.KW_RES,
    "IF": TipoToken.KW_IF,
    "THEN": TipoToken.KW_THEN,
    "ELSE": TipoToken.KW_ELSE,
    "ENDIF": TipoToken.KW_ENDIF,
    "WHILE": TipoToken.KW_WHILE,
    "DO": TipoToken.KW_DO,
    "ENDWHILE": TipoToken.KW_ENDWHILE,
    "START": TipoToken.KW_START,
    "END": TipoToken.KW_END,
}


@dataclass
class Token:
    tipo: TipoToken
    valor: str
    linha: int
    coluna: int

    def __repr__(self):
        return f"Token({self.tipo.name}, '{self.valor}', L{self.linha}:C{self.coluna})"

    def to_dict(self):
        return {
            "tipo": self.tipo.name,
            "valor": self.valor,
            "linha": self.linha,
            "coluna": self.coluna
        }

    @staticmethod
    def from_dict(d):
        return Token(
            tipo=TipoToken[d["tipo"]],
            valor=d["valor"],
            linha=d["linha"],
            coluna=d["coluna"]
        )


class ErroLexico(Exception):
    def __init__(self, mensagem, linha, coluna):
        self.mensagem = mensagem
        self.linha = linha
        self.coluna = coluna
        super().__init__(f"Erro lexico na linha {linha}, coluna {coluna}: {mensagem}")


class AnalisadorLexico:

    def __init__(self):
        self.tokens = []
        self.pos = 0
        self.linha_num = 0
        self.texto = ""

    def char_atual(self):
        if self.pos < len(self.texto):
            return self.texto[self.pos]
        return None

    def avancar(self):
        self.pos += 1

    def emitir(self, tipo, valor, coluna_inicio):
        token = Token(tipo=tipo, valor=valor, linha=self.linha_num, coluna=coluna_inicio)
        self.tokens.append(token)

    # === ESTADOS DO AUTOMATO ===

    def estado_inicial(self):
        while self.char_atual() is not None:
            c = self.char_atual()
            col = self.pos + 1

            if c == ' ' or c == '\t':
                self.avancar()
            elif c == '(':
                self.emitir(TipoToken.LPAREN, '(', col)
                self.avancar()
            elif c == ')':
                self.emitir(TipoToken.RPAREN, ')', col)
                self.avancar()
            elif c.isdigit():
                self.estado_numero(col)
            elif c == '|':
                self.emitir(TipoToken.OPERATOR, '|', col)
                self.avancar()
            elif c == '/':
                self.emitir(TipoToken.OPERATOR, '/', col)
                self.avancar()
            elif c in ('+', '-', '*', '%', '^'):
                self.emitir(TipoToken.OPERATOR, c, col)
                self.avancar()
            elif c in ('>', '<', '=', '!'):
                self.estado_comparacao(col)
            elif c.isupper():
                self.estado_identificador(col)
            elif c == '\n' or c == '\r':
                self.avancar()
            else:
                raise ErroLexico(f"Caractere inesperado: '{c}'", self.linha_num, col)

    def estado_numero(self, coluna_inicio):
        acumulador = ""
        tem_ponto = False

        while self.char_atual() is not None:
            c = self.char_atual()
            if c.isdigit():
                acumulador += c
                self.avancar()
            elif c == '.' and not tem_ponto:
                tem_ponto = True
                acumulador += c
                self.avancar()
                self.estado_decimal(acumulador, coluna_inicio)
                return
            elif c == '.' and tem_ponto:
                raise ErroLexico(
                    f"Numero malformado (dois pontos decimais): '{acumulador}.'",
                    self.linha_num, coluna_inicio
                )
            else:
                break

        if acumulador:
            self.emitir(TipoToken.NUMBER, acumulador, coluna_inicio)

    def estado_decimal(self, acumulador, coluna_inicio):
        tem_digito_decimal = False

        while self.char_atual() is not None:
            c = self.char_atual()
            if c.isdigit():
                acumulador += c
                tem_digito_decimal = True
                self.avancar()
            elif c == '.':
                raise ErroLexico(
                    f"Numero malformado (ponto extra): '{acumulador}.'",
                    self.linha_num, coluna_inicio
                )
            else:
                break

        if not tem_digito_decimal:
            raise ErroLexico(
                f"Numero malformado (nada apos o ponto): '{acumulador}'",
                self.linha_num, coluna_inicio
            )

        self.emitir(TipoToken.NUMBER, acumulador, coluna_inicio)

    def estado_comparacao(self, coluna_inicio):
        c = self.char_atual()
        self.avancar()

        if c in ('>', '<'):
            if self.char_atual() == '=':
                self.avancar()
                self.emitir(TipoToken.COMP_OP, c + '=', coluna_inicio)
            else:
                self.emitir(TipoToken.COMP_OP, c, coluna_inicio)
        elif c == '=':
            if self.char_atual() == '=':
                self.avancar()
                self.emitir(TipoToken.COMP_OP, '==', coluna_inicio)
            else:
                raise ErroLexico("Operador '=' incompleto (esperava '==')", self.linha_num, coluna_inicio)
        elif c == '!':
            if self.char_atual() == '=':
                self.avancar()
                self.emitir(TipoToken.COMP_OP, '!=', coluna_inicio)
            else:
                raise ErroLexico("Operador '!' incompleto (esperava '!=')", self.linha_num, coluna_inicio)

    def estado_identificador(self, coluna_inicio):
        acumulador = ""

        while self.char_atual() is not None:
            c = self.char_atual()
            if c.isupper():
                acumulador += c
                self.avancar()
            else:
                break

        if acumulador in KEYWORDS:
            self.emitir(KEYWORDS[acumulador], acumulador, coluna_inicio)
        else:
            self.emitir(TipoToken.MEM_ID, acumulador, coluna_inicio)

    def parseExpressao(self, linha, linha_num=1):
        self.tokens = []
        self.pos = 0
        self.linha_num = linha_num
        self.texto = linha
        self.estado_inicial()
        return self.tokens


def parseExpressao(linha, linha_num=1):
    lexer = AnalisadorLexico()
    return lexer.parseExpressao(linha, linha_num)


def analisar_programa(linhas):
    todos_tokens = []
    for i, linha in enumerate(linhas, 1):
        tokens = parseExpressao(linha, linha_num=i)
        todos_tokens.extend(tokens)
    todos_tokens.append(Token(TipoToken.EOF, "$", len(linhas), 0))
    return todos_tokens
