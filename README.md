# Analisador Léxico

Este projeto é um **Analisador Léxico (Scanner)** para a linguagem C desenvolvido em Python que utiliza expressões regulares (Regex) e um arquivo de configuração **YAML** para identificar tokens em arquivos de código-fonte (ex: `.c`).

A grande vantagem deste analisador é ser (quase) **genérico**: as regras de linguagem, palavras reservadas e operadores não estão "travados" no código Python, mas sim definidos externamente.

## Funcionalidades

* **Execução via comando**: Suporte a argumentos de linha de comando (sys.argv), permitindo processar qualquer arquivo passando o caminho como primeiro argumento.
* **Configuração Dinâmica**: Altere as regras da linguagem no `regras.yaml` sem mexer no código Python.
* **Gestão de Erros**: Identifica caracteres que não pertencem a nenhuma classe definida na linha e coluna exatas.
* **Saída Estruturada**: Gera um arquivo `tokens.csv` com a classificação completa de cada token encontrado.

---

## Estrutura do Arquivo `regras.yaml`

O arquivo YAML organiza a lógica do compilador em classes de tokens.

* **regras**: A expressão regular que define o token.
* **delimitadores**: (Opcional) Lista de classes de tokens que, ao aparecerem após um token atual, forçam o seu fechamento.
* **Ordem de Prioridade**: O analisador percorre o YAML de cima para baixo. Portanto, coloque `PALAVRA_RESERVADA` antes de `IDENTIFICADOR`.

### Exemplo de Regra:
```yaml
NUMERAL:
  regras: '([0-9]+\.[0-9]*|[0-9]*\.[0-9]+|[0-9]+)'
  delimitadores: ["SEPARADOR", "OPERADOR"]
```

---

## Código (`analisador_lexico.py`)

O código funciona através de um ponteiro chamado **batedor**, que percorre o arquivo caractere por caractere.

### 1. Estado Intermediário
O estado **INTERMEDIÁRIO** impede que o código "desista" de um token antes de ele estar completo.
* **Exemplo**: Ao ler `85.`, ele ainda não é um `NUMERAL` completo (float), mas o estado intermediário mantém o batedor acumulando caracteres até encontrar o `5` (formando `85.5`).

### 2. Lógica de Casamento (Match)
* **Match Total**: O código tenta dar um `fullmatch` em todas as regras do YAML. Se houver sucesso, ele continua aumentando o token.
* **Delimitadores**: Se o token parar de dar match, o código verifica se o caractere atual (`c`) é um delimitador válido (espaço ou uma classe permitida). Se for, o token é salvo e o batedor reinicia para o próximo.

---

## 📖 Como Usar

1.  Certifique-se de ter o Python 3 e a biblioteca `PyYAML` instalados:
    ```bash
    pip install pyyaml
    ```

2.  Prepare seu arquivo de entrada (ex: `codigo.c`) e o arquivo de regras (`regras.yaml`).

3.  Execute o analisador:
    ```bash
    python3 analisador_lexico.py codigo.c
    ```

4.  Verifique o resultado no arquivo `tokens.csv`.

---

## 📊 Exemplo de Saída (`tokens.csv`)

| token | classe | linha | coluna |
| :--- | :--- | :--- | :--- |
| int | PALAVRA_RESERVADA | 1 | 0 |
| main | IDENTIFICADOR | 1 | 4 |
| ( | SEPARADOR | 1 | 8 |
| 10.5 | NUMERAL | 5 | 15 |
| "Oi" | LITERAL | 2 | 11 |

---

## ⚠️ Limitações Conhecidas
* O estado **INTERMEDIÁRIO** é tratado dentro do código (`analisador_lexico.py`), logo, caso as regras mudem, ele deve ser verificado também, não deixando o código 100% genérico.

---
**Desenvolvido como projeto prático para a disciplina de Compiladores - UFSJ.**
