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
- Edição dinâmica das espécies protegidas via interface de configurações

## Tecnologias Utilizadas

- [Flask](https://flask.palletsprojects.com/) — Framework web em Python
- [pandas](https://pandas.pydata.org/) — Manipulação e análise eficiente de dados tabulares
- [numpy](https://numpy.org/) — Operações matemáticas e científicas
- [Bootstrap](https://getbootstrap.com/) — Estilização da interface

## Estrutura do Projeto

- `app.py`: Código principal da aplicação Flask
- `controllers/`: Lógica de controle e rotas da aplicação
- `models/`: Funções de processamento e regras de negócio
- `templates/`: Páginas HTML (interface)
- `static/`: Arquivos estáticos (CSS, JS, imagens)
- `uploads/`: Arquivos enviados pelo usuário
- `processed/`: Arquivos processados para download
- `instance/`: Banco de dados SQLite de usuários (futuro)

## Como rodar o projeto

1. **Pré-requisitos**  
   - Python 3.10+  
   - Instale as dependências:
     ```sh
     pip install -r requirements.txt
     ```

2. **Executando a aplicação**
   - Para ambiente de desenvolvimento:
     ```sh
     python app.py
     ```
     Acesse em [http://localhost:5000](http://localhost:5000)

   - Para produção (Heroku/Render):
     ```
     gunicorn app:app
     ```

## Uso

- Faça upload do arquivo Excel de inventário na página inicial.
- Aguarde o processamento e visualize os resultados.
- Baixe o arquivo processado.
- Para aplicar a classificação por UT, clique em "Aplicar Classificação por UT" após o processamento inicial.
- Ajuste as espécies protegidas e outros parâmetros em `/config`.

## Observações

- O arquivo Excel deve conter as colunas esperadas pelo sistema (ex: `CAP`, `DAP`, `FATOR`, `fid`, `DATA INVENTARIO`, `APP`, `ESPECIE`, `UT`, `QUALIDADE`).
- Os nomes das colunas podem ser ajustados no código conforme o padrão do seu inventário ([models/processamento.py](models/processamento.py)).
- O sistema utiliza Bootstrap para o layout e pandas para manipulação dos dados.

## Licença

Este projeto é de uso interno da Mil Madeiras Preciosas.

---
## Ajuda

- Dúvidas frequentes: [FAQ](docs/FAQ.md)
- Contato: jonasmoreira076@gmail.com

Desenvolvido por Jonas Moreira TI - Mil Madeiras
<p align="left">
  <img src="static/img/fundo.png" alt="Logo Mil Madeiras Preciosas" width="150"/>
</p>