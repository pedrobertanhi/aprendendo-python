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