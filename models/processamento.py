# import os

# # --- Função para aplicar as regras de negócio e salvar localmente ---
# def processar_arquivo_excel(caminho_arquivo, nome_arquivo_saida, processed_folder):
#     """
#     Lê um arquivo Excel, aplica as regras de negócio e salva um novo arquivo.
#     """
#     caminho_saida = os.path.join(processed_folder, nome_arquivo_saida)
#     # Carrega a planilha em um DataFrame do Pandas
#     df = pd.read_excel(caminho_saida)

#     # --- ATENÇÃO: Substitua os nomes das colunas pelos nomes reais do seu arquivo ---
#     # Exemplo: Se sua coluna de CAP se chama "Circunferência", use 'Circunferência'
#     coluna_cap = 'CAP'  # Nome da coluna com a Circunferência a Altura do Peito
#     coluna_g = 'DAP'      # Nome da coluna 'G' mencionada na fórmula da classe de diâmetro
#     coluna_fator = 'FATOR'      # Nome da coluna 'UT' mencionada na fórmula da classe de diâmetro      
    
#     # --- 1. Cálculo do DAP a partir do CAP ---
#     # Fórmula: DAP = CAP / π
#     df['DAP'] = df[coluna_cap] / np.pi
#     # Formatando para 2 casas decimais, por exemplo
#     df['DAP'] = df['DAP'].round(0)
    
#     # Manter o valor de ajuste da coluna FATOR na nova tabela
#     df['FATOR'] = df[coluna_fator].apply(lambda x: f"{float(x):.2f}")  # Se necessário, ajuste o nome da coluna 'UT'
        
#     # --- 2. Cálculo da Classe Diamétrica ---
#     # A fórmula do Excel: =INT(G55/10)*10 & "-" & (INT(G55/10)*10 + 10)
#     # Convertida para Pandas:
#     limite_inferior = ((df[coluna_g] // 10) * 10).astype(int)
#     limite_superior = (limite_inferior + 10).astype(int)
#     classe_diametrica = limite_inferior.astype(str) + '-' + limite_superior.astype(str)
    
#     # Se o DAP for maior que 100, mostra ">100"
#     classe_diametrica = np.where(df['DAP'] >= 100, '>100', classe_diametrica)
#     df['CLASSE DIAMETRICA'] = classe_diametrica
    
#     # --- 3. Cálculo do Volume do Iventário ---
#     # Fórmula: VOLUME INVENTARIO = 0,001602 * (DAP^1,9)
#     df['VOLUME INVENTARIO'] = VOLUME_FATOR * (df['DAP'] ** VOLUME_EXPOENTE)
#     df['VOLUME INVENTARIO'] = df['VOLUME INVENTARIO'].apply(lambda x: f"{float(x):.2f}")
#     #print(f"VOLUME INVENTARIO: {df['VOLUME INVENTARIO']}")  # Debug: Verifica os valores calculados de volume

#     # --- 5. Calculo do volume corrigido ---
#     df['VOLUME INVENTARIO'] = pd.to_numeric(df['VOLUME INVENTARIO'], errors='coerce')
#     df['FATOR'] = pd.to_numeric(df['FATOR'], errors='coerce')
#     df['VOLUME CORRIGIDO'] = (df['VOLUME INVENTARIO'] * df['FATOR']).map(lambda x: f"{x:.2f}")
    
#     #  --- 6. Tratamento da coluna Data ---
#     df['DATA INVENTARIO'] = pd.to_datetime(df['DATA INVENTARIO']).dt.strftime('%d/%m/%Y')
    
#     #print(f"DAP:  {df['DAP']}")  # Debug: Verifica os valores calculados de DAP
#     #print(f"CLASSE DIAMETRICA  {df['CLASSE DIAMETRICA']}")  # Debug: Verifica as classes diamétricas calculadas

#     # --- 4. Classifica Arvores de Preservação Permanente (APP) e Protegidas ---
#     especies_protegidas = ["SERI", "ANDI", "COPA", "CAST", "PARO", "PAA", "SOVA"]
    
#     condicoes = [
#         df['APP'].str.upper() == 'SIM',
#         df['ESPECIE'].str.upper().isin(especies_protegidas)
#     ]
#     resultados = [
#         'Arvore na area de preservacao permanente',
#         'Arvore protegida'
#     ]

#     df['CLASSIFICAÇÃO'] = np.select(condicoes, resultados, default='Pendente de Analise')
    
#     # --- 5. Correção no nome dos campos de observação
#     # DE = Diametro Estimado / NULO = OK / CT = Comercial Terra
#     if 'OBSERVAÇÃO' in df.columns:
#         df['OBSERVAÇÃO'] = df['OBSERVAÇÃO'].replace('NULO','OK')
        
#     # Salva o DataFrame modificado em um novo arquivo Excel
#     caminho_saida = os.path.join(processed_folder, nome_arquivo_saida)
#     # O `index=False` é crucial para não adicionar uma coluna de índice ao Excel
#     df.to_excel(caminho_saida, index=False)
    
#     return nome_arquivo_saida

# def classificar_ut(nome_arquivo_processado, processed_folder):
#     caminho_arquivo = os.path.join(processed_folder, nome_arquivo_processado)

#     # Carrega a planilha do arquivo de sa
#     df = pd.read_excel(caminho_arquivo)
    
#     for valor in df['UT'].unique():
#         tabela = df[df['UT'] == valor]
        
#         # Filtra apenas árvores que NÃO são APP nem protegidas
#         filtro_nao_app_protegida = ~(
#             (tabela['CLASSIFICAÇÃO'] == 'Arvore na area de preservacao permanente') |
#             (tabela['CLASSIFICAÇÃO'] == 'Arvore protegida')
#         )
#         tabela_filtrada = tabela[filtro_nao_app_protegida]
#         idx = tabela_filtrada.index
        
#         """
#         Regras de classificação aplicadas por UT para as espécies do tipo porte ACAR, ABIU e MATA:

#         - Se QUALIDADE == 3: classifica como 'REMANESCENTE QUALIDADE INFERIOR'
#           (árvore de qualidade inferior, não serve para serraria)
#         - Se 30 <= DAP <= 50: classifica como 'SELECIONADA PARA CORTE'
#           (árvore com porte adequado para corte)
#         - Se DAP < 30: classifica como 'REMANESCENTE FUTURO'
#           (árvore jovem, remanescente para o futuro)
#         - Se DAP > 50: classifica como 'REMANESCENTE FORA DO PLANO DE CORTE'
#           (árvore fora do plano de corte por porte elevado)

#         Observação: Essas regras só são aplicadas para árvores que NÃO estão em APP
#         (Área de Preservação Permanente) e NÃO são protegidas.
#         """
#         especies_porte = ["ACAR", "ABIU", "MATA"]
#         especies_acima70 = ["IPAM","IPRO"]
#         especies_acima80 = ["CUMA","CUVE"]
        
#         condicoes = [
#             (tabela_filtrada['ESPECIE'].isin(especies_acima70)) & (tabela_filtrada['DAP'] >= 70) & (tabela_filtrada['QUALIDADE'] < 3),
#             (tabela_filtrada['ESPECIE'].isin(especies_acima80)) & (tabela_filtrada['DAP'] >= 80) & (tabela_filtrada['QUALIDADE'] < 3),
#             (tabela_filtrada['ESPECIE'].isin(especies_porte)) & (tabela_filtrada['QUALIDADE'] == 3),
#             (tabela_filtrada['ESPECIE'].isin(especies_porte)) & (tabela_filtrada['DAP'] >= 30) & (tabela_filtrada['DAP'] <= 50),
#             (tabela_filtrada['ESPECIE'].isin(especies_porte)) & (tabela_filtrada['DAP'] < 30),
#             (tabela_filtrada['DAP'] >= 50) & (tabela_filtrada['QUALIDADE'] < 3),
#             (tabela_filtrada['DAP'] < 50) & (tabela_filtrada['QUALIDADE'] < 3),
#             tabela_filtrada['QUALIDADE'] == 3
#         ]
#         resultados = [
#             'Arvore Selecionada para corte',
#             'Arvore Selecionada para corte',
#             'Arvore Remanescente Qualidade Fuste 3',
#             'Arvore Selecionada para corte',
#             'Arvore Remanescente de Futuro',
#             'Arvore Selecionada para corte',
#             'Arvore Remanescente de Futuro',
#             'Arvore Remanescente Qualidade Fuste 3'
#         ]
        
#         '''
#         Destinação:
#             - ARVORE NA AREA DE PRESERVAÇÃO PERMANENTE
#             - ARVORE PROTEGIDA
#             - REMANESCENTE QUALIDADE INFERIOR PARA ARVORES GERAIS COM QUALIDADE 3
#             - SELECIONADA PARA CORTE
#             - REMANESCENTE FUTURO      
#         '''
        
#         # Aplica as classificações apenas nas linhas do grupo atual (UT)
#         classificacoes = np.select(condicoes, resultados, default=df.loc[idx, 'CLASSIFICAÇÃO'])
#         df.loc[idx, 'CLASSIFICAÇÃO'] = classificacoes
    
#     # Se o valor do DAP for maior que 100, mostra ">100"
                
#     # Salva o DataFrame atualizado
#     df.to_excel(caminho_arquivo, index=False)


# -- -Salva o arquivo processado no banco de dados ---
from io import BytesIO
import pandas as pd
import numpy as np
from models.arquivo import buscar_arquivo_por_nome, salvar_arquivo

VOLUME_FATOR = 0.001602
VOLUME_EXPOENTE = 1.9

def processar_arquivo_excel_bytes(conteudo_bytes, nome_arquivo_saida, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
    """
    Lê um arquivo Excel em memória, aplica as regras de negócio e retorna o arquivo processado em memória.
    Também salva o arquivo processado no banco de dados.
    """
    # Carrega a planilha em um DataFrame do Pandas
    df = pd.read_excel(BytesIO(conteudo_bytes))

    coluna_cap = 'CAP'
    coluna_dap = 'DAP'
    coluna_fator = 'FATOR'
    
    # remover colunas desnecessárias
    df['fid'] = df['fid'].astype(str)
    df = df.drop(columns=['fid'], errors='ignore')
    
    df['DAP'] = df[coluna_cap] / np.pi
    df['DAP'] = df['DAP'].round(0)
    df['FATOR'] = df[coluna_fator].apply(lambda x: f"{float(x):.2f}")

    limite_inferior = ((df[coluna_dap] // 10) * 10).astype(int)
    limite_superior = (limite_inferior + 10).astype(int)
    classe_diametrica = limite_inferior.astype(str) + '-' + limite_superior.astype(str)
    classe_diametrica = np.where(df['DAP'] >= 100, '>100', classe_diametrica)
    df['CLASSE DIAMETRICA'] = classe_diametrica

    df['VOLUME INVENTARIO'] = VOLUME_FATOR * (df['DAP'] ** VOLUME_EXPOENTE)
    df['VOLUME INVENTARIO'] = df['VOLUME INVENTARIO'].apply(lambda x: f"{float(x):.2f}")

    df['VOLUME INVENTARIO'] = pd.to_numeric(df['VOLUME INVENTARIO'], errors='coerce')
    df['FATOR'] = pd.to_numeric(df['FATOR'], errors='coerce')
    df['VOLUME CORRIGIDO'] = (df['VOLUME INVENTARIO'] * df['FATOR']).map(lambda x: f"{x:.2f}")

    df['DATA INVENTARIO'] = pd.to_datetime(df['DATA INVENTARIO']).dt.strftime('%d/%m/%Y')

    especies_protegidas = ["SERI", "ANDI", "COPA", "CAST", "PARO", "PAAM", "SOVA", "PREC"]
    condicoes = [
        df['APP'].str.upper() == 'SIM',
        df['ESPECIE'].str.upper().isin(especies_protegidas)
    ]
    resultados = [
        'Arvore na area de preservacao permanente',
        'Arvore protegida'
    ]
    df['CLASSIFICAÇÃO'] = np.select(condicoes, resultados, default='Selecionada para corte')

    if 'OBSERVAÇÃO' in df.columns:
        df['OBSERVAÇÃO'] = df['OBSERVAÇÃO'].replace('NULO','Não Possui')
        

    # Nova coluna DMC: verifica o critério por espécie
    def verifica_dmc(row):
        especie = row['ESPECIE'].upper()
        dap = row['DAP']
        if especie in ['ABIU', 'MATA']:
            return 'Atende' if dap >= 30 else 'Não Atende'
        elif especie == 'ACAR':
            return 'Atende' if dap >= 25 else 'Não Atende'
        elif especie in ['CUMA', 'CUVE']:
            return 'Atende' if dap >= 80 else 'Não Atende'
        elif especie in ['IPRO', 'IPAM']:
            return 'Atende' if dap >= 70 else 'Não Atende'
        elif row['CLASSIFICAÇÃO'] == 'Arvore protegida':
            return 'Protegida'
        else:
            return 'Atende' if dap >= 50 else 'Não Atende'

    df['DMC'] = df.apply(verifica_dmc, axis=1)
    
    # --- Fim do processamento ---

    # Salva o DataFrame modificado em memória
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    conteudo_processado = output.read()

    # Salva o arquivo processado no banco de dados
    salvar_arquivo(nome_arquivo_saida, conteudo_processado, mimetype)

    return conteudo_processado  # Se quiser retornar para download ou uso imediato

def classificar_ut_bytes(nome_arquivo_processado, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
    """
    Lê um arquivo Excel do banco (em bytes), aplica as regras de classificação UT,
    salva o resultado processado no banco e retorna os bytes do novo arquivo.
    """
    # Busca o arquivo processado no banco
    conteudo, _ = buscar_arquivo_por_nome(nome_arquivo_processado)
    if not conteudo:
        return None  # Ou lance uma exceção

    df = pd.read_excel(BytesIO(conteudo))

    for valor in df['UT'].unique():
        tabela = df[df['UT'] == valor]
        print(f"\n--- UT: {valor} ---")

        # Filtra apenas árvores que NÃO são APP nem protegidas
        filtro_nao_app_protegida = ~(
            (tabela['CLASSIFICAÇÃO'] == 'Arvore na area de preservacao permanente') |
            (tabela['CLASSIFICAÇÃO'] == 'Arvore protegida')
        )
        tabela_filtrada = tabela[filtro_nao_app_protegida]
        idx = tabela_filtrada.index

        especies_porte = ["ACAR", "ABIU", "MATA"]
        especies_acima70 = ["IPAM", "IPRO"]
        especies_acima80 = ["CUMA", "CUVE"]

        condicoes = [
            # 1. Espécies acima de 70cm de DAP e qualidade < 3
            (tabela_filtrada['ESPECIE'].isin(especies_acima70)) & (tabela_filtrada['DAP'] >= 70) & (tabela_filtrada['QUALIDADE'] < 3),
            # 1b. Espécies acima de 70cm de DAP e qualidade < 3, mas DAP < 70 (Remanescente Futuro)
            (tabela_filtrada['ESPECIE'].isin(especies_acima70)) & (tabela_filtrada['DAP'] < 70),
            # 2. Espécies acima de 80cm de DAP e qualidade < 3
            (tabela_filtrada['ESPECIE'].isin(especies_acima80)) & (tabela_filtrada['DAP'] >= 80) & (tabela_filtrada['QUALIDADE'] < 3),
            # 2b. Espécies acima de 80cm de DAP e qualidade < 3, mas DAP < 80 (Remanescente Futuro)
            (tabela_filtrada['ESPECIE'].isin(especies_acima80)) & (tabela_filtrada['DAP'] < 80),
            # 3. Espécies de porte com qualidade 3 (sempre remanescente)
            (tabela_filtrada['ESPECIE'].isin(especies_porte)) & (tabela_filtrada['QUALIDADE'] == 3),
            # 4. Espécies de porte com DAP entre 30 e 50
            (tabela_filtrada['ESPECIE'].isin(especies_porte)) & (tabela_filtrada['DAP'] >= 30) & (tabela_filtrada['DAP'] <= 50),
            (tabela_filtrada['ESPECIE'].isin(especies_porte)) & (tabela_filtrada['DAP'] < 30),
            (tabela_filtrada['DAP'] >= 50) & (tabela_filtrada['QUALIDADE'] < 3),
            (tabela_filtrada['DAP'] < 50),
            (tabela_filtrada['DAP'] > 50) & (tabela_filtrada['QUALIDADE'] == 3)
                     
        ]
        resultados = [
            'Selecionada para corte',
            'Arvore Remanescente de Futuro',
            'Arvore Remanescente de Futuro',
            'Selecionada para corte',
            'Arvore Remanescente Qualidade Fuste 3',
            'Selecionada para corte',
            'Arvore Remanescente de Futuro',
            'Selecionada para corte',
            'Arvore Remanescente de Futuro',
            'Arvore Qualidade Fuste 3'
        ]

        classificacoes = np.select(condicoes, resultados, default=df.loc[idx, 'CLASSIFICAÇÃO'])
        df.loc[idx, 'CLASSIFICAÇÃO'] = classificacoes
        
        #  Para Arvores Porta Semente:
        #     1° Filtrar por UT e selecionadas para corte
	    #     2° Filtrar por tipo de arvore e contabilizar a quantidade que possui (porta-selecionada), tirar 10% do total de arvores contabilizadas por espécie (porta-selecionada)
        #     3° Se o valor em % for menor que 3, seleciono o valor 3 para essa arvore Porta_Semente e para 
        #     para possivel_selecionada faco o calculo porta-selecionada - porta-semente 
        #     4° Se o valor em % da quantidade de arvores selecionadas for maior que 3, arrendondo o valor da % para inteiro e defino essa quantidade como porta-semente,
        #     e para possivel_selecionada faco o calculo porta-selecionada - porta-semente nesse caso é o que sobrou do total de arvores portas selecionadas
        #     5° Se o valor em % da quantidade de arvores selecionadas for menor que 3, então defino essa arvore como como rara, não podendo ser selecionada para corte
           
        # --- Porta Semente e Rara por espécie ---
        # Considera apenas árvores selecionadas para corte, excluindo APP, protegidas e qualidade 3
        selecionadas = tabela_filtrada[
            (df.loc[idx, 'CLASSIFICAÇÃO'] == 'Selecionada para corte') &
            (tabela_filtrada['QUALIDADE'] < 3)
        ]

        especies_15 = ["ANCA", "CUMA", "CUVE", "IPE"]
        
        especies_selecionadas = selecionadas['ESPECIE'].unique()
        # ...existing code...
        for especie in especies_selecionadas:
            arvores_especie = selecionadas[selecionadas['ESPECIE'] == especie]
            total = len(arvores_especie)

            if especie in especies_15:
                if total <= 4:
                    # Marca todas como rara
                    df.loc[arvores_especie.index, 'CLASSIFICAÇÃO'] = 'Arvore Rara'
                    continue
                percentual = 0.15
            else:
                if total <= 3:
                    df.loc[arvores_especie.index, 'CLASSIFICAÇÃO'] = 'Arvore Rara'
                    continue
                percentual = 0.10

            valor_calculado = total * percentual
            print(f"Valor Calculado para {especie}: {valor_calculado} (Total: {total}, Percentual: {percentual})")
            valor_calculado = round(float(total) * float(percentual), 6)  # arredonda para evitar erro de precisão
            print(f"Valor Calculado float para {especie}: {valor_calculado} (Total: {total}, Percentual: {percentual})")
            
            if valor_calculado < 3:
                n_porta_semente = 3
            else:   
                # Arredonda para cima
                n_porta_semente = int(np.ceil(valor_calculado))
                print(f"arredondado para o inteiro mais proximo: {n_porta_semente}")
            
            
            # 1. Encontrar a classe diamétrica com mais indivíduos
            # classe_mais_freq = arvores_especie['CLASSE DIAMETRICA'].mode()[0]
            arvores_classe = arvores_especie
            # 2. Priorizar qualidade 2 e menor volume
            arvores_qualidade2 = arvores_classe[arvores_classe['QUALIDADE'] == 2].sort_values(by='VOLUME INVENTARIO', ascending=True)
            arvores_outros = arvores_classe[arvores_classe['QUALIDADE'] != 2].sort_values(by='VOLUME INVENTARIO', ascending=True)
            # 3. Selecionar os porta-semente
            arvores_selecionadas = pd.concat([arvores_qualidade2, arvores_outros])
            idx_porta_semente = arvores_selecionadas.head(n_porta_semente).index    
            df.loc[idx_porta_semente, 'CLASSIFICAÇÃO'] = 'Porta Semente'
            
            # Após classificar porta semente, exibe resumo das árvores selecionadas para corte e porta semente'
        # selecionadas_corte = df[(df['UT'] == 1) & (df['CLASSIFICAÇÃO'] == 'Selecionada para corte') & (df['ESPECIE'] == 'CUMA')]
        # porta_semente = df[(df['UT'] == 1) & (df['CLASSIFICAÇÃO'] == 'Porta Semente')  & (df['ESPECIE'] == 'CUMA')]
        # print(f"\nResumo UT {valor}:")
        # # print(f"Selecionadas para corte ({len(selecionadas_corte)}):")
        # # print(selecionadas_corte[['ESPECIE', 'DAP', 'QUALIDADE', 'CLASSE DIAMETRICA']])
        # print(f"Porta Semente ({len(porta_semente)}):")
        # print(porta_semente[['ESPECIE', 'DAP', 'QUALIDADE', 'CLASSE DIAMETRICA']])
                
        # print("Resumo final para CUMA:")
        # print(
        #         f"UT: {1} | Total: {total} | Percentual: {percentual} | "
        #         f"Valor calculado: {valor_calculado} | Porta-semente: {n_porta_semente}"
        #     )
      

    # Salva o DataFrame atualizado em memória
    output = BytesIO()  
    df.to_excel(output, index=False)
    output.seek(0)
    conteudo_classificado = output.read()

    # Salva o arquivo classificado no banco (pode sobrescrever ou salvar com outro nome)
    salvar_arquivo(nome_arquivo_processado, conteudo_classificado, mimetype)

    return conteudo_classificado