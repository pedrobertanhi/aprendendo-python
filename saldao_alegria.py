print("Saldão da Alegria!")

total_compra = float(input("Por favor, informe o valor da sua compra: "))
forma_pagamento = int(input("Selecione a forma de pagamento: 1 - Boleto ou 2 - Cartão: "))

if forma_pagamento == 1:
    #desconto
    total_compra_desconto = total_compra * 0.95
    print(f"O total da compra de R${total_compra:.2f} sofreu um desconto de pagamento em boleto. O cliente devera pagar R${total_compra_desconto:.2f}")
else:
    #parcelamento
    parcela = int(input("Informe o numero de parcelas desejadas: "))
    valor_parcela = total_compra / parcela
    print(f"O total da compra de R${total_compra:.2f} será pago em {parcela} parcelas de R${valor_parcela:.2f}")
