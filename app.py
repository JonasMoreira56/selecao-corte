import os
import pandas as pd
from flask import Flask, request, render_template, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
import numpy as np # Usado para o valor de PI
from flask_sqlalchemy import SQLAlchemy
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
    coluna_especie = 'ESPECIE'        
    
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
    
    # --- 4. Classifica Arvores de Preservação Permanente (APP) ---
    # df['APP'] = np.where(df['DAP'] >= 50, 'SIM', 'NÃO')
    df['CLASSIFICAÇÃO'] = np.where(df['APP'].str.upper() == 'NÃO', 'Dentro do Plano', 'Fora do Plano')
    df['Situação Final'] = 'Aguardando Análise' 
    
    # --- 5. Correção no nome dos campos de observação
    # DE = Diametro Estimado / NULO = OK / CT = Comercial Terra
    if 'OBSERVAÇÃO' in df.columns:
        df['OBSERVAÇÃO'] = df['OBSERVAÇÃO'].replace('NULO','OK')
        
   
    # Salva o DataFrame modificado em um novo arquivo Excel
    caminho_saida = os.path.join(app.config['PROCESSED_FOLDER'], nome_arquivo_saida)
    # O `index=False` é crucial para não adicionar uma coluna de índice ao Excel
    df.to_excel(caminho_saida, index=False)
    
    return nome_arquivo_saida

def classificar_ut(nome_arquivo_processado):
    caminho_arquivo = os.path.join(app.config['PROCESSED_FOLDER'], nome_arquivo_processado)

    # Carrega a planilha do arquivo de sa
    df = pd.read_excel(caminho_arquivo)
    

    # PORTA SEMENTE
    # REMANESCENTE DE FUTURO - Possui o diametro pequeno e não podem ser selecionada pra corte
    # PROTEGIDA - Dentro da APP
    # PROTEGIDA POR LEI - ANDIROBA / COPAIBA / SERINGA / CASTANHEIRA / PAU ROSA
    # QUALIDADE 3 - NÃO SERVE PARA SERRARIA
    # FORA DO PLANO DE CORTE
    # SELECIONADA PARA CORTE  
      
    # CLASSIFICAÇÃO ESPECIE
    #Maior que 50       
        # mAIOR QUE 70
        #ipam - IPRO
    
    # MAIOR QUE 80
    # CUMA - CUVE 
    
    # menor que 50 para corte (PORTE)
    # (30 - 50 DE DAP) SELECIONADA PARA CORTE
    # QUALIDADE 3 - REMANESCENTE QUALIDADE INFERIOR
    # PRA ESSA ESPECIE < 30 -> REMANESCENTE FUTURO
    # >50 REMANESCENTE FORA DO PLANO DE CORTE

    # ACAR - ABIU - MATA

    # Seleciona arvores que não estão na APP
    
    # for valor in df['UT'].unique():
    #     tabela = df[df['UT'] == valor]
        
    #     # Filtra apenas as linhas com DAP >= 50
    #     selecionadas_corte = tabela[tabela['DAP'] >= 50]
    #     if not selecionadas_corte.empty:
    #         print("MAIOR QUE 50")
    #         print(selecionadas_corte.head())  # Mostra as primeiras linhas selecionadas para corte
        
    #     else:
    #         print("MENOR QUE 50")   
    #         if tabela[(tabela['ESPECIE'])] == "ACAR" or "ABIU" or "MATA":
    #             if tabela[df['QUALIDADE']] == 3:
    #                 print('REMANESCENTE QUALIDADE INFERIOR')
    #             if 30 <= tabela[df['DAP']] <= 50:
    #                 print('SELECIONADA PARA CORTE')
    #             elif tabela[df['DAP']]  < 30:
    #                 print ('REMANESCENTE FUTURO')
    #             elif tabela[df['DAP']] > 50:
    #                 print('REMANESCENTE FORA DO PLANO DE CORTE')
    #         return 'NÃO SE APLICA'
        
      
    #     # Seleciona árvores com DAP > 70 e espécie IPAM ou IPRO
    #     ipam_ipro = tabela[
    #         (tabela['DAP'] > 70) & 
    #         (tabela['ESPECIE'].isin(['IPAM', 'IPRO']))
    #     ]
    #     if not ipam_ipro.empty:
    #         print("MAIOR QUE 70 - IPAM ou IPRO")
    #         print(ipam_ipro.head())
            
    #     # Seleciona árvores com DAP > 80 e espécie CUMA ou CUVE
    #     cuma_cuve = tabela[
    #         (tabela['DAP'] > 80) & 
    #         (tabela['ESPECIE'].isin(['CUMA', 'CUVE']))
    #     ]
    #     if not cuma_cuve.empty:
    #         print("MAIOR QUE 80 - CUMA ou CUVE")
    #         print(cuma_cuve.head())
        
    
    #     print(f"Tabela para UT = {valor}:")
    #     #print(tabela.head())  # Mostra as primeiras linhas da tabela filtrada
    #     print("-" * 30)
   
    
    
    '''
    for valor in df['UT'].unique():
        tabela = df[df['UT'] == valor]
        
        # Filtra apenas as linhas com DAP >= 50
        selecionadas_corte = tabela[tabela['DAP'] >= 50]
        if not selecionadas_corte.empty:
            print("MAIOR QUE 50")
            print(selecionadas_corte.head())
        else:
            print("MENOR QUE 50")
            # Corrigindo a condição para múltiplas espécies
            especies_alvo = ["ACAR", "ABIU", "MATA"]
            filtro_especie = tabela['ESPECIE'].isin(especies_alvo)
            filtro_qualidade = tabela['QUALIDADE'] == 3
            filtro_dap_30_50 = (tabela['DAP'] >= 30) & (tabela['DAP'] <= 50)
            filtro_dap_menor_30 = tabela['DAP'] < 30
            filtro_dap_maior_50 = tabela['DAP'] > 50

            if filtro_especie.any():
                if filtro_qualidade.any():
                    print('REMANESCENTE QUALIDADE INFERIOR')
                if filtro_dap_30_50.any():
                    print('SELECIONADA PARA CORTE')
                elif filtro_dap_menor_30.any(): '''
    
    # Exemplo: adiciona uma coluna de teste
    df['TESTE'] = 'ATENDIDO'
    
    # Salva de volta
    # df.to_excel(caminho_arquivo, index=False)
                       
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

@app.route('/classificar/<arquivo>', methods=['POST'])
def classificar_arquivo(arquivo):
    classificar_ut(arquivo)
    # Recarrega o DataFrame atualizado
    df = pd.read_excel(os.path.join(app.config['PROCESSED_FOLDER'], arquivo))
    resultado_html = df.head().to_html(classes="results-table", index=False)
    return render_template('index.html', resultado=resultado_html, arquivo_processado=arquivo)

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