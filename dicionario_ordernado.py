# IMPORTA DICIONARIO ORDENADO
from collections import OrderedDict

dicionario_ordenado = OrderedDict()
print(dicionario_ordenado)

# Adicionando chaves e valores
dicionario_ordenado["NOME"] = "14s"
dicionario_ordenado["MARCA"] = "Xiaomi"
dicionario_ordenado["MODELO"] = "Redmi Note"

# PERCORER PARA VERIFICAR A ORDERM  
for chave, valor in dicionario_ordenado.items():
    print(f"{chave} -- {valor}")

# ALTERANDO UM ITEM

dicionario_ordenado["MARCA"] = "Chines"

# PERCOREER PRA VERIFICAR NOVA ORDEM
for chave, valor in dicionario_ordenado.items():
    print(f"{chave} -- {valor}")

# REMOVENDO UM ITEM
dicionario_ordenado.pop("MARCA")
print()

for chave, valor in dicionario_ordenado.items():
    print(f"{chave} -- {valor}")

# REINSERINDO UM ITEM NESTE DICIONARIO
dicionario_ordenado["MARCA"] = "Xiaomi"
print()

for chave, valor in dicionario_ordenado.items():
    print(f"{chave} -- {valor}")
