import tkinter as tk
from tkinter import filedialog
import fitz  # PyMuPDF
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
import random
import string
import shutil


# Variáveis globais
doc = None
pagina_atual = 0
imagens_pdf = []  
thumbnails = []  
zoom_factor = 1.0  
modo_pagina_unica = False  
paginas_selecionadas = set()  

def selecionar_pdf():
    caminho_pdf = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if caminho_pdf:
        carregar_pdf(caminho_pdf)

def carregar_pdf(caminho_pdf):
    global doc, pagina_atual, imagens_pdf, thumbnails, paginas_selecionadas
    if caminho_pdf.lower().endswith('.pdf'):
        doc = fitz.open(caminho_pdf)
        pagina_atual = 0
        imagens_pdf = []
        thumbnails = []
        paginas_selecionadas = set()
        for pagina_num in range(len(doc)):
            pagina = doc.load_page(pagina_num)
            pix = pagina.get_pixmap(matrix=fitz.Matrix(zoom_factor, zoom_factor))
            img = tk.PhotoImage(data=pix.tobytes("ppm"))
            imagens_pdf.append(img)

            # Criando miniatura
            pix_thumb = pagina.get_pixmap(matrix=fitz.Matrix(0.2, 0.2))
            thumb = tk.PhotoImage(data=pix_thumb.tobytes("ppm"))
            thumbnails.append(thumb)

        atualizar_thumbnails()
        exibir_pagina(pagina_atual)

def atualizar_thumbnails():
    for widget in frame_thumbnails_inner.winfo_children():
        widget.destroy()

    for idx in range(0, len(thumbnails), 2):
        row_frame = ttk.Frame(frame_thumbnails_inner)
        row_frame.pack(fill=tk.X, pady=2)

        for col in range(2):
            if idx + col < len(thumbnails):
                
                lbl = tk.Label(row_frame, image=thumbnails[idx + col], bg="white")
                lbl.pack(side=tk.LEFT, padx=2)
                lbl.bind("<Button-1>", lambda event, i=idx + col: selecionar_pagina(i))
                lbl.bind("<Control-Button-1>", lambda event, i=idx + col: selecionar_pagina(i))
                lbl.bind("<Shift-Button-1>", lambda event, i=idx + col: selecionar_pagina(i))

                
                if idx + col in paginas_selecionadas:
                    lbl.config(bg="lightblue")  

    frame_thumbnails_inner.update_idletasks()
    frame_thumbnails_canvas.config(scrollregion=frame_thumbnails_canvas.bbox(tk.ALL))

def exibir_pagina(num_pagina):
    global pagina_atual
    if not imagens_pdf:
        return

    pagina_atual = num_pagina
    canvas.delete("all")

    img = imagens_pdf[pagina_atual]
    canvas.create_image(0, 0, anchor=tk.NW, image=img)
    canvas.config(scrollregion=canvas.bbox(tk.ALL))

    label_pagina.config(text=f"Página {pagina_atual + 1} de {len(imagens_pdf)}")

def selecionar_pagina(num_pagina):
    if num_pagina in paginas_selecionadas:
        paginas_selecionadas.remove(num_pagina)
    else:
        paginas_selecionadas.add(num_pagina)
    atualizar_thumbnails()



def extrair_paginas_selecionadas():
    if not paginas_selecionadas:
        return

    novo_doc = fitz.open()

    for num_pagina in sorted(paginas_selecionadas):
        novo_doc.insert_pdf(doc, from_page=num_pagina, to_page=num_pagina)

    caminho_pdf_original = doc.name
    nome_arquivo_original = os.path.basename(caminho_pdf_original)
    diretorio_original = os.path.dirname(caminho_pdf_original)


    nome_aleatorio = ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + ".pdf"
    caminho_salvar = os.path.join(diretorio_original, nome_arquivo_original.replace(".pdf", f"_{nome_aleatorio}.pdf"))


    novo_doc.save(caminho_salvar)
    novo_doc.close()


    paginas_para_remover = sorted(paginas_selecionadas, reverse=True)  # Remover de trás para frente para evitar erro de índice
    for pagina in paginas_para_remover:
        doc.delete_page(pagina)


    caminho_temp = os.path.join(diretorio_original, nome_arquivo_original.replace(".pdf", "_temp.pdf"))
    doc.save(caminho_temp)  # Salvar como temporário, não pode ser feito no próprio arquivo original diretamente

    try:

        shutil.move(caminho_temp, caminho_pdf_original)
    except PermissionError as e:
        print(f"Erro ao substituir o arquivo: {e}")
        return

   
    carregar_pdf(caminho_pdf_original)
    atualizar_thumbnails()

    exibir_pagina(0)

def girar_pagina():
    global doc, pagina_atual, imagens_pdf, thumbnails

    if not doc:
        return 
  
    paginas_para_girar = [pagina_atual] if not paginas_selecionadas else sorted(paginas_selecionadas)

    for num_pagina in paginas_para_girar:
        pagina = doc.load_page(num_pagina)
        rotacao_atual = pagina.rotation  
        nova_rotacao = (rotacao_atual + 90) % 360 
        pagina.set_rotation(nova_rotacao)  

    
    caminho_pdf_original = doc.name
    caminho_temp = caminho_pdf_original.replace(".pdf", "_temp.pdf")
    doc.save(caminho_temp)  

    try:
        shutil.move(caminho_temp, caminho_pdf_original)
    except PermissionError as e:
        print(f"Erro ao substituir o arquivo: {e}")
        return  

    
    carregar_pdf(caminho_pdf_original)

    
    if paginas_selecionadas:
        atualizar_thumbnails()
    else:
        exibir_pagina(pagina_atual)
def proxima_pagina():
    if pagina_atual < len(imagens_pdf) - 1:
        exibir_pagina(pagina_atual + 1)

def pagina_anterior():
    if pagina_atual > 0:
        exibir_pagina(pagina_atual - 1)

def aumentar_zoom():
    global zoom_factor
    zoom_factor += 0.2
    carregar_pdf(doc.name)

def diminuir_zoom():
    global zoom_factor
    if zoom_factor > 0.4:
        zoom_factor -= 0.2
        carregar_pdf(doc.name)

def alternar_visualizacao():
    global modo_pagina_unica, zoom_factor
    modo_pagina_unica = not modo_pagina_unica
    zoom_factor = 0.760 if modo_pagina_unica else 1.0
    carregar_pdf(doc.name)

def on_mouse_scroll(event, widget):
    widget.yview_scroll(-1 * (event.delta // 120), "units")

# Configuração da interface gráfica
janela = ttk.Window(themename="darkly")
janela.title("Visualizador de PDF")
janela.geometry("900x600")
janela.bind("<F1>", lambda event: extrair_paginas_selecionadas())
janela.bind("<F2>", lambda event: girar_pagina())

# Frame para o menu e botão "Extrair Páginas"
frame_menu = ttk.Frame(janela)
frame_menu.pack(fill=tk.X, padx=10, pady=5)


fonte_menu = ("Arial", 15)
menu_bar = tk.Menu(frame_menu)
menu_arquivo = tk.Menu(menu_bar, tearoff=0, font=fonte_menu)
menu_bar.add_cascade(label="Arquivo", menu=menu_arquivo)
menu_arquivo.add_command(label="Abrir PDF", command=selecionar_pdf)
menu_bar.add_cascade(label="Extrair Páginas", command=extrair_paginas_selecionadas)
menu_bar.entryconfig("Extrair Páginas", font=fonte_menu)
menu_bar.add_cascade(label="Girar Páginas", command=girar_pagina)
menu_bar.entryconfig("Girar Páginas", font=fonte_menu)


# Adicionar o menu à janela
janela.config(menu=menu_bar)

frame_principal = ttk.Frame(janela, padding=10)
frame_principal.pack(fill=tk.BOTH, expand=True)

# Área de miniaturas com Scrollbar
frame_thumbnails = ttk.Frame(frame_principal)
frame_thumbnails.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

frame_thumbnails_canvas = tk.Canvas(frame_thumbnails)
frame_thumbnails_canvas.pack(side=tk.LEFT, fill=tk.Y, expand=True)

scrollbar_thumbnails = ttk.Scrollbar(frame_thumbnails, orient=tk.VERTICAL, command=frame_thumbnails_canvas.yview, bootstyle="primary")
scrollbar_thumbnails.pack(side=tk.RIGHT, fill=tk.Y)
frame_thumbnails_canvas.configure(yscrollcommand=scrollbar_thumbnails.set)

frame_thumbnails_inner = ttk.Frame(frame_thumbnails_canvas)
frame_thumbnails_canvas.create_window((0, 0), window=frame_thumbnails_inner, anchor=tk.NW)
frame_thumbnails_canvas.bind_all("<MouseWheel>", lambda event: on_mouse_scroll(event, frame_thumbnails_canvas))

frame_visualizador = ttk.Frame(frame_principal)
frame_visualizador.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

canvas = tk.Canvas(frame_visualizador)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(frame_visualizador, orient=tk.VERTICAL, command=canvas.yview, bootstyle="primary")
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind_all("<MouseWheel>", lambda event: on_mouse_scroll(event, canvas))

# Manter os controles visíveis
frame_controles = ttk.Frame(janela, padding=10)
frame_controles.pack(fill=tk.X)

botao_anterior = ttk.Button(frame_controles, text="Anterior", command=pagina_anterior, bootstyle=SECONDARY)
botao_anterior.pack(side=tk.LEFT, padx=5)

botao_proximo = ttk.Button(frame_controles, text="Próxima", command=proxima_pagina, bootstyle=SECONDARY)
botao_proximo.pack(side=tk.LEFT, padx=5)

label_pagina = ttk.Label(frame_controles, text="Página 0 de 0", font=("Helvetica", 12))
label_pagina.pack(side=tk.LEFT, padx=10)

botao_zoom_mais = ttk.Button(frame_controles, text="+ Zoom", command=aumentar_zoom, bootstyle=SUCCESS)
botao_zoom_mais.pack(side=tk.RIGHT, padx=5)

botao_zoom_menos = ttk.Button(frame_controles, text="- Zoom", command=diminuir_zoom, bootstyle=WARNING)
botao_zoom_menos.pack(side=tk.RIGHT, padx=5)

botao_modo_visualizacao = ttk.Button(frame_controles, text="Alternar Modo", command=alternar_visualizacao,
                                     bootstyle=INFO)
botao_modo_visualizacao.pack(side=tk.RIGHT, padx=5)

janela.mainloop()
