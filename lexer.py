# Aluno: Gabriel Almeida Fontes - lightlord77
# Grupo: RA1 1
# Disciplina: Linguagens Formais e Autômatos - PUCPR 2026-1
# Professor: Frank de Alcantara

from enum import Enum, auto
from dataclasses import dataclass


# === Definição dos tipos de token ===

class TipoToken(Enum):
    NUMBER = auto()
    OPERATOR = auto()
    INTDIV = auto()
    LPAREN = auto()
    RPAREN = auto()
    KW_RES = auto()
    MEM_ID = auto()
    EOF = auto()


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


# === Analisador Léxico (AFD com estados como funções) ===

class ErroLexico(Exception):
    def __init__(self, mensagem, linha, coluna):
        self.mensagem = mensagem
        self.linha = linha
        self.coluna = coluna
        super().__init__(f"Erro léxico na linha {linha}, coluna {coluna}: {mensagem}")


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

    # === ESTADOS DO AUTÔMATO (cada função = um estado) ===

    def estado_inicial(self):
        # Estado q0: decide a transição com base no caractere atual
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
            elif c == '/':
                self.estado_barra(col)
            elif c in ('+', '-', '*', '%', '^'):
                self.emitir(TipoToken.OPERATOR, c, col)
                self.avancar()
            elif c.isupper():
                self.estado_identificador(col)
            elif c == '\n' or c == '\r':
                self.avancar()
            else:
                raise ErroLexico(f"Caractere inesperado: '{c}'", self.linha_num, col)

    def estado_numero(self, coluna_inicio):
        # Estado q1: lê parte inteira, transiciona para q1b se encontrar '.'
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
                    f"Número malformado (dois pontos decimais): '{acumulador}.'",
                    self.linha_num, coluna_inicio
                )
            else:
                break

        if acumulador:
            self.emitir(TipoToken.NUMBER, acumulador, coluna_inicio)

    def estado_decimal(self, acumulador, coluna_inicio):
        # Estado q1b: lê dígitos após o ponto decimal
        tem_digito_decimal = False

        while self.char_atual() is not None:
            c = self.char_atual()

            if c.isdigit():
                acumulador += c
                tem_digito_decimal = True
                self.avancar()
            elif c == '.':
                raise ErroLexico(
                    f"Número malformado (ponto extra): '{acumulador}.'",
                    self.linha_num, coluna_inicio
                )
            else:
                break

        if not tem_digito_decimal:
            raise ErroLexico(
                f"Número malformado (nada após o ponto): '{acumulador}'",
                self.linha_num, coluna_inicio
            )

        self.emitir(TipoToken.NUMBER, acumulador, coluna_inicio)

    def estado_barra(self, coluna_inicio):
        # Estado q5: leu '/', verifica se é '/' ou '//'
        self.avancar()

        if self.char_atual() == '/':
            self.avancar()
            self.emitir(TipoToken.INTDIV, '//', coluna_inicio)
        else:
            self.emitir(TipoToken.OPERATOR, '/', coluna_inicio)

    def estado_identificador(self, coluna_inicio):
        # Estado q3: acumula letras maiúsculas, classifica RES ou MEM_ID
        acumulador = ""

        while self.char_atual() is not None:
            c = self.char_atual()
            if c.isupper():
                acumulador += c
                self.avancar()
            else:
                break

        if acumulador == "RES":
            self.emitir(TipoToken.KW_RES, "RES", coluna_inicio)
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
