class TabelaSimbolos:
    def __init__(self):
        self.pilha_escopos = [{}]
    
    def empilhar_escopo(self):
        self.pilha_escopos.append({})
    
    def desempilhar_escopo(self):
        if len(self.pilha_escopos) > 1:
            self.pilha_escopos.pop()
    
    def inserir(self, nome, tipo, linha):
        escopo_atual = self.pilha_escopos[-1]

        # Erro Semântico: Redeclaração de variável
        if nome in escopo_atual:
            raise Exception(f"Erro Semântico na linha {linha}: Variável '{nome}' já foi declarada neste escopo.")

        escopo_atual[nome] = tipo
    
    def consultar(self,nome):
        """Busca a variável de dentro para fora (escopo local até o global)."""
        for escopo in reversed(self.pilha_escopos):
            if nome in escopo:
                return escopo[nome] # Retorna o tipo da variável
        return None # Variável não encontrada em nenhum escopo