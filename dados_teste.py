"""import sqlite3

conexao = sqlite3.connect("advocacia.db")
cursor = conexao.cursor()

# Inserir cliente fictício

cursor.execute("INSERT INTO clientes (nome, cpf, telefone, email) Values (?, ?, ?, ?)",
                ("João Silva", "12345678900", "1199999999990", "joao@email.com"))

# Inserir contrato fictício

cursor.execute("INSERT INTO contratos (numero, valor_total, cliente_id) VALUES (?, ?, ?)",
               ("001", 5000.00, 1))

# Inserir parcelas fictícias

for i in range(1, 11):
    cursor.execute("INSERT INTO parcelas (numero, valor, status, contrato_id) VALUES (?, ?, ?, ?)",
                   (i, 500.00, "pendente", 1))
    
# Inserir prazo fictício

cursor.execute("INSERT INTO prazos (data, descricao, contrato_id) VALUES (?, ?, ?)",
                   ("2026-03-15", "Audiencia inicial", 1))
conexao.commit()
conexao.close()
print("Dados fictícios inseridos com sucesso!")    

from funcoes import cadastrar_cliente, cadastrar_contrato, saldo_em_aberto

# cadastrar cliente
cadastrar_cliente("Maria Silva", "12345678900", "119999999", "maria@email.com")

# criar contrato 5000 em 10x
cadastrar_contrato("001", 5000, 1, 10)

print("Saldo em aberto:", saldo_em_aberto(1))"""

from funcoes import cadastrar_cliente, cadastrar_contrato, saldo_em_aberto

print("Iniciando teste...")

# 1️⃣ Criar cliente
cadastrar_cliente(
    "Maria Silva",
    "12345678900",
    "11999999999",
    "maria@email.com"
)

print("Cliente criado!")

# 2️⃣ Criar contrato de 5000 em 10 parcelas
cadastrar_contrato(
    "001",   # número contrato
    5000,    # valor total
    1,       # id do cliente (primeiro cliente = id 1)
    10       # quantidade de parcelas
)

print("Contrato criado com parcelas!")

# 3️⃣ Ver saldo em aberto
saldo = saldo_em_aberto(1)
print("Saldo em aberto do contrato 1:", saldo)