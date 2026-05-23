class Parser:
    def __init__(self,tokens):
        """Tokens é uma lista de tokens gerados pelo analisador léxico"""
        self.tokens = tokens
        self.pos = 0
        self.token_atual = self.tokens[self.pos] if tokens else None

    def proximo_token(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.token_atual = self.tokens[self.pos]

            if self.token_atual['classe'] == 'COMENTARIO':
                self.proximo_token()

        else:
            self.token_atual = None

    def eat(self, classe_esperada, token_esperado=None):
        """
        Consome o token se for da classe esperada.
        Se 'token_esperado' for informado, valida também o texto exato.
        """
        if self.token_atual and self.token_atual['classe'] == classe_esperada:
            if token_esperado and self.token_atual['token'] != token_esperado:
                raise Exception(f"Erro Sintático na linha {self.token_atual['linha']}: "
                                f"Esperado '{token_esperado}', encontrado '{self.token_atual['token']}'")
            
            self.proximo_token()
        else:
            raise Exception(f"Erro Sintático: Esperado classe {classe_esperada}, "
                            f"encontrado {self.token_atual['classe']} na linha {self.token_atual['linha']}")
    
    #TODO comandos sem {}
    #TODO tratamento de erro

    """
    E -> BE'
    E' -> C | D
    C -> E
    D -> A
    """
    def parse_condicao(self):
        self.eat('PALAVRA_RESERVADA') 
        self.eat('SEPARADOR', token_esperado='(')
        self.parse_expressao()
        self.eat('SEPARADOR', token_esperado=')') 
        self.eat('SEPARADOR', token_esperado='{')
        self.parse_bloco()
        self.eat('SEPARADOR', token_esperado='}')

        if self.token_atual['token'] == 'else':
            self.eat('PALAVRA_RESERVADA', token_esperado='else')
            if self.token_atual['token'] == 'if':
                self.parse_condicao()
            else:
                self.eat('SEPARADOR', token_esperado='{')
                self.parse_bloco()
                self.eat('SEPARADOR', token_esperado='}')
        

    def parse_repeticao(self):
        if self.token_atual['token'] == 'for':
            self.eat('PALAVRA_RESERVADA') 
            self.eat('SEPARADOR', token_esperado='(')
            self.parse_declaracao()
            self.parse_expressao()
            self.eat('SEPARADOR', token_esperado=';')
            self.parse_expressao()
            self.eat('SEPARADOR', token_esperado=')') 
            self.eat('SEPARADOR', token_esperado='{')
            self.parse_bloco()
            self.eat('SEPARADOR', token_esperado='}')
        elif self.token_atual['token'] == 'while':
            self.eat('PALAVRA_RESERVADA') 
            self.eat('SEPARADOR', token_esperado='(')
            self.parse_expressao()
            self.eat('SEPARADOR', token_esperado=')') 
            self.eat('SEPARADOR', token_esperado='{')
            self.parse_bloco()
            self.eat('SEPARADOR', token_esperado='}')

    def parse_parametros(self):
        # Verifica se não é uma função vazia ex: main()
        if self.token_atual and self.token_atual['token'] != ')':
            # Lê o primeiro parâmetro
            self.eat('PALAVRA_RESERVADA') # Ex: int
            self.eat('IDENTIFICADOR')     # Ex: a
            
            # Se tiver vírgula, lê os próximos
            while self.token_atual and self.token_atual['token'] == ',':
                self.eat('SEPARADOR', token_esperado=',')
                self.eat('PALAVRA_RESERVADA')
                self.eat('IDENTIFICADOR')

    def parse_declaracao(self):
        self.eat('PALAVRA_RESERVADA')
        self.eat('IDENTIFICADOR')
        
        # Se for apenas declaração sem inicialização: int x;
        if self.token_atual['token'] == ';':
            self.eat('SEPARADOR', token_esperado=';')
        
        # Se for apenas declaração com atribuição: int x = 10;
        elif self.token_atual['token'] == '=':
            self.eat('OPERADOR', token_esperado='=')
            self.parse_expressao()
            self.eat('SEPARADOR', token_esperado=';')
        
        elif self.token_atual['token'] == '(':
            self.eat('SEPARADOR', token_esperado='(')
            if self.token_atual['token'] != ')':
                self.parse_parametros()
            self.eat('SEPARADOR', token_esperado=')')
            self.eat('SEPARADOR', token_esperado='{')
            self.parse_bloco()
            self.eat('SEPARADOR', token_esperado='}')
    
    def parse_expressao(self):
        # Uma expressão simples pode começar com número ou variável
        if self.token_atual['token'] == '(':
            self.eat('SEPARADOR', token_esperado='(')
            self.parse_expressao()
            self.eat('SEPARADOR', token_esperado=')')

        elif self.token_atual['classe'] == 'NUMERAL':
            self.eat('NUMERAL')

        elif self.token_atual['classe'] == 'IDENTIFICADOR':
            self.eat('IDENTIFICADOR')
        
        elif self.token_atual['classe'] == 'LITERAL':
            self.eat('LITERAL')

        else:
            raise Exception(f"Erro Sintático na linha {self.token_atual['linha']}: "
                            f"Início de expressão inválido: '{self.token_atual['token']}'")

        # Verifica se ainda temos tokens e se o próximo é um operador matemático (e não um '=' de atribuição)
        if self.token_atual and self.token_atual['classe'] == 'OPERADOR' and self.token_atual['token'] != '=':
            self.eat('OPERADOR')
            self.parse_expressao() # Continua a cadeia da expressão
    
    def parse_parametros(self):
        # Verifica se não é uma função vazia ex: main()
        if self.token_atual and self.token_atual['token'] != ')':
            # Lê o primeiro parâmetro
            self.eat('PALAVRA_RESERVADA') # Ex: int
            self.eat('IDENTIFICADOR')     # Ex: a
            
            # Se tiver vírgula, lê os próximos
            while self.token_atual and self.token_atual['token'] == ',':
                self.eat('SEPARADOR', token_esperado=',')
                self.eat('PALAVRA_RESERVADA')
                self.eat('IDENTIFICADOR')

    def parse_atribuicao(self):
        self.eat('IDENTIFICADOR')     

        if self.token_atual['token'] == '=':
            # Cenário 1: É uma atribuição pura (ex: x = 5;)
            self.eat('OPERADOR', token_esperado='=')
            self.parse_expressao()
            self.eat('SEPARADOR', token_esperado=';')
            
        elif self.token_atual['token'] == '(':
            # Cenário 2: É uma chamada de função! (ex: printf("Oi"); )
            self.eat('SEPARADOR', token_esperado='(')
            
            # Verifica se tem argumentos dentro dos parênteses (Expressões)
            if self.token_atual['token'] != ')':
                self.parse_expressao() # Lê o primeiro argumento
                
                # Se tiver vírgula, tem mais argumentos (ex: soma(a, b))
                while self.token_atual and self.token_atual['token'] == ',':
                    self.eat('SEPARADOR', token_esperado=',')
                    self.parse_expressao()
                    
            self.eat('SEPARADOR', token_esperado=')')
            self.eat('SEPARADOR', token_esperado=';')
            
        else:
            raise Exception(f"Erro Sintático na linha {self.token_atual['linha']}: Esperado '=' ou '(' após identificador")
    
    def parse_retorno(self):
        """Lida com o comando: return 0; ou return x + 5;"""
        self.eat('PALAVRA_RESERVADA', token_esperado='return')
        self.parse_expressao()
        self.eat('SEPARADOR', token_esperado=';')

    def parse_bloco(self):
        while self.token_atual and self.token_atual['token'] != '}':
            token = self.token_atual['token']
            classe = self.token_atual['classe']

            # 1. Condições (if)
            if token in ['if']:
                self.parse_condicao()
                
            # 2. Repetições (for, while)
            elif token in ['for','while']:
                self.parse_repeticao()
                
            # 3. Declarações de variáveis (int, float, char)
            elif token in ['int','float','char']:
                self.parse_declaracao()
            
            # 4. return (ex: return 0;)
            elif token == 'return':
                self.parse_retorno()

            # 5. Atribuição direta (ex: x = 10;) ou chamadas
            elif classe == 'IDENTIFICADOR':
                self.parse_atribuicao()

            # 6. Tratamento de erro 
            else:
                raise Exception(f"Erro Sintático na linha {self.token_atual['linha']}: "
                                f"Comando não reconhecido '{token}'.")
    
    def parse_programa(self):
        """Ponto de entrada do compilador"""
        while self.token_atual:
            self.parse_declaracao()