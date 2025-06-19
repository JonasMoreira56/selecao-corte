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

// ...existing code...
document.getElementById('abrirModal').onclick = function() {
  // Aqui você pode buscar os dados via AJAX/fetch ou já ter os dados em uma variável
  const info = `Tabela para UT = 1:
col1  col2  col3
1     2     3
4     5     6
------------------------------
Tabela para UT = 2:
col1  col2  col3
7     8     9
10    11    12  
------------------------------`;
  document.getElementById('infoTabela').textContent = info;
  document.getElementById('meuModal').style.display = "block";
};

document.querySelector('.fechar').onclick = function() {
  document.getElementById('meuModal').style.display = "none";
};

window.onclick = function(event) {
  if (event.target == document.getElementById('meuModal')) {
    document.getElementById('meuModal').style.display = "none";
  }
};
// ...existing code...