import re
import unicodedata
from funcoes import (
    cadastrar_cliente,
    cadastrar_processo,
    lancar_financeiro,
    lancar_financeiro_parcelado,
    pagar_financeiro,
    deletar_financeiro,
    deletar_cliente_por_cpf,
    deletar_processo_completo,
    deletar_prazo_agenda,
    cadastrar_agenda,
    consultar_visao_geral,
    consultar_agenda_do_dia # Nova função importada
)

dados_pendentes = {}

def remover_acentos(texto):
    return "".join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).replace('ç', 'c')

def extrair_numeros(texto):
    return re.sub(r"[-./()\s]", "", texto)

def limpar_valor(texto):
    texto = texto.upper().replace("R$", "").strip()
    if "," in texto and "." in texto:
        texto = texto.replace(".", "")
    texto = texto.replace(",", ".")
    return re.sub(r"[^\d.]", "", texto)

def obter_ajuda():
    return """🤖 ASSISTENTE JURÍDICO - MANUAL COMPLETO DE COMANDOS:

👤 CADASTROS BÁSICOS:
• cadastrar cliente NOME cpf CPF telefone TELEFONE email EMAIL
• criar processo NUMERO cliente NOME_DO_CLIENTE descricao TEXTO

📅 AGENDA E CONSULTA:
• agendar processo NUMERO DATA(DD/MM/AAAA) descricao TEXTO
• ver processo NUMERO (Ficha completa de um caso)
• agenda dia DATA(DD/MM/AAAA) (NOVO: Prazos de todos os clientes no dia!)

💰 PAINEL FINANCEIRO (Lançamentos):
• lancar financeiro a vista processo NUMERO valor VALOR descricao TEXTO
• lancar financeiro parcelado processo NUMERO valor VALOR_TOTAL parcelas QTD descricao TEXTO
• pagar financeiro ID processo NUMERO

🗑️ COMANDOS PARA DELETAR:
• deletar cliente cpf CPF_DO_CLIENTE
• deletar processo NUMERO
• deletar financeiro ID processo NUMERO
• deletar agenda DATA(DD/MM/AAAA) processo NUMERO"""

def responder_pergunta(pergunta):
    global dados_pendentes
    pergunta_original = pergunta.strip()
    pergunta_limpa = remover_acentos(pergunta_original.lower())

    if "ajuda" in pergunta_limpa or "comando" in pergunta_limpa:
        return obter_ajuda()

    # =========================================================================
    # FLUXO DE CONFIRMAÇÃO SE SERÁ PARCELADO OU À VISTA
    # =========================================================================
    if dados_pendentes:
        if "a vista" in pergunta_limpa or "nao" in pergunta_limpa or "1" in pergunta_limpa:
            num = dados_pendentes["num"]
            val = dados_pendentes["val"]
            desc = dados_pendentes["desc"]
            dados_pendentes = {}
            lancar_financeiro(num, val, desc)
            return f"✅ Entendido! Lançamento À VISTA de R$ {val:.2f} ('{desc}') adicionado ao processo {num}."
        
        match_qtd = re.search(r"(?:parcelado|sim|\s+)(\d+)", pergunta_limpa)
        if match_qtd or "parcelado" in pergunta_limpa or "sim" in pergunta_limpa:
            qtd = int(match_qtd.group(1)) if match_qtd else 2 
            num = dados_pendentes["num"]
            val = dados_pendentes["val"]
            desc = dados_pendentes["desc"]
            dados_pendentes = {}
            lancar_financeiro_parcelado(num, val, qtd, desc)
            return f"💰 Entendido! O plano de {qtd} parcelas foi gerado para o valor total de R$ {val:.2f} no processo {num}."
        
        dados_pendentes = {}
        return "⚠️ Confirmação cancelada. Por favor, refaça o comando utilizando os padrões do menu de ajuda."

    # =========================================================================
    # NOVO COMANDO: CONSULTA DE AGENDA DO DIA
    # Exemplos: "agenda dia 15/05/2026", "ver agenda 15/05/2026"
    # =========================================================================
    agenda_dia_match = re.search(r"(?:agenda\s+dia|ver\s+agenda)\s+(\d+/\d+/\d+)", pergunta_limpa)
    if agenda_dia_match:
        data_busca = agenda_dia_match.group(1).strip()
        return consultar_agenda_do_dia(data_busca)

    # =========================================================================
    # SÉRIE DE COMANDOS: DELETAR REGISTROS
    # =========================================================================
    del_cli_match = re.search(r"deletar\s+cliente\s+cpf\s+([\d.-]+)", pergunta_limpa)
    if del_cli_match:
        cpf = extrair_numeros(del_cli_match.group(1))
        if deletar_cliente_por_cpf(cpf):
            return f"🗑️ Cliente portador do CPF {cpf} foi removido do sistema."
        return f"❌ Não encontrei nenhum cliente com o CPF {cpf} cadastrado."

    del_proc_match = re.search(r"deletar\s+processo\s+([\w.-]+)", pergunta_limpa)
    if del_proc_match:
        num_proc = extrair_numeros(del_proc_match.group(1))
        if deletar_processo_completo(num_proc):
            return f"🗑️ O processo número {num_proc} e todo o seu histórico foram apagados."
        return f"❌ Processo número {num_proc} não foi localizado."

    del_age_match = re.search(r"deletar\s+agenda\s+(\d+/\d+/\d+)\s+processo\s+([\w.-]+)", pergunta_limpa)
    if del_age_match:
        data = del_age_match.group(1).strip()
        num_proc = extrair_numeros(del_age_match.group(2))
        if deletar_prazo_agenda(data, num_proc):
            return f"🗑️ Todos os compromissos agendados para a data {data} no processo {num_proc} foram removidos."
        return f"❌ Não encontrei prazos na data {data} para o processo {num_proc}."

    del_fin_match = re.search(r"deletar\s+financeiro\s+(\d+)\s+processo\s+([\w.-]+)", pergunta_limpa)
    if del_fin_match:
        id_financeiro = int(del_fin_match.group(1))
        num_processo = extrair_numeros(del_fin_match.group(2))
        if deletar_financeiro(id_financeiro, num_processo):
            return f"🗑️ Registro financeiro ID {id_financeiro} removido permanentemente do processo {num_processo}!"
        return f"❌ Não encontrei nenhum lançamento financeiro com o ID {id_financeiro} para o processo {num_processo}."

    # =========================================================================
    # CADASTROS E LANÇAMENTOS FINANCEIROS
    # =========================================================================
    parcela_match = re.search(r"lancar\s+financeiro\s+parcelado\s+processo\s+([\w.-]+)\s+valor\s+(.+?)\s+parcelas\s+(\d+)\s+descricao\s+(.+)", pergunta_limpa, re.IGNORECASE)
    if parcela_match:
        num_processo = extrair_numeros(parcela_match.group(1))
        valor_total = float(limpar_valor(parcela_match.group(2)))
        qtd_parcelas = int(parcela_match.group(3))
        desc_match_orig = re.search(r"descric(?:ao|ao|ão|ao)\s+(.+)", pergunta_original, re.IGNORECASE)
        descricao = desc_match_orig.group(1).strip() if desc_match_orig else "Parcelamento"
        lancar_financeiro_parcelado(num_processo, valor_total, qtd_parcelas, descricao)
        return f"💰 Plano Parcelado: {qtd_parcelas} parcelas de R$ {(valor_total/qtd_parcelas):.2f} geradas para o processo {num_processo}."

    vista_match = re.search(r"lancar\s+financeiro\s+a\s+vista\s+processo\s+([\w.-]+)\s+valor\s+(.+?)\s+descricao\s+(.+)", pergunta_limpa, re.IGNORECASE)
    if vista_match:
        num_processo = extrair_numeros(vista_match.group(1))
        valor = float(limpar_valor(vista_match.group(2)))
        desc_match_orig = re.search(r"descric(?:ao|ao|ão|ao)\s+(.+)", pergunta_original, re.IGNORECASE)
        descricao = desc_match_orig.group(1).strip() if desc_match_orig else "Lancamento"
        lancar_financeiro(num_processo, valor, descricao)
        return f"✅ Lançamento À VISTA de R$ {valor:.2f} ('{descricao}') adicionado ao processo {num_processo}."

    gen_match = re.search(r"lancar\s+financeiro\s+processo\s+([\w.-]+)\s+valor\s+(.+?)\s+descricao\s+(.+)", pergunta_limpa, re.IGNORECASE)
    if gen_match:
        desc_match_orig = re.search(r"descric(?:ao|ao|ão|ao)\s+(.+)", pergunta_original, re.IGNORECASE)
        dados_pendentes = {
            "num": extrair_numeros(gen_match.group(1)), 
            "val": float(limpar_valor(gen_match.group(2))), 
            "desc": desc_match_orig.group(1).strip() if desc_match_orig else "Lancamento"
        }
        return "❓ Este lançamento financeiro será [A VISTA] ou [PARCELADO]? Se for parcelado, digite a quantidade de parcelas (Ex: parcelado 3)."

    # =========================================================================
    # DEMAIS FUNÇÕES DO SISTEMA (MANUTENÇÃO)
    # =========================================================================
    cliente_match = re.search(r"cadastrar\s+cliente\s+(.+?)\s+cpf\s+([\d.-]+)\s+telefone\s+([\d() .-]+)\s+email\s+(.+)", pergunta_original, re.IGNORECASE)
    if cliente_match:
        nome = cliente_match.group(1).strip()
        cpf = extrair_numeros(cliente_match.group(2))
        telefone = extrair_numeros(cliente_match.group(3))
        email = cliente_match.group(4).strip()
        cadastrar_cliente(nome, cpf, telefone, email)
        return f"✨ Tudo pronto! O cliente '{nome}' foi registrado com sucesso."

    processo_match = re.search(r"criar\s+processo\s+([\w.-]+)\s+cliente\s+(.+?)\s+descricao\s+(.+)", pergunta_limpa, re.IGNORECASE)
    if processo_match:
        num_proc = extrair_numeros(processo_match.group(1))
        nome_cli = processo_match.group(2).strip()
        desc_match_orig = re.search(r"descric(?:ao|ao|ão|ao)\s+(.+)", pergunta_original, re.IGNORECASE)
        if cadastrar_processo(num_proc, nome_cli, desc_match_orig.group(1).strip() if desc_match_orig else "Processo"):
            return f"⚖️ Processo número {num_proc} aberto com sucesso!"
        return f"❌ Não encontrei o cliente na base de dados."

    pagar_match = re.search(r"pagar\s+financeiro\s+(\d+)\s+processo\s+([\w.-]+)", pergunta_limpa, re.IGNORECASE)
    if pagar_match:
        num_proc = extrair_numeros(pagar_match.group(2))
        if pagar_financeiro(int(pagar_match.group(1)), num_proc):
            return f"🟢 Confirmado! O lançamento de ID {pagar_match.group(1)} foi marcado como quitado."
        return f"⚠️ Lançamento não encontrado."

    agenda_match = re.search(r"agendar\s+processo\s+([\w.-]+)\s+(\d+/\d+/\d+)\s+descricao\s+(.+)", pergunta_limpa, re.IGNORECASE)
    if agenda_match:
        num_proc = extrair_numeros(agenda_match.group(1))
        data = agenda_match.group(2).strip()
        desc_match_orig = re.search(r"descric(?:ao|ao|ão|ao)\s+(.+)", pergunta_original, re.IGNORECASE)
        cadastrar_agenda(num_proc, data, desc_match_orig.group(1).strip() if desc_match_orig else "Compromisso")
        return f"📅 Agendamento concluído no processo {num_proc}."

    ver_match = re.search(r"ver\s+processo\s+([\w.-]+)", pergunta_limpa, re.IGNORECASE)
    if ver_match:
        num_proc = extrair_numeros(ver_match.group(1))
        return consultar_visao_geral(num_proc)

    return "🤔 Não consegui identificar este comando. Digite 'ajuda' para verificar a lista de opções válidas."
