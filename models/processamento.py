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
    
    # remover colunas desnecessárias
    if 'fid' in df.columns:
        df['fid'] = df['fid'].astype(str)
        df = df.drop(columns=['fid'], errors='ignore')
    
    df['DAP'] = df['CAP'] / np.pi
    df['DAP'] = df['DAP'].round(0)
    df['FATOR'] = df['FATOR'].apply(lambda x: f"{float(x):.2f}")

    limite_inferior = ((df['DAP'] // 10) * 10).astype(int)
    limite_superior = (limite_inferior + 10).astype(int)
    classe_diametrica = limite_inferior.astype(str) + '-' + limite_superior.astype(str)
    classe_diametrica = np.where(df['DAP'] >= 100, '>100', classe_diametrica)
    df['CLASSE DIAMETRICA'] = classe_diametrica

    df['VOLUME INVENTARIO'] = VOLUME_FATOR * (df['DAP'] ** VOLUME_EXPOENTE)
    df['VOLUME INVENTARIO'] = df['VOLUME INVENTARIO'].apply(lambda x: f"{float(x):.2f}")

    df['VOLUME INVENTARIO'] = pd.to_numeric(df['VOLUME INVENTARIO'], errors='coerce')
    df['FATOR'] = pd.to_numeric(df['FATOR'], errors='coerce')
    df['VOLUME CORRIGIDO'] = (df['VOLUME INVENTARIO'] * df['FATOR']).map(lambda x: f"{x:.2f}")


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
    
    # 1. Verifica se a coluna existe
    if 'DATA INVENTARIO' in df.columns:
        
        #   Formata a coluna para o tipo datetime e depois para string no formato desejado
        #    - pd.to_datetime converte vários formatos de data para um tipo de data padrão.
        #    - errors='coerce' transforma qualquer data que não puder ser convertida em 'NaT' (Not a Time), evitando erros.
        #    - .dt.strftime('%d/%m/%Y') formata a data para o formato string 'dd/mm/AAAA'.
        df['DATA INVENTARIO'] = pd.to_datetime(df['DATA INVENTARIO'], errors='coerce').dt.strftime('%d/%m/%Y')
        
        #   Move a coluna 'DATA INVENTARIO' para o final
        #    Esta é uma maneira um pouco mais curta de fazer o que você já estava fazendo.
        coluna_data = df.pop('DATA INVENTARIO') # Remove a coluna e a guarda em uma variável
        df['DATA INVENTARIO'] = coluna_data     # Adiciona a coluna de volta, no final
            
            
    # coloca a coluna observação para o final
    if 'OBSERVAÇÃO' in df.columns:
        df['OBSERVAÇÃO'] = df['OBSERVAÇÃO'].replace('NULO','Não Possui')
        # 2. Move a coluna 'OBSERVAÇÃO' para o final
        # Cria uma lista com todas as colunas
        cols = list(df.columns)
        # Remove a coluna 'OBSERVAÇÃO' da sua posição atual
        cols.remove('OBSERVAÇÃO')
        # Adiciona 'OBSERVAÇÃO' ao final da lista de colunas
        cols.append('OBSERVAÇÃO')
        # Reordena o DataFrame usando a nova lista de colunas
        df = df[cols]

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

        # Filtra apenas árvores que NÃO são APP nem protegidas
        filtro_nao_app_protegida = ~(
            (tabela['CLASSIFICAÇÃO'] == 'Arvore na area de preservacao permanente') |
            (tabela['CLASSIFICAÇÃO'] == 'Arvore protegida')
        )
        tabela_filtrada = tabela[filtro_nao_app_protegida]
        idx = tabela_filtrada.index

        especies_porte_dmc_30 = ["ABIU", "MATA"]
        especies_porte_dmc25 = ["ACAR"]
        especies_acima70 = ["IPAM", "IPRO"]
        especies_acima80 = ["CUMA", "CUVE"]

        # Condições para classificação
        condicoes = [
            # 1. Espécies com DAP acima de 70cm ("IPAM", "IPRO")
            (tabela_filtrada['ESPECIE'].isin(especies_acima70)) & (tabela_filtrada['DAP'] >= 70) & (tabela_filtrada['QUALIDADE'] < 3),
            (tabela_filtrada['ESPECIE'].isin(especies_acima70)) & (tabela_filtrada['DAP'] < 70) & (tabela_filtrada['QUALIDADE'] == 3),
            (tabela_filtrada['ESPECIE'].isin(especies_acima70)) & (tabela_filtrada['DAP'] < 70),
            
            # 2. Espécies com DAP acima de 80cm ("CUMA", "CUVE")
            (tabela_filtrada['ESPECIE'].isin(especies_acima80)) & (tabela_filtrada['DAP'] >= 80) & (tabela_filtrada['QUALIDADE'] < 3),
            (tabela_filtrada['ESPECIE'].isin(especies_acima80)) & (tabela_filtrada['DAP'] < 80) & (tabela_filtrada['QUALIDADE'] == 3),
            (tabela_filtrada['ESPECIE'].isin(especies_acima80)) & (tabela_filtrada['DAP'] < 80),
            
            # 3. Espécies de porte para corte com DAP acima de 30 e qualidade ("ABIU", "MATA")
            (tabela_filtrada['ESPECIE'].isin(especies_porte_dmc_30)) & (tabela_filtrada['DAP'] >= 30) & (tabela_filtrada['DAP'] <= 50) & (tabela_filtrada['QUALIDADE'] < 3),
            (tabela_filtrada['ESPECIE'].isin(especies_porte_dmc_30)) & (tabela_filtrada['DAP'] < 30) & (tabela_filtrada['QUALIDADE'] == 3),
            (tabela_filtrada['ESPECIE'].isin(especies_porte_dmc_30)) & (tabela_filtrada['DAP'] < 30),
            (tabela_filtrada['ESPECIE'].isin(especies_porte_dmc_30)) & (tabela_filtrada['DAP'] >= 30) & (tabela_filtrada['QUALIDADE'] == 3),
            
            # 5. Espécies de porte para corte com DAP acima de 25 ("ACAR")
            (tabela_filtrada['ESPECIE'].isin(especies_porte_dmc25)) & (tabela_filtrada['DAP'] >= 25) & (tabela_filtrada['QUALIDADE'] < 3),
            (tabela_filtrada['ESPECIE'].isin(especies_porte_dmc25)) & (tabela_filtrada['DAP'] < 25) & (tabela_filtrada['QUALIDADE'] == 3),
            (tabela_filtrada['ESPECIE'].isin(especies_porte_dmc25)) & (tabela_filtrada['DAP'] < 25),
            (tabela_filtrada['ESPECIE'].isin(especies_porte_dmc25)) & (tabela_filtrada['DAP'] >= 25) & (tabela_filtrada['QUALIDADE'] == 3),
            
            # 6. Espécies gerais com DAP acima de 50
            (tabela_filtrada['DAP'] >= 50) & (tabela_filtrada['QUALIDADE'] < 3),
            (tabela_filtrada['DAP'] < 50) & (tabela_filtrada['QUALIDADE'] == 3),
            (tabela_filtrada['DAP'] < 50),
            (tabela_filtrada['DAP'] >= 50) & (tabela_filtrada['QUALIDADE'] == 3)
                     
        ]
        resultados = [
            # 1. Espécies com DAP acima de 70cm ("IPAM", "IPRO")
            'Selecionada para corte',
            'Arvore Remanescente Qualidade Fuste 3',
            'Arvore Remanescente de Futuro',
            
            # 2. Espécies com DAP acima de 80cm ("CUMA", "CUVE")
            'Selecionada para corte',
            'Arvore Remanescente Qualidade Fuste 3',
            'Arvore Remanescente de Futuro',
            
            # 3. Espécies de porte para corte com DAP acima de 30 e qualidade ("ABIU", "MATA")
            'Selecionada para corte',
            'Arvore Remanescente Qualidade Fuste 3',
            'Arvore Remanescente de Futuro',
            'Arvore Qualidade Fuste 3',
            
            # 5. Espécies de porte para corte com DAP acima de 25 ("ACAR")
            'Selecionada para corte',
            'Arvore Remanescente Qualidade Fuste 3',
            'Arvore Remanescente de Futuro',
            'Arvore Qualidade Fuste 3',
            
            # 6. Espécies gerais com DAP acima de 50
            'Selecionada para corte',
            'Arvore Remanescente Qualidade Fuste 3',
            'Arvore Remanescente de Futuro',
            'Arvore Qualidade Fuste 3'
        ]

        classificacoes = np.select(condicoes, resultados, default=df.loc[idx, 'CLASSIFICAÇÃO'])
        df.loc[idx, 'CLASSIFICAÇÃO'] = classificacoes
           
        # --- Porta Semente e Rara por espécie ---
        # Considera apenas árvores selecionadas para corte, excluindo APP, protegidas e qualidade 3
        selecionadas = tabela_filtrada[
            #(tabela_filtrada['CLASSIFICAÇÃO'] == 'Selecionada para corte')
            (df.loc[idx, 'CLASSIFICAÇÃO'] == 'Selecionada para corte')
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

        
            # Calcula o valor de porta-semente
            valor_calculado = round(float(total) * float(percentual), 2)

            # Lógica ajustada para definir n_porta_semente
            if valor_calculado < 3:
                n_porta_semente = 3
            elif valor_calculado > 3.01:
                n_porta_semente = int(np.ceil(valor_calculado))
            else:
                n_porta_semente = int(round(valor_calculado))

            # Seleção dos porta-semente priorizando qualidade 2 e menor volume
            arvores_qualidade2 = arvores_especie[arvores_especie['QUALIDADE'] == 2].sort_values(by='VOLUME INVENTARIO', ascending=True)
            arvores_outros = arvores_especie[arvores_especie['QUALIDADE'] != 2].sort_values(by='VOLUME INVENTARIO', ascending=True)
            arvores_selecionadas = pd.concat([arvores_qualidade2, arvores_outros])
            idx_porta_semente = arvores_selecionadas.head(n_porta_semente).index
            df.loc[idx_porta_semente, 'CLASSIFICAÇÃO'] = 'Porta Semente'        

    # Salva o DataFrame atualizado em memória
    output = BytesIO()  
    df.to_excel(output, sheet_name='Inventario', index=False)
    output.seek(0)
    conteudo_classificado = output.read()

    # Salva o arquivo classificado no banco (pode sobrescrever ou salvar com outro nome)
    salvar_arquivo(nome_arquivo_processado, conteudo_classificado, mimetype)

    return conteudo_classificado