const URL_BACKEND = "http://127.0.0.1:8000";

async function carregarTreinos() {
    const token = localStorage.getItem('token_academia');

    // Se não tiver token, volta para o login
    if (!token) {
        window.location.href = "index.html";
        return;
    }

    try {
        const response = await fetch(`${URL_BACKEND}/treinos/meus-treinos`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}` // Aqui enviamos o token para a API
            }
        });

        if (response.status === 401) {
            alert("Sessão expirada. Faça login novamente.");
            logout();
        }

        const treinos = await response.json();
        renderizarTreinos(treinos);

    } catch (error) {
        console.error("Erro ao buscar treinos:", error);
        document.getElementById('lista-treinos').innerHTML = "<p>Erro ao carregar treinos. Verifique a conexão.</p>";
    }
}

function renderizarTreinos(treinos) {
    const container = document.getElementById('lista-treinos');
    container.innerHTML = ""; // Limpa o "Carregando..."

    if (treinos.length === 0) {
        container.innerHTML = "<p>Você ainda não possui treinos cadastrados.</p>";
        return;
    }

    treinos.forEach(treino => {
        // Criar a tabela de exercícios
        let exerciciosHtml = "";
        treino.exercicios.forEach(ex => {
            exerciciosHtml += `
                <tr>
                    <td><strong>${ex.nome}</strong></td>
                    <td>${ex.series}x${ex.repeticoes}</td>
                    <td>${ex.carga}kg</td>
                </tr>
            `;
        });

        // Criar o card do treino
        const card = `
            <div class="treino-card">
                <h3>${treino.nome}</h3>
                <span class="badge-objetivo">${treino.objetivo}</span>
                
                <table class="exercicios-table">
                    <thead>
                        <tr>
                            <th>Exercício</th>
                            <th>Séries</th>
                            <th>Peso</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${exerciciosHtml}
                    </tbody>
                </table>
            </div>
        `;
        container.innerHTML += card;
    });
}

function logout() {
    localStorage.removeItem('token_academia');
    window.location.href = "index.html";
}

document.getElementById('btnLogout').addEventListener('click', logout);

carregarTreinos();