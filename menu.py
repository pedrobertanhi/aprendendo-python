opcao = 0

while opcao != 3:
    print("1 - Receber um elogio")
    print("2 - Calculo Fatorial")
    print("3 - Sair")
    opcao = int(input("Escolha uma opção: "))
    
if opcao == 1:
    nome = input("Você é incrivel")
    print(f"{nome}, você é uma pessoa incrível!")
    
elif opcao == 2:
    numero = int(input("Informe o numero para calcular o fatorial: "))
    fat = numero 

    for valor in range(1, numero, 1):
        fat = fat * valor

    print(f"O fatorial de {numero} é de: {fat}")
    
elif opcao == 3:
    print("Menu Finalizado")
    
else:
    print("Opção inválida, tente novamente!")
