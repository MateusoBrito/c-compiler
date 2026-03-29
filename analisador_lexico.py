import re
import yaml

SEPARADORES = ["    ","\n","(",")","{","}"," ",";"]
OPERADORES = ["=","+","-"]
PALAVRAS_RESERVADAS = ["for", "int", "float", "if", "while"]
NUMERAL = rf'[0-9]+'
IDENTIFICADOR = rf'[A-Za-z_].*'
COMENTARIO = r'(//.*\n|/\*.*\*/)'
LITERAL = r'(\'[^\']*\'|\"[^\"]*\")'

def main():
    with open("codigo_entrada.c", "r") as f:
        file = f.read() 
    
    pivo = 0
    batedor = 0
    classe = None

    lista_tokens = []

    linhas = 0
    colunas = 0

    token = ""

    while batedor < len(file):
        c = file[batedor]
        print(c)
        delimitador = None

        if (
            (classe == "IDENTIFICADOR" and (c in SEPARADORES or c in OPERADORES)) or
            (classe == "PALAVRA_RESERVADA" and c in SEPARADORES) or
            (classe == "NUMERAL" and (c in SEPARADORES or c in OPERADORES)) or
            (classe == "LITERAL" and (c in SEPARADORES or re.fullmatch(c,IDENTIFICADOR))) or
            (classe == "OPERADOR" and (c in SEPARADORES)) or
            (classe == "COMENTARIO") or
            (classe == "SEPARADOR")
        ):
            print("oi")
            lista_tokens.append([token,classe,linhas,pivo])
            pivo = batedor
            classe = None
            token = ""


        token += c

        #if delimitador == None:
        if re.fullmatch(IDENTIFICADOR, token):
            if token in PALAVRAS_RESERVADAS:
                classe = "PALAVRA_RESERVADA"
            else: classe = "IDENTIFICADOR"
        elif re.fullmatch(NUMERAL, token):
            classe = "NUMERAL"
        elif token in SEPARADORES:
            print("entrou")
            classe = "SEPARADOR"
        elif re.fullmatch(LITERAL, token):
            classe = "LITERAL"
        elif re.fullmatch(COMENTARIO, token):
            classe = "COMENTARIO"
        elif token in OPERADORES:
            classe = "OPERADOR"
        #else:
            #print("TOKEN ENCONTRANDO")


        batedor += 1
        if c == '\n':
            linhas += 1
            colunas = 0
        else:
            colunas += 1
    
    if classe == "SEPARADOR": lista_tokens.append([token,classe,linhas,pivo])
    print(lista_tokens)


if __name__ == "__main__":
    main()
    