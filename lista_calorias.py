calorias = []
resposta = ""

while resposta.upper() != "NÃO":
    caloria = int(input("Quantas calorias vocÇe consumiu: "))
    calorias.append(calorias)
    resposta = input("Você deseja informar mais uma refeição ? ")
    
total = 0    
for caloria in calorias:
    print(f"Nesta refeição foram consumidas {caloria} calorias")
    total = total + caloria
    
media = total /len(calorias)
print(f"Neste dia, teve um consumo medio de {media} calorias por refeição")
