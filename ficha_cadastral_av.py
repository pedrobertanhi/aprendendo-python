op = 0
ficha = {}

while op != 4:
    print("\n FICHA CADASTRAL")
    print("1 - Incluir informação")
    print("2 - Recuperar informação")
    print("3 - Exibir ficha completa")
    print("4 - Sair")
    
    try:
        op = int(input("Informe uma opção: "))
    except ValueError:
        print("Opção inválida! Digite um número.")
        continue
    
    if op == 1:
        # Inserir Ficha
        chave = input("Informe o campo que deseja cadastrar na ficha: ")
        valor = input("Informe o dado que deseja cadastrar neste campo: ")
        ficha[chave] = valor
    
    elif op == 2:
        # Recuperar dados
        if ficha:
            print(f"Os campos disponíveis na ficha são: {list(ficha.keys())}")
            campo = input("Qual campo deseja consultar? ")
            if campo in ficha:
                print(f"{campo}: {ficha[campo]}")
            else:
                print("Campo não encontrado!")
        else:
            print("Nenhum campo cadastrado ainda.")

    elif op == 3:
        if ficha:
            print("\nFicha completa:")
            for chave, valor in ficha.items():
                print(f"{chave}: {valor}")
        else:
            print("Ficha vazia.")

    elif op == 4:
        print("Finalizando Sistema")
        break

    else:
        print("Selecione uma opção valida")
