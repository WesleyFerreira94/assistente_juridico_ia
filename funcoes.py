import sqlite3
import unicodedata

def criar_banco():
    """Cria o banco de dados e as novas tabelas centradas no Processo"""
    conexao = sqlite3.connect("advocacia.db")
    cursor = conexao.cursor()

    # Habilita o suporte a chaves estrangeiras no SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Tabela de Clientes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cpf TEXT UNIQUE NOT NULL,
        telefone TEXT,
        email TEXT
    );
    """)

    # 2. Tabela de Processos (Eixo Central)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS processos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_processo TEXT UNIQUE NOT NULL,
        descricao TEXT,
        cliente_id INTEGER,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
    );
    """)

    # 3. Tabela Financeira do Processo
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financeiro_processo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT NOT NULL,
        valor REAL NOT NULL,
        status TEXT DEFAULT 'aberto',
        processo_id INTEGER,
        FOREIGN KEY (processo_id) REFERENCES processos(id) ON DELETE CASCADE
    );
    """)

    # 4. Tabela de Agenda do Processo
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agenda_processo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT NOT NULL,
        descricao TEXT NOT NULL,
        processo_id INTEGER,
        FOREIGN KEY (processo_id) REFERENCES processos(id) ON DELETE CASCADE
    );
    """)

    conexao.commit()
    conexao.close()


def cadastrar_cliente(nome, cpf, telefone, email):
    """Cadastra um novo cliente no sistema"""
    conexao = sqlite3.connect("advocacia.db")
    cursor = conexao.cursor()
    try:
        cursor.execute(
            "INSERT INTO clientes (nome, cpf, telefone, email) VALUES (?, ?, ?, ?)",
            (nome, cpf, telefone, email)
        )
        conexao.commit()
    except sqlite3.IntegrityError:
        pass  # Evita que o programa trave se o CPF já existir
    finally:
        conexao.close()


def cadastrar_processo(numero_processo, nome_cliente, descricao):
    """Busca o cliente pelo nome de forma inteligente, removendo acentos de ambos os lados"""
    conexao = sqlite3.connect("advocacia.db")
    cursor = conexao.cursor()

    # Busca todos os clientes cadastrados no banco
    cursor.execute("SELECT id, nome FROM clientes")
    todos_clientes = cursor.fetchall()

    cliente_id = None
    
    # 1. Normaliza e remove acentos do nome digitado pelo usuário (Ex: 'João' vira 'joao')
    nome_busca_limpo = "".join(
        c for c in unicodedata.normalize('NFD', nome_cliente.lower())
        if unicodedata.category(c) != 'Mn'
    )

    # 2. Varre a lista do banco normalizando cada nome para comparar de forma justa
    for c_id, c_nome in todos_clientes:
        c_nome_limpo = "".join(
            c for c in unicodedata.normalize('NFD', c_nome.lower())
            if unicodedata.category(c) != 'Mn'
        )
        
        # Verifica se o termo buscado está contido no nome do banco (Ex: 'joao' está em 'joao da silva')
        if nome_busca_limpo in c_nome_limpo:
            cliente_id = c_id
            break

    # Se não encontrou nenhuma correspondência aproximada
    if not cliente_id:
        conexao.close()
        return False

    # 3. Salva o processo vinculando ao ID localizado
    try:
        cursor.execute(
            "INSERT INTO processos (numero_processo, descricao, cliente_id) VALUES (?, ?, ?)",
            (numero_processo, descricao, cliente_id)
        )
        conexao.commit()
        sucesso = True
    except sqlite3.IntegrityError:
        sucesso = False
    finally:
        conexao.close()
        
    return sucesso


def lancar_financeiro(numero_processo, valor, descricao):
    """Lança uma movimentação financeira à vista vinculada ao número do processo"""
    conexao = sqlite3.connect("advocacia.db")
    cursor = conexao.cursor()

    cursor.execute("SELECT id FROM processos WHERE numero_processo = ?", (numero_processo,))
    processo = cursor.fetchone()

    if processo:
        processo_id = processo[0]
        cursor.execute(
            "INSERT INTO financeiro_processo (descricao, valor, status, processo_id) VALUES (?, ?, 'aberto', ?)",
            (descricao, valor, processo_id)
        )
        conexao.commit()

    conexao.close()


def lancar_financeiro_parcelado(numero_processo, valor_total, quantidade_parcelas, descricao_base):
    """Gera lançamentos financeiros divididos em parcelas sequenciais no banco"""
    conexao = sqlite3.connect("advocacia.db")
    cursor = conexao.cursor()

    cursor.execute("SELECT id FROM processos WHERE numero_processo = ?", (numero_processo,))
    processo = cursor.fetchone()

    if processo:
        processo_id = processo[0]
        valor_parcela = valor_total / quantidade_parcelas
        
        for i in range(1, quantidade_parcelas + 1):
            descricao_parcela = f"{descricao_base} ({i}/{quantidade_parcelas})"
            cursor.execute("""
                INSERT INTO financeiro_processo (descricao, valor, status, processo_id) 
                VALUES (?, ?, 'aberto', ?)
            """, (descricao_parcela, valor_parcela, processo_id))
            
        conexao.commit()
        sucesso = True
    else:
        sucesso = False

    conexao.close()
    return sucesso


def pagar_financeiro(id_financeiro, numero_processo):
    """Dá baixa (paga) um lançamento financeiro específico de um processo"""
    conexao = sqlite3.connect("advocacia.db")
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT f.id FROM financeiro_processo f
        JOIN processos p ON f.processo_id = p.id
        WHERE f.id = ? AND p.numero_processo = ?
    """, (id_financeiro, numero_processo))
    
    lancamento = cursor.fetchone()

    if lancamento:
        cursor.execute(
            "UPDATE financeiro_processo SET status = 'pago' WHERE id = ?",
            (id_financeiro,)
        )
        conexao.commit()
        sucesso = True
    else:
        sucesso = False

    conexao.close()
    return sucesso


def deletar_financeiro(id_financeiro, numero_processo):
    """Remove definitivamente um lançamento financeiro pelo ID para corrigir erros"""
    conexao = sqlite3.connect("advocacia.db")
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT f.id FROM financeiro_processo f
        JOIN processos p ON f.processo_id = p.id
        WHERE f.id = ? AND p.numero_processo = ?
    """, (id_financeiro, numero_processo))
    
    existe = cursor.fetchone()

    if existe:
        cursor.execute("DELETE FROM financeiro_processo WHERE id = ?", (id_financeiro,))
        conexao.commit()
        sucesso = True
    else:
        sucesso = False

    conexao.close()
    return sucesso


def deletar_cliente_por_cpf(cpf):
    """Remove um cliente e tudo que estiver atrelado a ele pelo CPF (Cascade)"""
    conexao = sqlite3.connect("advocacia.db")
    cursor = conexao.cursor()
    
    cursor.execute("SELECT id FROM clientes WHERE cpf = ?", (cpf,))
    cliente = cursor.fetchone()
    
    if cliente:
        cliente_id = cliente[0]
        cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        conexao.commit()
        sucesso = True
    else:
        sucesso = False
        
    conexao.close()
    return sucesso


def deletar_processo_completo(numero_processo):
    """Remove um processo, seu financeiro e sua agenda pelo número (Cascade)"""
    conexao = sqlite3.connect("advocacia.db")
    cursor = conexao.cursor()
    
    cursor.execute("SELECT id FROM processos WHERE numero_processo = ?", (numero_processo,))
    processo = cursor.fetchone()
    
    if processo:
        processo_id = processo[0]
        cursor.execute("DELETE FROM processos WHERE id = ?", (processo_id,))
        conexao.commit()
        sucesso = True
    else:
        sucesso = False
        
    conexao.close()
    return sucesso


def deletar_prazo_agenda(data, numero_processo):
    """Remove todos os prazos de uma data específica de um processo"""
    conexao = sqlite3.connect("advocacia.db")
    cursor = conexao.cursor()
    
    cursor.execute("""
        SELECT a.id FROM agenda_processo a
        JOIN processos p ON a.processo_id = p.id
        WHERE a.data = ? AND p.numero_processo = ?
    """, (data, numero_processo))
    
    prazos = cursor.fetchall()
    
    if prazos:
        cursor.execute("""
            DELETE FROM agenda_processo 
            WHERE data = ? AND processo_id = (SELECT id FROM processos WHERE numero_processo = ?)
        """, (data, numero_processo))
        conexao.commit()
        sucesso = True
    else:
        sucesso = False
        
    conexao.close()
    return sucesso


def cadastrar_agenda(numero_processo, data, descricao):
    """Agenda um compromisso ou prazo vinculado ao processo"""
    conexao = sqlite3.connect("advocacia.db")
    cursor = conexao.cursor()

    cursor.execute("SELECT id FROM processos WHERE numero_processo = ?", (numero_processo,))
    processo = cursor.fetchone()

    if processo:
        processo_id = processo[0]
        cursor.execute(
            "INSERT INTO agenda_processo (data, descricao, processo_id) VALUES (?, ?, ?)",
            (data, descricao, processo_id)
        )
        conexao.commit()

    conexao.close()


def consultar_visao_geral(numero_processo):
    """Cruza as tabelas e monta um relatório unificado do processo com diagnóstico de erros"""
    try:
        conexao = sqlite3.connect("advocacia.db")
        cursor = conexao.cursor()

        # 1. Busca dados do Processo e do Cliente associado
        cursor.execute("""
            SELECT p.descricao, c.nome, c.cpf 
            FROM processos p
            JOIN clientes c ON p.cliente_id = c.id
            WHERE p.numero_processo = ?
        """, (numero_processo,))
        dados_base = cursor.fetchone()

        if not dados_base:
            conexao.close()
            return f"❌ Processo {numero_processo} não foi encontrado no sistema. Verifique se o número está correto."

        proc_descricao, nome_cliente, cpf_cliente = dados_base

        # 2. Busca lançamentos financeiros do processo
        cursor.execute("""
            SELECT id, descricao, valor, status 
            FROM financeiro_processo 
            WHERE processo_id = (SELECT id FROM processos WHERE numero_processo = ?)
        """, (numero_processo,))
        financeiros = cursor.fetchall()

        # 3. Busca compromissos da agenda do processo
        cursor.execute("""
            SELECT data, descricao 
            FROM agenda_processo 
            WHERE processo_id = (SELECT id FROM processos WHERE numero_processo = ?)
            ORDER BY data ASC
        """, (numero_processo,))
        compromissos = cursor.fetchall()

        conexao.close()

        # 4. Montagem estética da resposta em texto para a IA exibir
        resposta = f"⚖️ VISÃO GERAL DO PROCESSO: {numero_processo}\n"
        resposta += f"👤 Cliente: {nome_cliente} (CPF: {cpf_cliente})\n"
        resposta += f"📝 Descrição: {proc_descricao}\n"
        resposta += "-" * 40 + "\n"

        resposta += "💰 PAINEL FINANCEIRO:\n"
        if not financeiros:
            resposta += "  Nenhum lançamento financeiro registrado.\n"
        else:
            saldo_aberto = 0
            for fin_id, desc, val, status in financeiros:
                icone = "🟢 [PAGO]" if status == "pago" else "🔴 [ABERTO]"
                resposta += f"  ID {fin_id}: {desc} - R$ {val:.2f} {icone}\n"
                if status == "aberto":
                    saldo_aberto += val
            resposta += f"   Total Pendente: R$ {saldo_aberto:.2f}\n"

        resposta += "-" * 40 + "\n"
        resposta += "📅 AGENDA DO PROCESSO:\n"
        if not compromissos:
            resposta += "  Nenhum compromisso ou prazo agendado.\n"
        else:
            for data, desc in compromissos:
                resposta += f"  • {data} - {desc}\n"

        return resposta

    except Exception as e:
        return f"🚨 Erro interno no banco de dados ao buscar o processo: {str(e)}"


def consultar_agenda_do_dia(data_busca):
    """Busca todos os prazos de uma data específica, trazendo o Processo e o Cliente"""
    try:
        conexao = sqlite3.connect("advocacia.db")
        cursor = conexao.cursor()

        # Consulta com múltiplos JOINs para cruzar Agenda -> Processo -> Cliente
        cursor.execute("""
            SELECT p.numero_processo, c.nome, a.descricao 
            FROM agenda_processo a
            JOIN processos p ON a.processo_id = p.id
            JOIN clientes c ON p.cliente_id = c.id
            WHERE a.data = ?
        """, (data_busca,))
        
        prazos = cursor.fetchall()
        conexao.close()

        if not prazos:
            return f"📅 Agenda livre! Nenhum prazo ou compromisso localizado para o dia {data_busca}."

        # Montagem do relatório diário
        resposta = f"📅 AGENDA JURÍDICA DO DIA: {data_busca}\n"
        resposta += f"Encontrado(s) {len(prazos)} compromisso(s) para esta data:\n"
        resposta += "-" * 50 + "\n"

        for num_proc, nome_cli, descricao in prazos:
            resposta += f"⚖️ Proc: {num_proc}\n"
            resposta += f"👤 Cliente: {nome_cli}\n"
            resposta += f"📝 Prazo: {descricao}\n"
            resposta += "-" * 50 + "\n"

        return resposta

    except Exception as e:
        return f"🚨 Erro ao buscar agenda do dia: {str(e)}"
