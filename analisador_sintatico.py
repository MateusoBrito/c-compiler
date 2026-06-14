class Parser:
    def __init__(self, tokens):
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

    def sincronizar(self, tokens_sincronizacao=[';']):
        while self.token_atual:
            if self.token_atual['token'] in tokens_sincronizacao:
                self.proximo_token()
                return
            self.proximo_token()

    def erro(self, mensagem, sincronizacao=[';']):
        linha = self.token_atual['linha'] if self.token_atual else '?'
        coluna = self.token_atual['coluna'] if self.token_atual else '?'
        print(f"Erro Sintático na linha: {linha} | coluna: {coluna} {mensagem}")
        self.sincronizar(sincronizacao)

    def eat(self, classe_esperada, token_esperado=None):
        if not self.token_atual:
            self.erro("Fim inesperado do arquivo")
            return False
        if self.token_atual['classe'] != classe_esperada:
            self.erro(f"Esperado classe {classe_esperada}, encontrado {self.token_atual['classe']}")
            return False
        if token_esperado and self.token_atual['token'] != token_esperado:
            self.erro(f"Esperado '{token_esperado}', encontrado '{self.token_atual['token']}'")
            return False
        self.proximo_token()
        return True

    def parse_condicao(self):
        try:
            self.eat('PALAVRA_RESERVADA')  # if
            self.eat('SEPARADOR', token_esperado='(')
            self.parse_expressao()
            self.eat('SEPARADOR', token_esperado=')')
            self.eat('SEPARADOR', token_esperado='{')
            self.parse_bloco()
            self.eat('SEPARADOR', token_esperado='}')

            if self.token_atual and self.token_atual['token'] == 'else':
                self.eat('PALAVRA_RESERVADA', token_esperado='else')
                if self.token_atual and self.token_atual['token'] == 'if':
                    self.parse_condicao()
                else:
                    self.eat('SEPARADOR', token_esperado='{')
                    self.parse_bloco()
                    self.eat('SEPARADOR', token_esperado='}')
        except Exception as e:
            self.erro(str(e), ['}'])

    def parse_repeticao(self):
        try:
            if self.token_atual['token'] == 'for':
                self.eat('PALAVRA_RESERVADA')  # for
                self.eat('SEPARADOR', token_esperado='(')
                self.parse_declaracao()        # int i = 0;
                self.parse_expressao()         # i < 10
                self.eat('SEPARADOR', token_esperado=';')
                self.parse_expressao()         # i++ 
                self.eat('SEPARADOR', token_esperado=')')
                self.eat('SEPARADOR', token_esperado='{')
                self.parse_bloco()
                self.eat('SEPARADOR', token_esperado='}')

            elif self.token_atual['token'] == 'while':
                self.eat('PALAVRA_RESERVADA')  # while
                self.eat('SEPARADOR', token_esperado='(')
                self.parse_expressao()
                self.eat('SEPARADOR', token_esperado=')')
                self.eat('SEPARADOR', token_esperado='{')
                self.parse_bloco()
                self.eat('SEPARADOR', token_esperado='}')
        except Exception as e:
            self.erro(str(e), ['}'])

    def parse_parametros(self):
        if self.token_atual and self.token_atual['token'] != ')':
            self.eat('PALAVRA_RESERVADA')  # tipo: int, float, char...
            self.eat('IDENTIFICADOR')      # nome do parâmetro
            while self.token_atual and self.token_atual['token'] == ',':
                self.eat('SEPARADOR', token_esperado=',')
                self.eat('PALAVRA_RESERVADA')
                self.eat('IDENTIFICADOR')

    def parse_declaracao(self):
        self.eat('PALAVRA_RESERVADA')  # int / float / char / void
        self.eat('IDENTIFICADOR')      # nome da variável ou função

        if self.token_atual and self.token_atual['token'] == ';':
            self.eat('SEPARADOR', token_esperado=';')

        elif self.token_atual and self.token_atual['token'] == '=':
            self.eat('OPERADOR', token_esperado='=')
            self.parse_expressao()
            self.eat('SEPARADOR', token_esperado=';')

        elif self.token_atual and self.token_atual['token'] == '(':
            self.eat('SEPARADOR', token_esperado='(')
            self.parse_parametros()
            self.eat('SEPARADOR', token_esperado=')')
            self.eat('SEPARADOR', token_esperado='{')
            self.parse_bloco()
            self.eat('SEPARADOR', token_esperado='}')

    def parse_expressao(self):
        if self.token_atual and self.token_atual['token'] == '(':
            self.eat('SEPARADOR', token_esperado='(')
            self.parse_expressao()
            self.eat('SEPARADOR', token_esperado=')')

        elif self.token_atual and self.token_atual['classe'] == 'NUMERAL':
            self.eat('NUMERAL')

        elif self.token_atual and self.token_atual['classe'] == 'IDENTIFICADOR':
            self.eat('IDENTIFICADOR')
            if self.token_atual and self.token_atual['token'] in ('++', '--'):
                self.eat('OPERADOR')
                return 

        elif self.token_atual and self.token_atual['classe'] == 'LITERAL':
            self.eat('LITERAL')

        else:
            self.erro(
                f"Início de expressão inválido: "
                f"'{self.token_atual['token'] if self.token_atual else 'EOF'}'"
            )
            return

        operadores_binarios = ['+', '-', '*', '/', '==', '!=', '<', '>', '<=', '>=']
        if (
            self.token_atual
            and self.token_atual['classe'] == 'OPERADOR'
            and self.token_atual['token'] in operadores_binarios
        ):
            self.eat('OPERADOR')
            self.parse_expressao()

    def parse_atribuicao(self):
        self.eat('IDENTIFICADOR')

        operadores_atribuicao = ['=', '+=', '-=', '*=', '/=']

        if self.token_atual and self.token_atual['token'] in operadores_atribuicao:
            self.eat('OPERADOR')
            self.parse_expressao()
            self.eat('SEPARADOR', token_esperado=';')

        elif self.token_atual and self.token_atual['token'] in ('++', '--'):
            self.eat('OPERADOR')
            self.eat('SEPARADOR', token_esperado=';')

        elif self.token_atual and self.token_atual['token'] == '(':
            # Chamada de função como statement: printf("Oi\n");
            self.eat('SEPARADOR', token_esperado='(')
            if self.token_atual and self.token_atual['token'] != ')':
                self.parse_expressao()
                while self.token_atual and self.token_atual['token'] == ',':
                    self.eat('SEPARADOR', token_esperado=',')
                    self.parse_expressao()
            self.eat('SEPARADOR', token_esperado=')')
            self.eat('SEPARADOR', token_esperado=';')

        else:
            self.erro("Esperado '=', operador de atribuição, '++', '--' ou '(' após identificador")

    def parse_retorno(self):
        self.eat('PALAVRA_RESERVADA', token_esperado='return')
        self.parse_expressao()
        self.eat('SEPARADOR', token_esperado=';')

    def parse_bloco(self):
        while self.token_atual and self.token_atual['token'] != '}':
            token = self.token_atual['token']
            classe = self.token_atual['classe']

            if token == 'if':
                self.parse_condicao()
            elif token in ('for', 'while'):
                self.parse_repeticao()
            elif token in ('int', 'float', 'char', 'void'):
                self.parse_declaracao()
            elif token == 'return':
                self.parse_retorno()
            elif classe == 'IDENTIFICADOR':
                self.parse_atribuicao()
            else:
                self.erro(f"Comando não reconhecido '{token}'")

    def parse_programa(self):
        while self.token_atual:
            try:
                self.parse_declaracao()
            except Exception as e:
                self.erro(str(e))