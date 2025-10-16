def calcular_velocidade_media(distancia, tempo):
    # Codigo da nossa função
    velocidade_media = distancia / tempo
    # Exibir Resultados
    print(f"A velocidade média é {velocidade_media}")

# Solicitar distancia e tempo
dist_digitada = float(input("Digite a distância percorrida: "))
tempo_digitado = float(input("Digite o tempo da viagem: "))
calcular_velocidade_media(dist_digitada, tempo_digitado)
