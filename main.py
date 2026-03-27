# Aluno: Gabriel Almeida Fontes - lightlord77
# Grupo: RA1 1
# Disciplina: Linguagens Formais e Autômatos - PUCPR 2026-1
# Professor: Frank de Alcantara

import sys
import json
from lexer import parseExpressao, ErroLexico, Token
from gerador_assembly import gerarAssembly


def lerArquivo(nomeArquivo):
    try:
        with open(nomeArquivo, 'r', encoding='utf-8') as f:
            linhas = [linha.strip() for linha in f.readlines()]
            linhas = [l for l in linhas if l]
            return linhas
    except FileNotFoundError:
        print(f"Erro: arquivo '{nomeArquivo}' não encontrado.")
        sys.exit(1)
    except IOError as e:
        print(f"Erro ao ler arquivo: {e}")
        sys.exit(1)


def executarExpressao(tokens_por_linha, resultados, memoria):
    # Validação interna — os cálculos reais são feitos pelo Assembly
    pass


def exibirResultados(resultados):
    print("\n--- Resultados ---")
    for i, res in enumerate(resultados, 1):
        if res is not None:
            if isinstance(res, float):
                print(f"Linha {i}: {res:.1f}")
            else:
                print(f"Linha {i}: {res}")
        else:
            print(f"Linha {i}: (sem resultado)")


def salvar_tokens(tokens_por_linha, caminho="tokens_output.json"):
    dados = []
    for linha_tokens in tokens_por_linha:
        dados.append([t.to_dict() for t in linha_tokens])

    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

    print(f"Tokens salvos em: {caminho}")


def main():
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} <arquivo_teste.txt>")
        sys.exit(1)

    nome_arquivo = sys.argv[1]

    linhas = lerArquivo(nome_arquivo)
    print(f"Arquivo '{nome_arquivo}' lido: {len(linhas)} linhas")

    tokens_por_linha = []
    for i, linha in enumerate(linhas, 1):
        try:
            tokens = parseExpressao(linha, linha_num=i)
            tokens_por_linha.append(tokens)
            print(f"  Linha {i}: {len(tokens)} tokens → {tokens}")
        except ErroLexico as e:
            print(f"  ERRO na linha {i}: {e}")
            tokens_por_linha.append([])

    salvar_tokens(tokens_por_linha)

    codigo_assembly = gerarAssembly(tokens_por_linha)
    with open("output.s", 'w') as f:
        f.write(codigo_assembly)
    print(f"Assembly gerado em: output.s ({len(codigo_assembly.splitlines())} linhas)")


if __name__ == "__main__":
    main()
