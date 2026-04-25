# Documentacao - Fase 2: Analisador Sintatico LL(1)

## 1. Gramatica LL(1) (EBNF)

Convencao: minusculas = nao-terminais, MAIUSCULAS = terminais.

```
programa       → LPAREN KW_START RPAREN lista_cmd LPAREN KW_END RPAREN

lista_cmd      → comando lista_cmd
               | ε

comando        → LPAREN corpo RPAREN

corpo          → KW_IF expr_cmp KW_THEN lista_cmd resto_if
               | KW_WHILE expr_cmp KW_DO lista_cmd KW_ENDWHILE
               | NUMBER pos_numero
               | MEM_ID
               | LPAREN corpo RPAREN pos_subexpr

resto_if       → KW_ELSE lista_cmd KW_ENDIF
               | KW_ENDIF

pos_numero     → KW_RES
               | MEM_ID
               | operando OPERATOR [MEM_ID]
               | operando COMP_OP [MEM_ID]

pos_subexpr    → operando OPERATOR [MEM_ID]
               | operando COMP_OP [MEM_ID]
               | MEM_ID
               | OPERATOR [MEM_ID]
               | COMP_OP [MEM_ID]
               | ε

operando       → NUMBER
               | LPAREN corpo RPAREN

expr_cmp       → LPAREN operando operando COMP_OP RPAREN
```

## 2. Terminais

| Token       | Descricao                                  |
|-------------|-------------------------------------------|
| LPAREN      | Parentese de abertura `(`                 |
| RPAREN      | Parentese de fechamento `)`               |
| NUMBER      | Numero inteiro ou real (ex: `42`, `3.14`) |
| OPERATOR    | Operadores `+`, `-`, `*`, `|`, `/`, `%`, `^` |
| COMP_OP     | Operadores de comparacao `>`, `<`, `==`, `!=`, `>=`, `<=` |
| MEM_ID      | Identificador de memoria (letras maiusculas) |
| KW_RES      | Palavra-chave `RES`                       |
| KW_IF       | Palavra-chave `IF`                        |
| KW_THEN     | Palavra-chave `THEN`                      |
| KW_ELSE     | Palavra-chave `ELSE`                      |
| KW_ENDIF    | Palavra-chave `ENDIF`                     |
| KW_WHILE    | Palavra-chave `WHILE`                     |
| KW_DO       | Palavra-chave `DO`                        |
| KW_ENDWHILE | Palavra-chave `ENDWHILE`                  |
| KW_START    | Palavra-chave `START`                     |
| KW_END      | Palavra-chave `END`                       |
| EOF         | Fim da entrada                            |

## 3. Conjuntos FIRST

| Nao-terminal  | FIRST                                    |
|---------------|------------------------------------------|
| programa      | { LPAREN }                               |
| lista_cmd     | { LPAREN, ε }                            |
| comando       | { LPAREN }                               |
| corpo         | { KW_IF, KW_WHILE, NUMBER, MEM_ID, LPAREN } |
| resto_if      | { KW_ELSE, KW_ENDIF }                   |
| pos_numero    | { KW_RES, MEM_ID, NUMBER, LPAREN }      |
| pos_subexpr   | { NUMBER, LPAREN, MEM_ID, OPERATOR, COMP_OP, ε } |
| operando      | { NUMBER, LPAREN }                       |
| expr_cmp      | { LPAREN }                               |

## 4. Conjuntos FOLLOW

| Nao-terminal  | FOLLOW                                   |
|---------------|------------------------------------------|
| programa      | { EOF }                                  |
| lista_cmd     | { LPAREN, KW_ELSE, KW_ENDIF, KW_ENDWHILE } |
| comando       | { LPAREN, KW_ELSE, KW_ENDIF, KW_ENDWHILE } |
| corpo         | { RPAREN }                               |
| resto_if      | { RPAREN }                               |
| pos_numero    | { RPAREN }                               |
| pos_subexpr   | { RPAREN }                               |
| operando      | { OPERATOR, COMP_OP, NUMBER, LPAREN }    |
| expr_cmp      | { KW_THEN, KW_DO }                      |

## 5. Tabela de Analise LL(1)

| Nao-terminal | LPAREN | NUMBER | MEM_ID | KW_IF | KW_WHILE | KW_RES | KW_ELSE | KW_ENDIF | KW_ENDWHILE | OPERATOR | COMP_OP | RPAREN |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| programa | prog→LP START RP lista LP END RP | | | | | | | | | | | |
| lista_cmd | lista→cmd lista | | | | | | lista→ε | lista→ε | lista→ε | | | |
| comando | cmd→LP corpo RP | | | | | | | | | | | |
| corpo | corpo→LP corpo RP pos_sub | corpo→NUM pos_num | corpo→MEM_ID | corpo→IF... | corpo→WHILE... | | | | | | | |
| resto_if | | | | | | | resto→ELSE lista ENDIF | resto→ENDIF | | | | |
| pos_numero | pos→op OP | pos→op OP | pos→MEM_ID | | | pos→KW_RES | | | | pos→op OP | pos→op CMP | |
| pos_subexpr | pos→op OP | pos→op OP | pos→MEM_ID | | | | | | | pos→OP | pos→CMP | pos→ε |
| operando | op→LP corpo RP | op→NUMBER | | | | | | | | | | |
| expr_cmp | expr→LP op op CMP RP | | | | | | | | | | | |

## 6. Sintaxe das Estruturas de Controle

### 6.1 Tomada de Decisao (IF/ELSE)

```
(IF (condicao) THEN
    comandos_se_verdadeiro
ENDIF)

(IF (condicao) THEN
    comandos_se_verdadeiro
ELSE
    comandos_se_falso
ENDIF)
```

A condicao deve ser uma expressao de comparacao em RPN: `(A B op_cmp)`, onde `op_cmp` pode ser `>`, `<`, `==`, `!=`, `>=`, `<=`.

Exemplo:
```
(IF ((X) 10.0 >) THEN
    ((X) 2.0 |)
ELSE
    ((X) 3.0 +)
ENDIF)
```

### 6.2 Laco de Repeticao (WHILE)

```
(WHILE (condicao) DO
    comandos_do_corpo
ENDWHILE)
```

Exemplo:
```
(WHILE ((I) 10.0 <) DO
    ((I) 1.0 + I)
ENDWHILE)
```

### 6.3 Operadores de Comparacao

| Operador | Significado        |
|----------|--------------------|
| `>`      | Maior que          |
| `<`      | Menor que          |
| `==`     | Igual a            |
| `!=`     | Diferente de       |
| `>=`     | Maior ou igual a   |
| `<=`     | Menor ou igual a   |

O resultado da comparacao e 1.0 (verdadeiro) ou 0.0 (falso).

## 7. Arvore Sintatica

A arvore sintatica e representada como uma estrutura hierarquica com nos do tipo:

| Tipo do No    | Descricao                                  |
|---------------|-------------------------------------------|
| `programa`    | No raiz, filhos sao os comandos           |
| `expr_bin`    | Expressao binaria, valor = operador       |
| `expr_cmp`    | Expressao de comparacao, valor = operador |
| `number`      | Literal numerico, valor = string do numero|
| `mem_store`   | Armazenamento em memoria, valor = nome    |
| `mem_load`    | Leitura de memoria, valor = nome          |
| `res`         | Referencia a resultado anterior, valor = N|
| `if`          | Condicional sem else                      |
| `if_else`     | Condicional com else                      |
| `while`       | Laco de repeticao                         |
| `bloco_then`  | Bloco de comandos do then                 |
| `bloco_else`  | Bloco de comandos do else                 |
| `bloco_do`    | Bloco de comandos do while                |

A arvore e salva em formato JSON (`arvore_sintatica.json`) e tambem exibida em formato texto indentado no terminal.

## 8. Arvore Sintatica da Ultima Execucao (teste3.txt)

```
programa
  mem_store: GRAVIDADE
    number: 9.81
  mem_store: MASSA
    number: 72.0
  expr_bin: *
    mem_load: MASSA
    mem_load: GRAVIDADE
  res: 1
  mem_store: SALDO
    number: 100.0
  if_else
    expr_cmp: >=
      mem_load: SALDO
      number: 50.0
    bloco_then
      mem_store: SALDO
        expr_bin: -
          mem_load: SALDO
          number: 50.0
    bloco_else
      mem_store: SALDO
        number: 0.0
  mem_load: SALDO
  mem_store: CONT
    number: 1.0
  while
    expr_cmp: <
      mem_load: CONT
      number: 3.0
    bloco_do
      mem_store: CONT
        expr_bin: *
          mem_load: CONT
          mem_load: CONT
      mem_store: CONT
        expr_bin: +
          mem_load: CONT
          number: 1.0
  mem_load: CONT
  expr_bin: +
    expr_bin: ^
      number: 2.5
      expr_bin: -
        number: 4.0
        number: 1.0
    number: 10.0
  expr_bin: /
    number: 45
    number: 7
```
