def calcular_velocidade_media(distancia:float, tempo:float, unidade_medida="km/h"):
    # Codigo da nossa função
    velocidade_media = distancia / tempo
    # Exibir Resultados
    print(f"A velocidade média é {velocidade_media}{unidade_medida}")
    

calcular_velocidade_media(200, 3)

