Compilador RPN → Assembly ARMv7

Instituição: Pontifícia Universidade Católica do Paraná (PUCPR)  
Disciplina: Linguagens Formais e Autômatos  
Professor: Frank de Alcantara  
Semestre: 2026-1  


Aluno
Gabriel Almeida Fontes - GitHub: [@lightlord77](https://github.com/lightlord77)

Grupo no Canvas: RA1 1

---


Programa que processa expressões aritméticas em notação polonesa reversa (RPN) a partir de um arquivo de texto, realiza análise léxica usando um Autômato Finito Determinístico (AFD) com estados implementados como funções, e gera código Assembly ARMv7 funcional para o simulador CPUlator DE1-SoC (v16.1).

Nenhum cálculo é realizado em Python. O código Assembly gerado é responsável por todas as operações aritméticas, utilizando instruções VFP de ponto flutuante em 64 bits (IEEE 754).





Operações Suportadas

- Adição: `(A B +)`
- Subtração: `(A B -)`
- Multiplicação: `(A B *)`
- Divisão real: `(A B /)`
- Divisão inteira: `(A B //)`
- Resto: `(A B %)`
- Potenciação: `(A B ^)` (B inteiro positivo)
- Armazenar em memória: `(V MEM)`
- Recuperar da memória: `(MEM)`
- Resultado anterior: `(N RES)`
- Expressões aninhadas sem limite









Como Executar:
	
Requisitos:

- Python 3.6 ou superior

Compilar e gerar Assembly

```bash
python main.py testes/teste1.txt
```

O programa gera dois arquivos de saída:
- `output.s` — código Assembly ARMv7
- `tokens_output.json` — tokens da análise léxica





Executar os testes do analisador léxico

```bash
python testes_lexer.py
```




Executar o Assembly no CPUlator

1. Abrir https://cpulator.01xz.net/?sys=arm-de1soc
2. Confirmar que o sistema é **ARMv7 DE1-SoC (v16.1)**
3. Colar o conteúdo de `output.s` no editor
4. Clicar em **Compile and Load (F5)**
5. Clicar em **Continue (F3)**
6. Os resultados aparecem no terminal **JTAG UART** e nos displays **HEX3-HEX0**





Detalhes Técnicos

Analisador Léxico

Implementado como AFD com cada estado sendo uma função:
- `estado_inicial` — estado q0, decide transições
- `estado_numero` — estado q1, lê parte inteira
- `estado_decimal` — estado q1b, lê parte fracionária
- `estado_barra` — estado q5, diferencia `/` de `//`
- `estado_identificador` — estado q3, reconhece MEM_ID e keyword RES

Detecta erros léxicos: caracteres inválidos, números malformados, vírgula como separador decimal.





Assembly Gerado

- Habilita VFP (coprocessadores 10/11) para ponto flutuante 64 bits
- Constantes armazenadas como IEEE 754 double na seção `.data`
- Avaliação RPN via pilha do processador (VPUSH/VPOP)
- Instruções VFP: VADD.F64, VSUB.F64, VMUL.F64, VDIV.F64
- Potenciação por loop de multiplicações
- Saída via JTAG UART (0xFF201000) e displays 7 segmentos (0xFF200020)
