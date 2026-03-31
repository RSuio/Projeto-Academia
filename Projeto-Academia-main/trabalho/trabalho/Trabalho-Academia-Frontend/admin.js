const URL_BACKEND = "http://127.0.0.1:8000";
const token = localStorage.getItem('token_academia');


document.getElementById('btnAddExercicio').addEventListener('click', () => {
    const container = document.getElementById('container-exercicios');
    const div = document.createElement('div');
    div.className = 'exercicio-item';
    div.style = "display: flex; gap: 5px; margin-bottom: 10px;";
    div.innerHTML = `
        <input type="text" placeholder="Nome" class="ex-nome" required>
        <input type="number" placeholder="Séries" class="ex-series" style="width: 60px" required>
        <input type="number" placeholder="Reps" class="ex-reps" style="width: 60px" required>
        <input type="number" placeholder="Carga" class="ex-carga" style="width: 60px"> `;
    container.appendChild(div);
});


document.getElementById('formNovoTreino').addEventListener('submit', async (e) => {
    e.preventDefault();

   const exercicios = Array.from(document.querySelectorAll('.exercicio-item')).map(item => {
    const cargaValor = item.querySelector('.ex-carga').value;
    
    return {
        nome: item.querySelector('.ex-nome').value,
        series: parseInt(item.querySelector('.ex-series').value),
        repeticoes: parseInt(item.querySelector('.ex-reps').value),
        carga: cargaValor === "" ? null : parseInt(cargaValor)
    };
    });


    const payload = {
        nome: document.getElementById('nome_treino').value,
        objetivo: document.getElementById('objetivo').value,
        usuario_id: parseInt(document.getElementById('usuario_id').value),
        exercicios: exercicios
    };

    const response = await fetch(`${URL_BACKEND}/treinos/cadastrar-completo`, {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify(payload)
    });

    if (response.ok) {
        alert("Treino cadastrado com sucesso!");
        location.reload();
    } else {
        alert("Erro ao cadastrar. Verifique se você é Admin.");
    }
});


document.getElementById('btnDeletar').addEventListener('click', async () => {
    const id = document.getElementById('id_treino_deletar').value;
    if (!id) return;

    if (confirm(`Deseja realmente excluir o treino ${id}?`)) {
        const response = await fetch(`${URL_BACKEND}/treinos/deletar/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            alert("Treino removido!");
            location.reload();
        } else {
            alert("Erro ao remover. Treino não encontrado.");
        }
    }
});
function alternarTela(idTela) {
    document.querySelector('.admin-menu-grid').classList.add('hidden');
    document.querySelector('.profile-header').classList.add('hidden');

    fecharTelas();
    document.getElementById(idTela).classList.remove('hidden');
}

function fecharTelas() {
    document.querySelectorAll('.admin-section').forEach(s => s.classList.add('hidden'));
    document.querySelector('.admin-menu-grid').classList.remove('hidden');
    document.querySelector('.profile-header').classList.remove('hidden');
}
function logout() {
    localStorage.removeItem('token_academia');
    window.location.href = "index.html"; 
}
document.getElementById('btnLogout').addEventListener('click', logout);

if (!localStorage.getItem('token_academia')) {
    alert("Acesso negado. Por favor, faça login.");
    window.location.href = "index.html";
}

function irParaMeusTreinos() {
    window.location.href = "dashboard.html";
}