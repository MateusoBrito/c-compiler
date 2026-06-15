from tabela_simbolos import TabelaSimbolos

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.token_atual = self.tokens[self.pos] if tokens else None
        
        self.tabela = TabelaSimbolos()

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
        
        if "Erro Semântico" in mensagem:
            print(mensagem)
        else:
            print(f"Erro Sintático na linha {linha} | coluna {coluna}: {mensagem}")
            
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

    def parse_declaracao(self):
        tipo_var = self.token_atual['token']
        self.eat('PALAVRA_RESERVADA')  # int / float / char / void

        nome_var = self.token_atual['token']
        linha_var = self.token_atual['linha']
        self.eat('IDENTIFICADOR')      # nome da variável ou função

        self.tabela.inserir(nome_var, tipo_var, linha_var)

        if self.token_atual and self.token_atual['token'] == ';':
            self.eat('SEPARADOR', token_esperado=';')

        elif self.token_atual and self.token_atual['token'] == '=':
            self.eat('OPERADOR', token_esperado='=')
            self.parse_expressao()
            self.eat('SEPARADOR', token_esperado=';')
        
        elif self.token_atual and self.token_atual['token'] == ',':
            while self.token_atual and self.token_atual['token'] == ',':
                self.eat('SEPARADOR', token_esperado=',')
                nome_var = self.token_atual['token']
                linha_var = self.token_atual['linha']
                self.eat('IDENTIFICADOR')
                self.tabela.inserir(nome_var, tipo_var, linha_var)
            self.eat('SEPARADOR', token_esperado=';')

        elif self.token_atual and self.token_atual['token'] == '(':
            self.eat('SEPARADOR', token_esperado='(')
            if self.token_atual and self.token_atual['token'] != ')':
                self.parse_declaracao()
            self.eat('SEPARADOR', token_esperado=')')
            self.eat('SEPARADOR', token_esperado='{')
            self.parse_bloco()
            self.eat('SEPARADOR', token_esperado='}')

    def avaliar_operacao(self, tipo1,tipo2, operador):

            REGRAS_TIPO = {
                ('int', 'int'): 'int',
                ('float', 'float'): 'float',
                ('char', 'char'): 'char',
                ('int', 'float'): 'float',
                ('float', 'int'): 'float',
            }
            
            if operador in ['==', '!=', '<', '>', '<=', '>=']:
                return 'int'
            
            resultado = REGRAS_TIPO.get((tipo1, tipo2))
            if not resultado:
                raise Exception(f"Erro Semântico: Operação inválida entre '{tipo1}' e '{tipo2}'")
            return resultado

    def parse_expressao(self):
        tipo_esq = None

        if self.token_atual and self.token_atual['token'] == '(':
            self.eat('SEPARADOR', token_esperado='(')
            tipo_esq = self.parse_expressao()
            self.eat('SEPARADOR', token_esperado=')')

        elif self.token_atual and self.token_atual['classe'] == 'NUMERAL':
            valor = self.token_atual['token']
            tipo_esq = 'float' if '.' in valor else 'int'
            self.eat('NUMERAL')

        elif self.token_atual and self.token_atual['classe'] == 'IDENTIFICADOR':
            tipo_esq = self.tabela.consultar(self.token_atual['token'])  # Verifica se a variável foi declarada
            if not tipo_esq:
                raise Exception(f"Erro Semântico na linha {self.token_atual['linha']}: Variável '{self.token_atual['token']}' não declarada.")
            self.eat('IDENTIFICADOR')
            if self.token_atual and self.token_atual['token'] in ('++', '--'):
                self.eat('OPERADOR')
                return tipo_esq

        elif self.token_atual and self.token_atual['classe'] == 'LITERAL':
            self.eat('LITERAL')
            tipo_esq = 'char'

        else:
            self.erro(
                f"Início de expressão inválido: "
                f"'{self.token_atual['token'] if self.token_atual else 'EOF'}'"
            )
            return

        operadores_binarios = ['+', '-', '*', '/', '==', '!=', '<', '>', '<=', '>=']

        while (
            self.token_atual
            and self.token_atual['classe'] == 'OPERADOR'
            and self.token_atual['token'] in operadores_binarios
        ):  
            operador = self.token_atual['token']
            self.eat('OPERADOR')

            tipo_dir = self.parse_expressao()  # Tipo do lado direito da operação
            # Cruza a esquerda e a direita na tabela de regras
            # O resultado substitui o lado esquerdo para continuar o laço (se houver mais contas)
            tipo_esq = self.avaliar_operacao(tipo_esq, tipo_dir, operador)
        
        return tipo_esq
    
    def parse_atribuicao(self):
        tipo_var = self.tabela.consultar(self.token_atual['token'])
        if not tipo_var:
            raise Exception(f"Erro Semântico na linha {self.token_atual['linha']}: Variável '{self.token_atual['token']}' não declarada.")
        self.eat('IDENTIFICADOR')

        operadores_atribuicao = ['=', '+=', '-=', '*=', '/=']
        operador = None

        if self.token_atual and self.token_atual['token'] in operadores_atribuicao:
            operador = self.token_atual['token']
            self.eat('OPERADOR')
            tipo_resultado = self.parse_expressao()
            self.avaliar_operacao(tipo_var, tipo_resultado, operador)
            self.eat('SEPARADOR', token_esperado=';')

        elif self.token_atual and self.token_atual['token'] in ('++', '--'):
            self.eat('OPERADOR')
            self.eat('SEPARADOR', token_esperado=';')

        else:
            self.erro("Esperado '=', operador de atribuição, '++', '--' ou '(' após identificador")

    def parse_retorno(self):
        self.eat('PALAVRA_RESERVADA', token_esperado='return')
        self.parse_expressao()
        self.eat('SEPARADOR', token_esperado=';')

    def parse_bloco(self):
        self.tabela.empilhar_escopo()

        while self.token_atual and self.token_atual['token'] != '}':
            token = self.token_atual['token']
            classe = self.token_atual['classe']

            try:
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
            except Exception as e:
                self.erro(str(e))

        self.tabela.desempilhar_escopo()

    def parse_programa(self):
        while self.token_atual:
            try:
                self.parse_declaracao()
            except Exception as e:
                self.erro(str(e))