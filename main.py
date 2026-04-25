# Aluno: Gabriel Almeida Fontes - lightlord77
# Grupo: RA1 1
# Disciplina: Linguagens Formais e Autômatos - PUCPR 2026-1
# Professor: Frank de Alcantara

import sys
import json
from lexer import parseExpressao, ErroLexico, Token, TipoToken
from gramatica import construirGramatica
from parser_ll1 import parsear, gerarArvore, ErroSintatico
from gerador_assembly import gerarAssembly


def lerArquivo(nomeArquivo):
    try:
        with open(nomeArquivo, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Erro: arquivo '{nomeArquivo}' nao encontrado.")
        sys.exit(1)
    except IOError as e:
        print(f"Erro ao ler arquivo: {e}")
        sys.exit(1)


def lerTokens(arquivo):
    conteudo = lerArquivo(arquivo)
    linhas = conteudo.strip().split('\n')
    todos_tokens = []
    for i, linha in enumerate(linhas, 1):
        linha = linha.strip()
        if not linha:
            continue
        try:
            tokens_linha = parseExpressao(linha, linha_num=i)
            todos_tokens.extend(tokens_linha)
        except ErroLexico as e:
            print(f"  ERRO LEXICO na linha {i}: {e}")
            sys.exit(1)
    todos_tokens.append(Token(tipo=TipoToken.EOF, valor="EOF", linha=0, coluna=0))
    return todos_tokens


def salvar_tokens(tokens, caminho="tokens_output.json"):
    dados = [t.to_dict() for t in tokens if t.tipo != TipoToken.EOF]
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    print(f"Tokens salvos em: {caminho}")


def salvar_arvore(arvore, caminho="arvore_sintatica.json"):
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(arvore.to_dict(), f, indent=2, ensure_ascii=False)
    print(f"Arvore sintatica salva em: {caminho}")


def main():
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} <arquivo_teste.txt>")
        sys.exit(1)

    nome_arquivo = sys.argv[1]
    print(f"=== Analisador Sintatico LL(1) ===")
    print(f"Arquivo: {nome_arquivo}")
    print()

    print("--- Analise Lexica ---")
    tokens = lerTokens(nome_arquivo)
    print(f"Total de tokens: {len(tokens) - 1}")
    salvar_tokens(tokens)
    print()

    print("--- Gramatica LL(1) ---")
    info_gramatica = construirGramatica()
    print(f"Nao-terminais: {len(info_gramatica['nao_terminais'])}")
    print(f"Terminais: {len(info_gramatica['terminais'])}")
    print()

    print("--- Analise Sintatica ---")
    try:
        arvore = parsear(tokens, info_gramatica['tabela'])
        print("Analise sintatica concluida com sucesso!")
        print()
        print("--- Arvore Sintatica ---")
        print(arvore.to_texto())
        salvar_arvore(arvore)
    except ErroSintatico as e:
        print(f"ERRO SINTATICO: {e}")
        sys.exit(1)

    print("--- Geracao de Assembly ---")
    codigo_assembly = gerarAssembly(arvore)
    with open("output.s", 'w') as f:
        f.write(codigo_assembly)
    print(f"Assembly gerado em: output.s ({len(codigo_assembly.splitlines())} linhas)")


if __name__ == "__main__":
    main()
