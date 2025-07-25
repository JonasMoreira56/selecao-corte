import os
from flask import Flask
from controllers.main_controller import main

# Define as pastas para upload e arquivos processados
# UPLOAD_FOLDER = 'uploads'
# PROCESSED_FOLDER = 'processed'

# # Garante que as pastas existam
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# --- Configuração Inicial ---
app = Flask(__name__)

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.register_blueprint(main)


if __name__ == '__main__':
    # Inicia o servidor Flask
    app.run(debug=True)