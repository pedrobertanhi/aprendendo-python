conjunto = set()
print(type(conjunto))

lista = ["Pedro", "Henrique", "Bruno", "Pedro"]
print(lista)

conjunto2 = set(lista)
print(conjunto2)

conjunto3 = {"Cebolinha", "Magali", "Monica", "Cebolinha"}
print(conjunto3)

conjunto3.add("Franjinha")
print(conjunto3)

## RECRIANDO CONJUNTO
conjunto1 = {"Mega Drive", "Super Nitendo", "Playstation"}
conjunto2 = {"Playstation", "Nitendo 64", "Sega Saturn", "Dreamcast"}

print(f"O primeiro set contem: {conjunto1}")
print(f"O segundo set contem: {conjunto2}")

# TIRA ELEMENTOS IGUAIS NOS CONJUNTOS (difference_update)
conjunto1.difference_update(conjunto2)
print(f"O primeiro set contem {conjunto1}")

## REMOVER ELEMENTO ESPECIFICO (remove)
conjunto1 = {"Mega Drive", "Super Nitendo", "Playstation"}
print(conjunto1)
conjunto1.remove("Mega Drive")
print(conjunto1)

### REMOVER UM ELEMENTO ESPECIFICO (Discard)
conjunto1.discard("Super Nintendo")
print(conjunto1)
conjunto1.discard("Super Nintendo")
print(conjunto1)
