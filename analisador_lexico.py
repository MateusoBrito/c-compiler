import re
import sys
import csv
import yaml

def read_file():
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
    return file

def read_rules(file_path="regras.yaml"):
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
            if data is None:
                return {}

            rules = []
            for nome_classe, propriedades in data.items():
                propriedades['nome'] = nome_classe 
                rules.append(propriedades)
            
            return rules

    except FileNotFoundError:
        print(f"Aviso: O arquivo '{file_path}' não foi encontrado.")
        return {}
    
def save_tokens(lista_tokens):
    with open("tokens.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["token", "classe", "linha", "coluna"])
        writer.writerows(lista_tokens)
    

def main():
    file = read_file()
    rules = read_rules()
    if not rules:
        print("Erro ao carregar regras.")
        return


    linhas = 1
    colunas = 1
    batedor = 0

    classe = None
    token = ""
    lista_tokens = []

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

        for item in rules:
            if re.fullmatch(item['regras'], proximo):
                achou_classe = item['nome']
                break

        if not achou_classe:
            if not classe: 
                if proximo.startswith('"') or proximo.startswith("'") or proximo.startswith('/'):
                    achou_classe = 'INTERMEDIARIO'
            elif re.fullmatch(r"[0-9]+\.", proximo) or proximo == ".":
                achou_classe = 'INTERMEDIARIO'
            elif proximo.startswith('/*') and classe != 'COMENTARIO':
                achou_classe = 'INTERMEDIARIO'

        if achou_classe:
            if achou_classe != "INTERMEDIARIO":
                classe = achou_classe
            token += c
            batedor += 1
            colunas += 1
        else:
            valido = False
            if classe:
                if c.isspace():
                    valido = True
                else:
                    current_rule = next((r for r in rules if r['nome'] == classe), None)
                    
                    if current_rule and 'delimitadores' in current_rule:
                        for d_nome in current_rule['delimitadores']:
                            target_rule = next((r for r in rules if r['nome'] == d_nome), None)
                            if target_rule and re.fullmatch(target_rule['regras'], c):
                                valido = True
                                break
                    else:
                        valido = True
            
            if valido:
                lista_tokens.append([token, classe, linhas, colunas - len(token)])
                token = ""
                classe = None
            else:
                print(f"Erro léxico na linha {linhas} e coluna {colunas}: {c}")
                batedor += 1
                colunas += 1

    if classe == "SEPARADOR": lista_tokens.append([token, classe, linhas, colunas - len(token)])

    save_tokens(lista_tokens)

if __name__ == "__main__":
    main()