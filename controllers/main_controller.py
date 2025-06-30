
from models.arquivo import criar_tabela_arquivos, salvar_arquivo, buscar_arquivo_por_nome
from io import BytesIO
from flask import Blueprint, current_app, render_template, request, redirect, url_for, send_from_directory
#from models.processamento import processar_arquivo_excel, classificar_ut
import os
import sqlite3
import pandas as pd
from werkzeug.utils import secure_filename
from flask import send_file
from models.processamento import processar_arquivo_excel_bytes, classificar_ut_bytes


criar_tabela_arquivos()
main = Blueprint('main', __name__)

# Lista inicial de árvores protegidas 
arvores_protegidas = ["ANDIROBA", "COPAIBA", "SERINGUEIRA", "CASTANHEIRA", "PAU ROSA"]

# Rotas e lógica de controle
# --- Rotas da Aplicação Flask --
@main.route('/')
def index():
    """Renderiza a página inicial com o formulário de upload."""
    return render_template('index.html', resultado=None)



@main.route('/upload', methods=['POST'])
def upload_file():
    
    if 'file' not in request.files:
        return "Nenhum arquivo enviado", 400

    file = request.files['file']  # <-- Adicione esta linha

    if file.filename == '':
        return "Nenhum arquivo selecionado", 400
    
    # ...verificações...
    if file and file.filename.endswith('.xlsx'):
        filename = secure_filename(file.filename)
        conteudo = file.read()
        mimetype = file.mimetype

        # Salva o original
        salvar_arquivo(filename, conteudo, mimetype)

        # Processa e salva o processado no banco
        nome_arquivo_saida = f"selecao_UPA_{filename}"
        conteudo_processado = processar_arquivo_excel_bytes(conteudo, nome_arquivo_saida, mimetype)

        # Exemplo: mostrar preview do processado
        df = pd.read_excel(BytesIO(conteudo_processado))
        resultado_html = df.head().to_html(classes="results-table", index=False)
        return render_template('index.html', resultado=resultado_html, arquivo_processado=nome_arquivo_saida)
# @main.route('/upload', methods=['POST'])
# def upload_file():
#     """Recebe o arquivo, processa e redireciona para o download."""
#     if 'file' not in request.files:
#         return "Nenhum arquivo enviado", 400
    
#     file = request.files['file']
#     if file.filename == '':
#         return "Nenhum arquivo selecionado", 400
        
#     if file and file.filename.endswith('.xlsx'):
#         # Garante um nome de arquivo seguro
#         filename = secure_filename(file.filename)
#         # Salva o arquivo original na pasta 'uploads'
#         caminho_original = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
#         file.save(caminho_original)

#         # Define um nome para o arquivo processado
#         nome_arquivo_processado = f"selecao_UPA_{filename}"
        
#         # Chama a função de processamento
#         # e salva o arquivo processado na pasta 'processed'
#         print(f"Processando arquivo: {caminho_original}")
#         print(f"Arquivo processado será salvo como: {nome_arquivo_processado}")
        
#         processar_arquivo_excel(caminho_original, nome_arquivo_processado, current_app.config['PROCESSED_FOLDER'])

#         # Carrega parte dos dados para exibir no template
#         df = pd.read_excel(os.path.join(current_app.config['PROCESSED_FOLDER'], nome_arquivo_processado))
#         # # Exemplo: mostra as 5 primeiras linhas como HTML
#         resultado_html = df.head().to_html(classes="results-table", index=False)
        
#         # Mostra todas linhas como HTML
#         #resultado_html = df.to_html(classes="results-table", index=False)
        
#         # Redireciona para a página inicial com o resultado
#         return render_template('index.html', resultado=resultado_html, arquivo_processado=nome_arquivo_processado)
    
#     return render_template('index.html', resultado=None, erro="Formato de arquivo inválido. Por favor, envie um arquivo .xlsx")

@main.route('/classificar/<arquivo>', methods=['POST'])
def classificar_arquivo(arquivo):
    conteudo_classificado = classificar_ut_bytes(arquivo)
    if conteudo_classificado:
        df = pd.read_excel(BytesIO(conteudo_classificado))
        resultado_html = df.head(10).to_html(classes="results-table", index=False)
        return render_template('resultado.html', resultado=resultado_html, arquivo_processado=arquivo)
    return "Arquivo não encontrado", 404

# @main.route('/download/<filename>')
# def download_file(filename):
#     """Fornece o arquivo processado para download."""
#     return send_from_directory(current_app.config['PROCESSED_FOLDER'], filename, as_attachment=True)

@main.route('/download/<filename>')
def download_file(filename):
    conteudo, mimetype = buscar_arquivo_por_nome(filename)
    if conteudo:
        return send_file(BytesIO(conteudo), download_name=filename, mimetype=mimetype, as_attachment=True)
    return "Arquivo não encontrado", 404

@main.route('/config', methods=['GET'])
def config():
    return render_template('config.html', arvores_protegidas=arvores_protegidas)

@main.route('/update_protegidas', methods=['POST'])
def update_protegidas():
    global arvores_protegidas
    # Recebe a lista do formulário
    arvores = request.form.getlist('arvores[]')
    # Remove vazios e padroniza para maiúsculas
    arvores_protegidas = [a.strip().upper() for a in arvores if a.strip()]
    return redirect(url_for('main.config'))

@main.route('/novo-projeto')
def novo_projeto():
    return render_template('index.html', resultado=None)