import re
import string as str

SEPARADORES = ["    ","\n","(",")","{","}"," "]
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

    while batedor < len(file):
        c = file[batedor]

        token = ""
        token += c
    
        delimitador = None

        if (classe == "IDENTIFICADOR" and c in SEPARADORES or c in OPERADORES 
            or classe == "PALAVRAS_RESERVADAS" and c in SEPARADORES or c in OPERADORES
            or classe == "NUMERAL" and c in OPERADORES
            or classe == "SEPARADOR" and c in SEPARADORES
            or classe == "LITERAL" and c in SEPARADORES
            or classe == "COMENTARIO" and c in SEPARADORES
            or classe == "OPERADOR" and c in SEPARADORES
            ): 
            
            delimitador = c


        if delimitador == None:
            if re.fullmatch(IDENTIFICADOR, token):
                classe = "IDENTIFICADOR"
            elif re.fullmatch(PALAVRAS_RESERVADAS, token):
                classe = "PALAVRAS_RESERVADAS"
            elif re.fullmatch(NUMERAL, token):
                classe = "NUMERAL"
            elif re.fullmatch(SEPARADORES, token):
                classe = "SEPARADOR"
            elif re.fullmatch(LITERAL, token):
                classe = "LITERAL"
            elif re.fullmatch(COMENTARIO, token):
                classe = "COMENTARIO"
            elif re.fullmatch(OPERADORES, token):
                classe = "OPERADOR"
        else:
            print("TOKEN ENCONTRANDO")


        batedor += 1


if __name__ == "__main__":
    main()