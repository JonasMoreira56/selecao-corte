import os
import pandas as pd
from flask import Flask, request, render_template, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
import numpy as np # Usado para o valor de PI
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash



# --- Configuração Inicial ---
app = Flask(__name__)
# Define as pastas para upload e arquivos processados
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
VOLUME_FATOR = 0.001602
VOLUME_EXPOENTE = 1.9

# Garante que as pastas existam
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# --- Função para aplicar as regras de negócio ---
def processar_arquivo_excel(caminho_arquivo, nome_arquivo_saida):
    """
    Lê um arquivo Excel, aplica as regras de negócio e salva um novo arquivo.
    """
    # Carrega a planilha em um DataFrame do Pandas
    df = pd.read_excel(caminho_arquivo)

    # --- ATENÇÃO: Substitua os nomes das colunas pelos nomes reais do seu arquivo ---
    # Exemplo: Se sua coluna de CAP se chama "Circunferência", use 'Circunferência'
    coluna_cap = 'CAP'  # Nome da coluna com a Circunferência a Altura do Peito
    coluna_g = 'DAP'      # Nome da coluna 'G' mencionada na fórmula da classe de diâmetro
    coluna_fator = 'FATOR'      # Nome da coluna 'UT' mencionada na fórmula da classe de diâmetro
            
    
    # --- 1. Cálculo do DAP a partir do CAP ---
    # Fórmula: DAP = CAP / π
    df['DAP'] = df[coluna_cap] / np.pi
    # Formatando para 2 casas decimais, por exemplo
    df['DAP'] = df['DAP'].round(0)
    
    # Manter o valor de ajuste da coluna FATOR na nova tabela
    df['FATOR'] = df[coluna_fator].apply(lambda x: f"{float(x):.2f}")  # Se necessário, ajuste o nome da coluna 'UT'
    
    # Remover coluna fid
    df = df.drop(columns=['fid'])
    
    # --- 2. Cálculo da Classe Diamétrica ---
    # A fórmula do Excel: =INT(G55/10)*10 & "-" & (INT(G55/10)*10 + 10)
    # Convertida para Pandas:
    limite_inferior = ((df[coluna_g] // 10) * 10).astype(int)
    limite_superior = (limite_inferior + 10).astype(int)
    #df['CLASSE DIAMETRICA'] = limite_inferior.astype(str) + '-' + limite_superior.astype(str)
    
    classe_diametrica = limite_inferior.astype(str) + '-' + limite_superior.astype(str)
    # Se o valor do DAP for maior que 100, mostra ">100"
    #df['CLASSE DIAMETRICA'] = np.where(df[coluna_g] > 100, '>100', classe_diametrica)
    df['CLASSE DIAMETRICA'] = classe_diametrica
    
    # --- 3. Cálculo do Volume do Iventário ---
    # Fórmula: VOLUME INVENTARIO = 0,001602 * (DAP^1,9)
    df['VOLUME INVENTARIO'] = VOLUME_FATOR * (df['DAP'] ** VOLUME_EXPOENTE)
    df['VOLUME INVENTARIO'] = df['VOLUME INVENTARIO'].apply(lambda x: f"{float(x):.2f}")
    #print(f"VOLUME INVENTARIO: {df['VOLUME INVENTARIO']}")  # Debug: Verifica os valores calculados de volume

    # --- 5. Calculo do volume corrigido ---
    df['VOLUME INVENTARIO'] = pd.to_numeric(df['VOLUME INVENTARIO'], errors='coerce')
    df['FATOR'] = pd.to_numeric(df['FATOR'], errors='coerce')
    df['VOLUME CORRIGIDO'] = (df['VOLUME INVENTARIO'] * df['FATOR']).map(lambda x: f"{x:.2f}")
    
    #  --- 6. Tratamento da coluna Data ---
    df['DATA INVENTARIO'] = pd.to_datetime(df['DATA INVENTARIO']).dt.strftime('%d/%m/%Y')
    
        
    
    #print(f"DAP:  {df['DAP']}")  # Debug: Verifica os valores calculados de DAP
    #print(f"CLASSE DIAMETRICA  {df['CLASSE DIAMETRICA']}")  # Debug: Verifica as classes diamétricas calculadas

    # --- 4. Criação dos campos "Categoria" e "Situação Final" ---
    # --- 4. Cálculo da Área de Preservação Permanente (APP) ---
    # df['APP'] = np.where(df['DAP'] >= 50, 'SIM', 'NÃO')
    df['Categoria'] = np.where(df['APP'].str.upper() == 'NÃO', 'Dentro do Plano', 'Fora do Plano')
    df['Situação Final'] = 'Pendente de Análise' 
    '''
    PORTA SEMENTE
    REMANESCENTE DE FUTURO - Possui o diametro pequeno e não podem ser selecionada pra corte
    PROTEGIDA - Dentro da APP
    PROTEGIDA POR LEI - ANDIROBA / COPAIBA / SERINGA / CASTANHEIRA / PAU ROSA
    QUALIDADE 3 - NÃO SERVE PARA SERRARIA
    FORA DO PLANO DE CORTE
    SELECIONADA PARA CORTE  
    
    '''
    
    
    
    # Salva o DataFrame modificado em um novo arquivo Excel
    caminho_saida = os.path.join(app.config['PROCESSED_FOLDER'], nome_arquivo_saida)
    # O `index=False` é crucial para não adicionar uma coluna de índice ao Excel
    df.to_excel(caminho_saida, index=False)
    
    
    
    return nome_arquivo_saida

# --- Rotas da Aplicação Flask ---

@app.route('/')
def index():
    """Renderiza a página inicial com o formulário de upload."""
    return render_template('index.html', resultado=None)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Recebe o arquivo, processa e redireciona para o download."""
    if 'file' not in request.files:
        return "Nenhum arquivo enviado", 400
    
    file = request.files['file']
    if file.filename == '':
        return "Nenhum arquivo selecionado", 400
        
    if file and file.filename.endswith('.xlsx'):
        # Garante um nome de arquivo seguro
        filename = secure_filename(file.filename)
        # Salva o arquivo original na pasta 'uploads'
        caminho_original = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(caminho_original)

        # Define um nome para o arquivo processado
        nome_arquivo_processado = f"selecionado_corte_{filename}"
        
        # Chama a função de processamento
        # e salva o arquivo processado na pasta 'processed'
        print(f"Processando arquivo: {caminho_original}")
        print(f"Arquivo processado será salvo como: {nome_arquivo_processado}")
        
        processar_arquivo_excel(caminho_original, nome_arquivo_processado)

        # Carrega parte dos dados para exibir no template
        df = pd.read_excel(os.path.join(app.config['PROCESSED_FOLDER'], nome_arquivo_processado))
        # # Exemplo: mostra as 5 primeiras linhas como HTML
        resultado_html = df.head().to_html(classes="results-table", index=False)
        
        # Mostra todas linhas como HTML
        #resultado_html = df.to_html(classes="results-table", index=False)
        
        # Redireciona para a página inicial com o resultado
        return render_template('index.html', resultado=resultado_html, arquivo_processado=nome_arquivo_processado)
    
    return render_template('index.html', resultado=None, erro="Formato de arquivo inválido. Por favor, envie um arquivo .xlsx")

@app.route('/download/<filename>')
def download_file(filename):
    """Fornece o arquivo processado para download."""
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename, as_attachment=True)

@app.route('/configuracoes', methods=['GET', 'POST'])
def pagina_configuracoes():
    global VOLUME_FATOR, VOLUME_EXPOENTE
    if request.method == 'POST':
        VOLUME_FATOR = float(request.form.get('fator', VOLUME_FATOR))
        VOLUME_EXPOENTE = float(request.form.get('expoente', VOLUME_EXPOENTE))
        return redirect(url_for('pagina_configuracoes'))
    
    # Passe os valores atuais de min_dap e max_dap se desejar
    min_dap = 50  # ou recupere de algum lugar
    max_dap = 100 # ou recupere de algum lugar
    return render_template(
        'config.html',
        min_dap=min_dap,
        max_dap=max_dap,
        fator=VOLUME_FATOR,
        expoente=VOLUME_EXPOENTE)

@app.route('/novo-projeto')
def novo_projeto():
    return render_template('index.html', resultado=None)


if __name__ == '__main__':
    # Inicia o servidor Flask
    app.run(debug=True)