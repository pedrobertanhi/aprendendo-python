# importação

from collections import defaultdict

dicionario_lista = defaultdict(list)
dicionario_lista["PRODUTO"] = "Mackbook Pro"
dicionario_lista["MARCA"] = "APPLE"

print(dicionario_lista["PREÇO"])
print(dicionario_lista)

# criação de função que retorna a frase "INEXISTENTE"
def funcao_exemplo():
    return "INEXISTENTE"

dicionario_funcao = defaultdict(funcao_exemplo)
dicionario_funcao["PRODUTO"] = "Mackbook Pro"
dicionario_funcao["MARCA"] = "APPLE"

print(dicionario_funcao)
print(dicionario_funcao["PREÇO"])

# criação de dicionario com uma função lambda

dicionario_lambda = defaultdict(lambda: "Não Disponível")
dicionario_lambda["PRODUTO"] = "Mackbook Pro"
dicionario_lambda["MARCA"] = "APPLE"

print(dicionario_lambda)
print(dicionario_lambda["PREÇO"])
