import sqlite3
import tkinter as tk
from tkinter import scrolledtext
from ia import responder_pergunta
from funcoes import criar_banco

# Executa a criação das novas tabelas focadas em Processo
criar_banco()

# =============================
# FUNÇÕES CHAT
# =============================
def adicionar_mensagem(remetente, mensagem):
    chat.config(state="normal")

    if remetente == "Você":
        chat.insert(tk.END, "\nVocê:\n", "user")
        chat.insert(tk.END, f"{mensagem}\n", "user_msg")
    else:
        chat.insert(tk.END, "\nAssistente:\n", "bot")
        chat.insert(tk.END, f"{mensagem}\n", "bot_msg")

    chat.config(state="disabled")
    chat.see(tk.END)

def enviar_pergunta():
    pergunta = entrada.get()
    if pergunta.strip() == "":
        return

    adicionar_mensagem("Você", pergunta)
    resposta = responder_pergunta(pergunta)
    adicionar_mensagem("Assistente", resposta)

    entrada.delete(0, tk.END)

# =============================
# JANELA PRINCIPAL
# =============================
janela = tk.Tk()
janela.title("Assistente Jurídico")
janela.geometry("520x720")
janela.minsize(500,680)
janela.configure(bg="#020617")  # fundo geral bem escuro

# =============================
# HEADER (barra superior azul)
# =============================
header = tk.Frame(janela, bg="#2563eb", height=70)
header.pack(fill="x")
header.pack_propagate(False)

titulo = tk.Label(
    header,
    text="Assistente Jurídico",
    bg="#2563eb",
    fg="white",
    font=("Segoe UI", 16, "bold")
)
titulo.pack(pady=18)

# =============================
# ÁREA DO CHAT (cinza azulado)
# =============================
frame_chat = tk.Frame(janela, bg="#111827")
frame_chat.pack(padx=15, pady=(10,15), fill="both", expand=True)

chat = scrolledtext.ScrolledText(
    frame_chat,
    wrap=tk.WORD,
    font=("Segoe UI", 11),
    bg="#111827",
    fg="#e5e7eb",
    bd=0,
    padx=15,
    pady=15
)
chat.pack(fill="both", expand=True)
chat.config(state="disabled")

# Tags de cores do chat
chat.tag_config("user", foreground="#60a5fa", font=("Segoe UI", 10, "bold"))
chat.tag_config("bot", foreground="#34d399", font=("Segoe UI", 10, "bold"))
chat.tag_config("user_msg", foreground="#e5e7eb", font=("Segoe UI", 11))
chat.tag_config("bot_msg", foreground="#e5e7eb", font=("Segoe UI", 11))

# =============================
# ÁREA DE DIGITAÇÃO (barra fixa)
# =============================
frame_input = tk.Frame(janela, bg="#020617", height=90)
frame_input.pack(fill="x", padx=20, pady=(0,20))
frame_input.pack_propagate(False)

entrada = tk.Entry(
    frame_input,
    font=("Segoe UI", 12),
    bg="#f8fafc",
    fg="#111827",
    bd=0
)
entrada.pack(side="left", fill="x", expand=True, ipady=12, padx=(0,10))

# Permite enviar a mensagem também apertando a tecla 'Enter' do teclado
janela.bind('<Return>', lambda event: enviar_pergunta())

botao_enviar = tk.Button(
    frame_input,
    text="Enviar",
    command=enviar_pergunta,
    font=("Segoe UI", 10, "bold"),
    bg="#2563eb",
    fg="white",
    activebackground="#1d4ed8",
    activeforeground="white",
    bd=0,
    padx=25,
    pady=10,
    cursor="hand2"
)
botao_enviar.pack(side="right")

# Faz o assistente iniciar exibindo a ajuda na tela assim que o app abre
adicionar_mensagem("Assistente", "Olá! Sou o seu Assistente Jurídico. Como posso ajudar hoje?\n\n" + responder_pergunta("ajuda"))

janela.mainloop()