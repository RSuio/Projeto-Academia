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
        const response = await fetch(`${URL_BACKEND}/alunos/`, {
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
                <div class="bg-zinc-950 border border-zinc-800 p-5 rounded-2xl flex justify-between items-center hover:border-emerald-500/50 transition-colors">
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
                    <div class="flex flex-col gap-2">
                        <button onclick="copiarIdAluno(${aluno.id})"
                                class="bg-zinc-800 hover:bg-emerald-500 hover:text-black px-4 py-2 rounded-xl text-sm font-medium transition-colors">
                            Usar ID
                        </button>
                        <button onclick="abrirGradeSemanal(${aluno.id}, '${aluno.nome}')"
                                class="bg-zinc-800 hover:bg-emerald-500/20 hover:text-emerald-400 border border-zinc-700 hover:border-emerald-500/30 px-4 py-2 rounded-xl text-xs font-medium transition-colors flex items-center gap-1 justify-center">
                            <i class="fa-solid fa-calendar-week"></i> Ver Treinos
                        </button>
                        <button onclick="abrirModalObjetivo(${aluno.id}, '${aluno.nome}')"
                                class="bg-zinc-800 hover:bg-blue-500/20 hover:text-blue-400 border border-zinc-700 hover:border-blue-500/30 px-4 py-2 rounded-xl text-xs font-medium transition-colors flex items-center gap-1 justify-center">
                            <i class="fa-solid fa-bullseye"></i> Objetivo
                        </button>
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