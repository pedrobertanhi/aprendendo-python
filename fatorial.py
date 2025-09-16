for contador in range(10, 100, 2):
    print(contador)
    if contador == 20:
        break
    
numero = int(input("Informe o numero para calcular o fatorial: "))
fat = numero 

for valor in range(1, numero, 1):
    fat = fat * valor

print(f"O fatorial de {numero} é de: {fat}")
