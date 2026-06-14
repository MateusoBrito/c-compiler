import re
import csv
import yaml

class AnalisadorLexico:
    def __init__(self, regras_path="regras.yaml"):
        """Inicializa o Léxico carregando as regras do YAML."""
        self.rules = self.read_rules(regras_path)
        self.lista_tokens = []

    def read_rules(self, file_path):
        """Lê o arquivo YAML e retorna a lista de regras."""
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
                if data is None:
                    return []

                rules = []
                for nome_classe, propriedades in data.items():
                    propriedades['nome'] = nome_classe 
                    rules.append(propriedades)
                
                return rules
        except FileNotFoundError:
            print(f"Aviso: O arquivo de regras '{file_path}' não foi encontrado.")
            return []

    def analisar_arquivo(self, file_path):
        """Lê o arquivo fonte e dispara a análise textual."""
        try:
            with open(file_path, "r") as f:
                texto = f.read() 
        except FileNotFoundError:
            print(f"Erro: O arquivo '{file_path}' não foi encontrado.")
            return None
        
        return self.analisar_texto(texto)

    def analisar_texto(self, texto):
        """Executa a máquina de estados para gerar os tokens."""
        if not self.rules:
            print("Erro ao carregar regras.")
            return []

        linhas = 1
        colunas = 1
        batedor = 0
        classe = None
        token = ""
        self.lista_tokens = []

        while batedor < len(texto):
            c = texto[batedor]
            
            if c.isspace() and token == "":
                if c == '\n':
                    linhas += 1
                    colunas = 0
                batedor += 1
                colunas += 1
                continue

            proximo = token + c
            achou_classe = None

            for item in self.rules:
                if re.fullmatch(item['regras'], proximo):
                    achou_classe = item['nome']
                    break

            if not achou_classe:
                if not classe:
                    if proximo.startswith('"') or proximo.startswith("'") or proximo.startswith('/'):
                        achou_classe = 'INTERMEDIARIO'
                    # CORREÇÃO: + e - sozinhos ficam em INTERMEDIARIO para permitir
                    # acumular o segundo caractere e reconhecer ++ e --
                    elif proximo in ('+', '-'):
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
                        current_rule = next((r for r in self.rules if r['nome'] == classe), None)
                        
                        if current_rule and 'delimitadores' in current_rule:
                            for d_nome in current_rule['delimitadores']:
                                target_rule = next((r for r in self.rules if r['nome'] == d_nome), None)
                                if target_rule and re.fullmatch(target_rule['regras'], c):
                                    valido = True
                                    break
                        else:
                            valido = True
                
                if valido:
                    self.lista_tokens.append({
                        'token': token, 
                        'classe': classe, 
                        'linha': linhas, 
                        'coluna': colunas - len(token)
                    })
                    token = ""
                    classe = None
                else:
                    # CORREÇÃO: token em INTERMEDIARIO (ex: '+' sozinho antes de checar '++')
                    # nunca chegará aqui porque + e - são marcados como INTERMEDIARIO acima.
                    # Este bloco trata erros léxicos genuínos.
                    print(f"Erro léxico na linha {linhas} e coluna {colunas}: {proximo}")
                    token = ""
                    classe = None
                    batedor += 1
                    colunas += 1

        # Salva o último token caso o arquivo termine sem espaço no final
        if classe: 
            self.lista_tokens.append({
                'token': token, 
                'classe': classe, 
                'linha': linhas, 
                'coluna': colunas - len(token)
            })

        return self.lista_tokens

    def salvar_tokens_csv(self, output_path="tokens.csv"):
        """Gera o arquivo CSV com a saída léxica."""
        if not self.lista_tokens:
            return
            
        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["token", "classe", "linha", "coluna"])
            for t in self.lista_tokens:
                writer.writerow([t['token'], t['classe'], t['linha'], t['coluna']])