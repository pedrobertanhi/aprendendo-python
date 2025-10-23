def soma(a, b):
    resultado =  a + b
    return resultado
    
valor1 = int(input("Digite o primeiro valor: "))
valor2 = int(input("Digite o segundo valor: "))

resposta = soma(valor1, valor2)
print(f"A soma entre {valor1} e {valor2} é igual a {resposta}.")
print(f"A resposta é {soma(valor1, valor2)}.")
