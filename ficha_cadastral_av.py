op = 0
ficha = {}

while op != 4:
    print("\n FICHA CADASTRAL")
    print("1 - Incluir informação")
    print("2 - Recuperar informação")
    print("3 - Exibir ficha completa")
    print("4 - Sair")
    
    op = int(input("Informe uma opção: "))
    
    if op == 1:
        #Inserir Ficha
        chave = input("Informe o que deseja cadastrar na ficha: ")
        valor = input("Informe o dado que deseja cadastrar neste campo:")
    
    elif op == 2:
        #Recuperar dados
        
    elif op == 3:
        #Exibir ficha completa
        
    elif op == 4:
        print("Finalizando Sistema")
        break
    else:
        print("Selecione uma opção valida")

## PAREI NO 04:01
