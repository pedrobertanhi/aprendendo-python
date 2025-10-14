def calcular_velocidade_media():
    #Codigo da nossa função
    velocidade_media = distancia / tempo
    #Exibir Resultados
    print(f"A velocidade media é {velocidade_media}")
    

# Solicitar distancia e tempo
distancia = float(input("Digite a distancia percorrida: "))
tempo = float(input("Digite o tempo da viagem: "))
calcular_velocidade_media()
