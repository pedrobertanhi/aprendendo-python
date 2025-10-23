texto_para_gravar = "Este texto sera gravado!"

with open("arquivo_text.txt", mode="w", encoding="UTF-8") as arquivo:
    arquivo.write(texto_para_gravar)

print("O arquivo foi gravado!")