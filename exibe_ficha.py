def exibe_ficha(**dados):
    print("--- FICHA ---")
    for chave, valor in dados.items():
        print(f"{chave.upper()} - {valor}")

ficha_cliente = {
    'nome': 'Ana Silva',
    'idade': 28,
    'cidade': 'Rio de Janeiro',
    'profissão': 'Designer'
}

exibe_ficha(**ficha_cliente)