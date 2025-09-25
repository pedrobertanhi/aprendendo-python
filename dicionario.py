dicionario = {
    "Nome": "Star Wars - Episódio IV - uma nova esperança",
    "Diretor": "George Lucas",
    "Lançamento": 1977,
    "Bilheteria": 765640000.00
}
print(type(dicionario))

print(dicionario)

print(dicionario["Nome"])

# Inserir novo valor

dicionario["Gênero"] = "Space Opera"
print(dicionario)

#KEYS
print(dicionario.keys())

for chave in dicionario.keys():
    print(chave)
    
    
# VALUES
print(dicionario.values())
for valor in dicionario.values():
    print(valor)
    
#ITEMS
print(dicionario.items())
for chave, valor in dicionario.items():
    print(f"{chave} -- {valor}")
    
# GET (Procura no dicionario)
print(dicionario.get("público")) # N EXISTE
print(dicionario.get("nome")) # EXISTE

#SETDEFAULT
dicionario.setdefault("púlico", 1000)
print(dicionario)
dicionario.setdefault("público", 9000)
print(dicionario)
