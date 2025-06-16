document.getElementById('uploadForm').addEventListener('submit', function() {
    // Mostra o spinner na área de resultados
    document.getElementById('resultsArea').innerHTML = `
        <div class="d-flex flex-column align-items-center justify-content-center" style="min-height:120px;">
            <div class="spinner-border text-success" role="status" style="width: 3rem; height: 3rem;">
                <span class="visually-hidden">Processando...</span>
            </div>
            <div class="mt-3">Processando arquivo, aguarde...</div>
        </div>
    `;
});