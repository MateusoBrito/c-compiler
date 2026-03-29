import re
import sys
import csv

IDENTIFICADOR = r"[A-Za-z_][A-Za-z0-9_]*"
PALAVRA_RESERVADA = r"^(for|int|float|if|while)$" 
OPERADOR = r"(\+\+|--|\+=|-=|\*=|/=|==|!=|>=|<=|>|<|\+|-|\*|/|=|&&|\|\|)"
LITERAL = r"(\"[^\"]*\"|'[^']*')"
COMENTARIO = r"(//[^\n]*|/\*[\s\S]*?\*/)"
SEPARADOR = r"[()\{\};]"
NUMERAL = r"[0-9]+"

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 analisador_lexico.py <nome_do_arquivo.c>")
        return
    file_path = sys.argv[1]
    try:
        with open(file_path, "r") as f:
            file = f.read() 
    except FileNotFoundError:
        print(f"Erro: O arquivo '{file_path}' não foi encontrado.")
        return
    
    batedor = 0
    classe = None
    lista_tokens = []
    linhas = 1
    colunas = 1
    token = ""

    while batedor < len(file):
        c = file[batedor]
        
        if c.isspace() and token == "":
            if c == '\n':
                linhas += 1
                colunas = 0
            batedor += 1
            colunas += 1
            continue

        proximo = token + c
        achou_classe = None

        if re.fullmatch(PALAVRA_RESERVADA, proximo): achou_classe = "PALAVRA_RESERVADA"
        elif re.fullmatch(NUMERAL, proximo): achou_classe = "NUMERAL"
        elif re.fullmatch(SEPARADOR, proximo): achou_classe = "SEPARADOR"
        elif re.fullmatch(OPERADOR, proximo): achou_classe = "OPERADOR"
        elif re.fullmatch(IDENTIFICADOR, proximo): achou_classe = "IDENTIFICADOR"
        elif re.fullmatch(LITERAL, proximo): achou_classe = "LITERAL"
        elif re.fullmatch(COMENTARIO, proximo): achou_classe = "COMENTARIO"
        
        if not achou_classe and not classe:
            if proximo.startswith('"') or proximo.startswith("'") or proximo.startswith('/'):
                achou_classe = "INTERMEDIARIO"

        if achou_classe:
            if achou_classe != "INTERMEDIARIO":
                classe = achou_classe
            token += c
            batedor += 1
            colunas += 1
        else:
            is_space = c.isspace()
            is_sep_or_op = c in SEPARADOR or c in "+-*/=<>!&|"
            
            if classe and (
                (classe == "IDENTIFICADOR" and (is_sep_or_op or is_space)) or
                (classe == "PALAVRA_RESERVADA" and (is_sep_or_op or is_space)) or
                (classe == "NUMERAL" and (is_sep_or_op or is_space)) or
                (classe == "LITERAL") or
                (classe == "OPERADOR") or 
                (classe == "COMENTARIO") or
                (classe == "SEPARADOR")
            ):
                lista_tokens.append([token, classe, linhas, colunas - len(token)])
                token = ""
                classe = None
            else:
                print(f"Erro léxico na linha {linhas} e coluna {colunas}: {c}")
                batedor += 1
                colunas += 1

    if classe == "SEPARADOR": lista_tokens.append([token, classe, linhas, colunas - len(token)])
    
    with open("tokens.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["token", "classe", "linha", "coluna"])
        writer.writerows(lista_tokens)

if __name__ == "__main__":
    main()