lista = [12, 15.5, "Textos"]
print(type(lista))

#Inserindo Elementos
lista.append("Teste de Inserção")


#Mostrando a lista inteira
print(lista)


#Mostrando Elemento Pelo Indice
print(lista[0:3])


#Exibindo com o loop
for valor in lista:
    print(valor)

    
#Removendo
lista.pop()
print(lista)
lista.remove(12)
print(lista)

#Tamanho da lista
print(len(lista))
