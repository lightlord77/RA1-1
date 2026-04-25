# Fase 2 - Analisador Sintatico LL(1)

**Instituicao:** PUCPR - Pontificia Universidade Catolica do Parana
**Disciplina:** Linguagens Formais e Autômatos - 2026/1
**Professor:** Frank de Alcantara

## Integrantes

- Gabriel Almeida Fontes - @lightlord77

**Grupo Canvas:** RA1 1

## Descricao

Compilador para uma linguagem de programacao simplificada em notacao polonesa reversa (RPN), com:

- Analisador lexico (AFD com estados como funcoes)
- Analisador sintatico descendente recursivo LL(1)
- Geracao de arvore sintatica
- Geracao de codigo Assembly ARMv7 para CPUlator DE1-SoC v16.1

### Operacoes suportadas

| Operador | Descricao          | Exemplo         |
|----------|--------------------|-----------------|
| `+`      | Adicao             | `(A B +)`       |
| `-`      | Subtracao          | `(A B -)`       |
| `*`      | Multiplicacao      | `(A B *)`       |
| `\|`     | Divisao real       | `(A B \|)`      |
| `/`      | Divisao inteira    | `(A B /)`       |
| `%`      | Resto              | `(A B %)`       |
| `^`      | Potenciacao        | `(A B ^)`       |

### Comandos especiais

- `(V MEM)` - Armazena valor em variavel
- `(MEM)` - Recupera valor de variavel
- `(N RES)` - Recupera resultado de N linhas anteriores

### Estruturas de controle

**IF/ELSE:**
```
(IF (A B >) THEN (expressoes...) ELSE (expressoes...) ENDIF)
```

**WHILE:**
```
(WHILE (A B <) DO (expressoes...) ENDWHILE)
```

## Estrutura do Projeto

| Arquivo            | Descricao                                    |
|--------------------|----------------------------------------------|
| `main.py`          | Ponto de entrada e orquestracao              |
| `lexer.py`         | Analisador lexico (AFD)                      |
| `gramatica.py`     | Gramatica LL(1), FIRST, FOLLOW, tabela       |
| `parser_ll1.py`    | Parser descendente recursivo e arvore        |
| `gerador_assembly.py` | Gerador de Assembly ARMv7 a partir da AST |
| `testes_parser.py` | Testes do analisador sintatico               |
| `documentacao.md`  | Gramatica, FIRST/FOLLOW, tabela LL(1)        |
| `testes/`          | Arquivos de teste                            |

## Como executar

### Requisitos
- Python 3.8+

### Execucao
```bash
python main.py testes/teste1.txt
```

### Testes do parser
```bash
python testes_parser.py
```

### Execucao no CPUlator
1. Abra https://cpulator.01xz.net/?sys=arm-de1soc
2. Selecione sistema: ARMv7 DE1-SoC (v16.1)
3. Cole o conteudo de `output.s` no editor
4. Clique em Compile, depois Continue (F3)
5. Os resultados aparecem no painel JTAG UART

## Saidas do programa

- `tokens_output.json` - Tokens gerados pelo analisador lexico
- `arvore_sintatica.json` - Arvore sintatica em formato JSON
- `output.s` - Codigo Assembly ARMv7
