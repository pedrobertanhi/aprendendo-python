usuario = input("Informe o usuário que deseja acessar o sistema: ")
senha = input("Informe a senha do usuário que deseja acessar o sistema: ")

if usuario.upper() == "ADMIN" and senha == "123":
    print("Acesso autorizado! ")
else:
    print("Usuário ou senha incorretos. Acesso negado!")



# OUTROS (Praticando)

pais = "Brasil"
cidade = "São Paulo"
curso = "Python"

teste = pais == "Brasil" and cidade == "São Paulo"
print(f"Ao comparar se o país é Brasil e a cidade é São Paulo com o operador AND obtivemos: {teste}")

teste = pais == "Brasil" and cidade == "Rio de Janeiro"
print(f"Ao comparar se o país é Brasil e a cidade é Rio de Janeiro com o operador AND obtivemos: {teste}")

teste = pais == "Brasil" or curso == "Python"
print(f"Ao comparar se o país é Brasil e o curso é Python com o operador OR obtivemos: {teste}")

teste = pais == "Brasil" or curso == "Java"
print(f"Ao comparar se o país é Brasil e o curso é Java com o operador OR obtivemos: {teste}")

teste = not pais == "Brasil"
print(f"Ao aplicar o NOT na comparação pais == Brasil obtivemos: {teste}")

teste = not pais == "Inglaterra"
print(f"Ao aplicar o NOT na comparação pais == Inglaterra obtivemos: {teste}")
