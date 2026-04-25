# Aluno: Gabriel Almeida Fontes - lightlord77
# Grupo: RA1 1
# Disciplina: Linguagens Formais e Autômatos - PUCPR 2026-1
# Professor: Frank de Alcantara

from lexer import TipoToken


def construirGramatica():
    gramatica = {
        "programa": [
            ["LPAREN", "KW_START", "RPAREN", "lista_cmd", "LPAREN", "KW_END", "RPAREN"]
        ],
        "lista_cmd": [
            ["comando", "lista_cmd"],
            []
        ],
        "comando": [
            ["LPAREN", "corpo", "RPAREN"]
        ],
        "corpo": [
            ["KW_IF", "expr_cmp", "KW_THEN", "lista_cmd", "resto_if"],
            ["KW_WHILE", "expr_cmp", "KW_DO", "lista_cmd", "KW_ENDWHILE"],
            ["NUMBER", "pos_numero"],
            ["MEM_ID"],
            ["LPAREN", "corpo", "RPAREN", "pos_subexpr"],
        ],
        "pos_subexpr": [
            ["operando", "OPERATOR"],
            ["operando", "COMP_OP"],
            ["MEM_ID"],
            ["OPERATOR"],
            ["COMP_OP"],
        ],
        "resto_if": [
            ["KW_ELSE", "lista_cmd", "KW_ENDIF"],
            ["KW_ENDIF"],
        ],
        "pos_numero": [
            ["KW_RES"],
            ["MEM_ID"],
            ["operando", "OPERATOR"],
            ["operando", "COMP_OP"],
        ],
        "operando": [
            ["NUMBER"],
            ["LPAREN", "corpo", "RPAREN"],
        ],
        "expr_cmp": [
            ["LPAREN", "operando", "operando", "COMP_OP", "RPAREN"],
        ],
    }

    terminais = {
        "LPAREN", "RPAREN", "NUMBER", "OPERATOR", "COMP_OP",
        "MEM_ID", "KW_RES", "KW_IF", "KW_THEN", "KW_ELSE",
        "KW_ENDIF", "KW_WHILE", "KW_DO", "KW_ENDWHILE",
        "KW_START", "KW_END", "EOF",
    }

    nao_terminais = set(gramatica.keys())

    first = calcularFirst(gramatica, terminais, nao_terminais)
    follow = calcularFollow(gramatica, terminais, nao_terminais, first)
    tabela = construirTabelaLL1(gramatica, terminais, nao_terminais, first, follow)

    return {
        "gramatica": gramatica,
        "terminais": terminais,
        "nao_terminais": nao_terminais,
        "first": first,
        "follow": follow,
        "tabela": tabela,
    }


def calcularFirst(gramatica, terminais, nao_terminais):
    first = {nt: set() for nt in nao_terminais}
    for t in terminais:
        first[t] = {t}

    mudou = True
    while mudou:
        mudou = False
        for nt in nao_terminais:
            for producao in gramatica[nt]:
                if not producao:
                    if "epsilon" not in first[nt]:
                        first[nt].add("epsilon")
                        mudou = True
                else:
                    for simbolo in producao:
                        if simbolo in terminais:
                            if simbolo not in first[nt]:
                                first[nt].add(simbolo)
                                mudou = True
                            break
                        elif simbolo in nao_terminais:
                            antes = len(first[nt])
                            first[nt] |= (first[simbolo] - {"epsilon"})
                            if len(first[nt]) > antes:
                                mudou = True
                            if "epsilon" not in first[simbolo]:
                                break
                        else:
                            if simbolo not in first[nt]:
                                first[nt].add(simbolo)
                                mudou = True
                            break
                    else:
                        if "epsilon" not in first[nt]:
                            first[nt].add("epsilon")
                            mudou = True
    return first


def calcularFollow(gramatica, terminais, nao_terminais, first):
    follow = {nt: set() for nt in nao_terminais}
    follow["programa"].add("EOF")

    mudou = True
    while mudou:
        mudou = False
        for nt in nao_terminais:
            for producao in gramatica[nt]:
                for i, simbolo in enumerate(producao):
                    if simbolo not in nao_terminais:
                        continue
                    resto = producao[i + 1:]
                    first_resto = set()
                    todos_epsilon = True
                    for s in resto:
                        if s in terminais:
                            first_resto.add(s)
                            todos_epsilon = False
                            break
                        elif s in nao_terminais:
                            first_resto |= (first[s] - {"epsilon"})
                            if "epsilon" not in first[s]:
                                todos_epsilon = False
                                break
                    else:
                        todos_epsilon = True

                    antes = len(follow[simbolo])
                    follow[simbolo] |= first_resto
                    if todos_epsilon:
                        follow[simbolo] |= follow[nt]
                    if len(follow[simbolo]) > antes:
                        mudou = True
    return follow


def construirTabelaLL1(gramatica, terminais, nao_terminais, first, follow):
    tabela = {}
    for nt in nao_terminais:
        tabela[nt] = {}

    for nt in nao_terminais:
        for idx, producao in enumerate(gramatica[nt]):
            first_prod = set()
            if not producao:
                first_prod.add("epsilon")
            else:
                for simbolo in producao:
                    if simbolo in terminais:
                        first_prod.add(simbolo)
                        break
                    elif simbolo in nao_terminais:
                        first_prod |= (first[simbolo] - {"epsilon"})
                        if "epsilon" not in first[simbolo]:
                            break
                    else:
                        first_prod.add(simbolo)
                        break
                else:
                    first_prod.add("epsilon")

            for terminal in first_prod:
                if terminal != "epsilon":
                    tabela[nt][terminal] = (idx, producao)

            if "epsilon" in first_prod:
                for terminal in follow[nt]:
                    if terminal not in tabela[nt]:
                        tabela[nt][terminal] = (idx, producao)

    return tabela
