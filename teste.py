from funcoes import cadastrar_cliente, consultar_contratos, atualizar_parcela, cadastrar_contrato, cadastrar_prazo, consultar_contratos, relatorio_parcelas, saldo_em_aberto



# 1. Cadastrar um novo cliente

cadastrar_cliente("Maria Oliveira", "98765432100", "11988887777", "maria@email.com")
print("Cliente cadastrado com sucesso!")

# 2. consultar contratos existentes

contratos = consultar_contratos()
print("Lista de contratos:")
for contrato in contratos:
    print(contrato)

# 3. Atualizar status de uma parcela

atualizar_parcela(contrato_id=1, numero_parcela=2, novo_status="paga")
print("Parcela atualizada com sucesso!")

# 4. Cadastrar contrato fictício
cadastrar_contrato("002", 3000.00, 1)
print("Contrato cadastrado com sucesso!")

# 5. Cadastrar prazo fictício
cadastrar_prazo("2026-04-10", "Entrega de documentos", 1)
print("Prazo cadastrado com sucesso!")

# 6. Consultar contratos
contratos = consultar_contratos()
print("Contratos cadastrados:")
for contrato in contratos:
    print(contrato)

 # Relatório de parcelas
print("Relatório de parcelas do contrato 001:")
print(relatorio_parcelas(1))

# Saldo em aberto
print("Saldo em aberto do contrato 001:")
print(saldo_em_aberto(1))
   