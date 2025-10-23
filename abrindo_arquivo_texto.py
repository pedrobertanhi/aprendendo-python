with open("arquivo_text.txt", mode="r", encoding="UTF-8") as arquivo:
    conteudo = arquivo.read() #Le todas as linhas
    conteudo2 = arquivo.readline() #Le apenas uma linha
    
print(conteudo)