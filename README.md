# Seleção de Corte - Processador de Inventário Florestal

Este projeto é uma aplicação web para processar arquivos de inventário florestal em Excel, aplicando regras de seleção de corte e cálculo de volume, com interface amigável para upload, visualização e download dos resultados.

## Funcionalidades

- Upload de arquivos Excel (.xlsx) de inventário florestal
- Processamento automático dos dados:
  - Cálculo do DAP a partir do CAP
  - Cálculo da Classe Diamétrica
  - Cálculo do Volume do Inventário e Volume Corrigido
  - Classificação de Categoria e Situação Final
- Download do arquivo processado
- Visualização dos resultados na interface
- Configuração dos parâmetros de cálculo (fator e expoente do volume)

## Tecnologias Utilizadas

- [Flask](https://flask.palletsprojects.com/) — Framework web em Python
- [pandas](https://pandas.pydata.org/) — Manipulação e análise eficiente de dados tabulares
- [numpy](https://numpy.org/) — Operações matemáticas e científicas
- [Bootstrap](https://getbootstrap.com/) — Estilização da interface


## Estrutura do Projeto

- `app.py`: Código principal da aplicação Flask
- `templates/`: Páginas HTML (interface)
- `static/`: Arquivos estáticos (CSS, JS, imagens)
- `uploads/`: Arquivos enviados pelo usuário
- `processed/`: Arquivos processados para download

## Como rodar o projeto

<!-- 1. **Pré-requisitos**  
   - Python 3.10+  
   - Instale as dependências:
     ```sh
     pip install flask flask_sqlalchemy flask_login pandas numpy openpyxl
     ```

2. **Executando a aplicação**
   ```sh
   python app.py
   ```
   Acesse em [http://localhost:5000](http://localhost:5000) -->

1. **Uso**
   - Faça upload do arquivo Excel de inventário na página inicial.
   - Aguarde o processamento e visualize os resultados.
   - Baixe o arquivo processado.
   - Ajuste os parâmetros de cálculo em `/configuracoes` se necessário.

## Observações

- O arquivo Excel deve conter as colunas esperadas pelo sistema (ex: `CAP`, `DAP`, `FATOR`, `fid`, `Data`, `APP`).
- Os nomes das colunas podem ser ajustados no código conforme o padrão do seu inventário.
- O sistema utiliza Bootstrap para o layout e pandas para manipulação dos dados.

## Licença

Este projeto é de uso interno da Mil Madeiras Preciosas.

---

Desenvolvido por Jonas Moreira TI - Mil Madeiras
<p align="left">
  <img src="static/img/fundo.png" alt="Logo Mil Madeiras Preciosas" width="150"/>
</p>
