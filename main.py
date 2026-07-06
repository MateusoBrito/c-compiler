import sys
from analisador_lexico import AnalisadorLexico
from analisador_sintatico import Parser 

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 main.py <nome_do_arquivo.c>")
        sys.exit(1)
        
    arquivo_fonte = sys.argv[1]
    
    print(f"Iniciando compilação de: {arquivo_fonte}")
    lexico = AnalisadorLexico("regras.yaml")
    
    lista_de_tokens = lexico.analisar_arquivo(arquivo_fonte)
    
    if not lista_de_tokens:
        print("Falha na análise léxica. Processo abortado.")
        sys.exit(1)
        
    lexico.salvar_tokens_csv("tokens.csv")
    #print("Análise Léxica concluída. (tokens.csv gerado)")
    
    # 3. Inicia e executa a Análise Sintática
    print("Iniciando Análise Sintática e Semântica...")
    parser = Parser(lista_de_tokens)
    
    try:
        parser.parse_programa() 
        print(" Análise Sintática e Semântica concluída!")
    except Exception as e:
        print(f"\n Falha na compilação:\n{e}")

if __name__ == "__main__":
    main()