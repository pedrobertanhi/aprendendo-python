#Função para caluclar velocidade media
def calcular_elocidade_media(distancia:float, tempo:float, unidade='km/h'):
    if tempo == 0:
        return 0
    velocidade_media = distancia / tempo
    return f"{velocidade_media} {unidade}"

#Função para converter a temperatura
def converter_temperatura(temperatura:float, unidade_medida="Celsius"):
    if unidade_medida == "Celsius":
        fahrenheit = temperatura * 1.8 + 32
        return f"{fahrenheit} °F"
    elif unidade_medida == "Fahrenheit":
        celsius = (temperatura - 32) / 1.8
        return f"{celsius} °C"
    else:
        return 0
    
#Função exibir menu
def exibir_menu():
    print("MENU")
    print("1 - Calcular velocidade media")
    print("2 - Converter temperatura")
    print("3 - sair")
    
    
#FUNÇÃO PRA CHAMAR OUTRAS OPÇÕES
def aluno_de_fisica():
    op = 0
    while op != 3:
        exibir_menu()
        op = int(input("Informe a opção desejada: "))
        if op == 1:
            distancia_percorrida = float(input("Informe a distância: "))
            tempo_viagem = float(input("Informe o tempo da viagem: "))
            medida = input("Informe a unidade de medida: ")
            print(f"A velocidade média é {calcular_elocidade_media(distancia_percorrida, tempo_viagem, medida)}")
        
        elif op == 2:   
            temperatura_informada = float(input("Informe a temperatura que deseja converter: "))
            medida = input("A temperatura informada está em celsius ou fahrenhit")
            print(f"O resultado da conversão é {converter_temperatura(temperatura_informada, medida)}")
        
        elif op == 3:
            print("Saindo ...")
            break
        else:
            print("Opção Invalida")