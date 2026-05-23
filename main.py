import sys
# Importa as suas classes
from analisador_lexico import AnalisadorLexico
from analisador_sintatico import Parser 

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 main.py <nome_do_arquivo.c>")
        sys.exit(1)
        
    arquivo_fonte = sys.argv[1]
    
    # 2. Inicia e executa a Análise Léxica
    print(f"Iniciando compilação de: {arquivo_fonte}")
    lexico = AnalisadorLexico("regras.yaml")
    
    lista_de_tokens = lexico.analisar_arquivo(arquivo_fonte)
    
    if not lista_de_tokens:
        print("Falha na análise léxica. Processo abortado.")
        sys.exit(1)
        
    #lexico.salvar_tokens_csv("tokens.csv")
    #print("✓ Análise Léxica concluída. (tokens.csv gerado)")
    
    # 3. Inicia e executa a Análise Sintática
    print("Iniciando Análise Sintática...")
    parser = Parser(lista_de_tokens)
    
    try:
        parser.parse_programa() # Chama a raiz da sua árvore
        print(" Análise Sintática concluída com sucesso! Nenhuma violação encontrada.")
    except Exception as e:
        print(f"\n Falha na compilação:\n{e}")

if __name__ == "__main__":
    main()