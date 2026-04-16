// ═══════════════════════════════════════════════════════════════
// students.js — Aba "Meus Alunos" (aba 3)
// ═══════════════════════════════════════════════════════════════

async function loadAlunos() {
    const container = document.getElementById('alunos-container');
    const token     = localStorage.getItem('token_academia');

    if (!token || currentRole !== 'personal') return;

    container.innerHTML = '<p class="text-zinc-400 animate-pulse">Buscando alunos no sistema...</p>';
    container.classList.add('items-center', 'justify-center');

    try {
        const response = await fetch(`${URL_BACKEND}/auth/alunos`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) {
            const data = await response.json();
            container.innerHTML = `<p class="text-red-400">Erro: ${data.detail || 'Falha ao buscar alunos'}</p>`;
            return;
        }

        const alunos = await response.json();

        if (alunos.length === 0) {
            container.innerHTML = `
                <i class="fa-solid fa-users-slash text-6xl mb-4 opacity-30"></i>
                <p class="text-zinc-400">Nenhum aluno encontrado no sistema.</p>`;
            return;
        }

        container.classList.remove('items-center', 'justify-center');
        let html = '<div class="flex flex-col gap-4 w-full">';
alunos.forEach(aluno => {
            html += `
                <div class="bg-zinc-950 border border-zinc-800 p-5 rounded-2xl flex flex-col hover:border-emerald-500/50 transition-colors">
                    
                    <div class="flex justify-between items-center w-full">
                        <div class="flex items-center gap-4">
                            <div class="w-12 h-12 bg-zinc-800 rounded-full flex items-center justify-center text-emerald-400 font-bold text-xl">
                                ${aluno.nome.charAt(0).toUpperCase()}
                            </div>
                            <div class="text-left">
                                <h3 class="text-white font-bold text-lg leading-tight">${aluno.nome}</h3>
                                <p class="text-zinc-500 text-sm mt-1">
                                    ID: <span class="text-emerald-400 font-mono bg-zinc-900 px-2 rounded">${aluno.id}</span>
                                    | ${aluno.email}
                                </p>
                            </div>
                        </div>
                        
                        <div class="flex gap-2">
                            <button onclick="verTreinosDoAluno(${aluno.id})"
                                    class="bg-zinc-800 hover:bg-zinc-700 px-4 py-2 rounded-xl text-sm font-medium transition-colors text-white border border-zinc-700">
                                Ver Treinos
                            </button>
                            <button onclick="copiarIdAluno(${aluno.id})"
                                    class="bg-emerald-500 text-black hover:bg-emerald-600 px-4 py-2 rounded-xl text-sm font-medium transition-colors">
                                Usar ID
                            </button>
                        </div>
                    </div>

                    <div id="treinos-aluno-${aluno.id}" class="hidden w-full mt-4 pt-4 border-t border-zinc-800">
                        <p class="text-zinc-500 text-xs italic">Carregando treinos...</p>
                    </div>

                </div>`;
        });

        html += '</div>';
        container.innerHTML = html;

    } catch {
        container.innerHTML = '<p class="text-red-400">Falha de conexão com o servidor.</p>';
    }
}

function copiarIdAluno(id) {
    const input = document.getElementById('new-treino-id-aluno');
    if (input) input.value = id;
    showToast(`ID ${id} selecionado! Vamos criar o treino.`);
    switchTab(2);
}

// Função para carregar e exibir os treinos de um aluno específico
async function verTreinosDoAluno(alunoId) {
    const listaTreinosContainer = document.getElementById(`treinos-aluno-${alunoId}`);
    
    // Se já estiver visível, a gente esconde (efeito toggle)
    if (!listaTreinosContainer.classList.contains('hidden')) {
        listaTreinosContainer.classList.add('hidden');
        return;
    }

    const token = localStorage.getItem('token_academia');
    
    try {
        // Rota no seu backend que busca treinos por ID de usuário
        const response = await fetch(`${URL_BACKEND}/treinos/usuario/${alunoId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        const treinos = await response.json();
        listaTreinosContainer.innerHTML = ''; // Limpa o "Carregando..."
        listaTreinosContainer.classList.remove('hidden');

        if (treinos.length === 0) {
            listaTreinosContainer.innerHTML = '<p class="text-zinc-500 text-sm p-2">Este aluno ainda não possui treinos.</p>';
            return;
        }

        treinos.forEach(treino => {
            const div = document.createElement('div');
            div.className = "flex justify-between items-center bg-zinc-800/50 p-3 rounded-lg mb-2 border border-zinc-700";
            div.innerHTML = `
                <div>
                    <p class="text-white font-bold text-sm">${treino.nome}</p>
                    <p class="text-zinc-400 text-xs">${treino.objetivo || 'Sem objetivo'}</p>
                </div>
                <button onclick="deletarTreino(${treino.id}, true)" class="text-zinc-500 hover:text-red-500 transition-colors p-2">
                    <i class="fa-solid fa-trash"></i>
                </button>
            `;
            listaTreinosContainer.appendChild(div);
        });

    } catch (error) {
        console.error(error);
        showToast("Erro ao carregar treinos do aluno", true);
    }
}