class TabelaSimbolos:
    def __init__(self):
        self.pilha_escopos = [{}]
    
    def empilhar_escopo(self):
        self.pilha_escopos.append({})
    
    def desempilhar_escopo(self):
        escopo_atual = self.pilha_escopos[-1]
        for nome, info in escopo_atual.items():
            if not info['usada']:
                print(f"Warning Semântico: Variável '{nome}' (tipo '{info['tipo']}') declarada na linha {info['linha']} nunca foi utilizada.")
        #self.exibir_tabela()
        if len(self.pilha_escopos) > 1:
            self.pilha_escopos.pop()
    
    def inserir(self, nome, tipo, linha):
        escopo_atual = self.pilha_escopos[-1]

        # Erro Semântico: Redeclaração de variável
        if nome in escopo_atual:
            print(f"Erro Semântico na linha {linha}: Variável '{nome}' já foi declarada neste escopo.")
            return 

        escopo_atual[nome] = {
            'tipo': tipo,
            'usada': False,
            'linha': linha
        }
    
    def consultar(self,nome):
        """Busca a variável de dentro para fora (escopo local até o global)."""
        for escopo in reversed(self.pilha_escopos):
            if nome in escopo:
                escopo[nome]['usada'] = True
                return escopo[nome]['tipo'] # Retorna o tipo da variável
        return None # Variável não encontrada em nenhum escopo

    def exibir_tabela(self):
        print("\n" + "="*40)
        print(" ESTADO ATUAL DA TABELA DE SÍMBOLOS")
        print("="*40)
        
        for i, escopo in enumerate(self.pilha_escopos):
            nome_escopo = "Global" if i == 0 else f"Local (Nível {i})"
            print(f"[{nome_escopo}]")
            
            if not escopo:
                print("  (Vazio)")
            else:
                for nome, info in escopo.items():
                    status = "Usada" if info['usada'] else "Não usada"
                    print(f"  -> Variável: '{nome}' | Tipo: {info['tipo']} | Linha: {info['linha']} | Status: {status}")
            print("-" * 40)
        print("\n")