// ═══════════════════════════════════════════════════════════════
// students.js — Aba "Meus Alunos" (aba 3)
// ═══════════════════════════════════════════════════════════════

async function loadAlunos() {
    const container = document.getElementById('alunos-container');
    const token     = localStorage.getItem('token_academia');

    if (!token || currentRole !== 'personal') return;

    container.innerHTML = '<p class="text-slate-500 dark:text-zinc-400 animate-pulse">Buscando alunos no sistema...</p>';
    container.classList.add('items-center', 'justify-center');

    try {
        const response = await fetch(`${URL_BACKEND}/alunos/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) {
            const data = await response.json();
            container.innerHTML = `<p class="text-red-500">Erro: ${data.detail || 'Falha ao buscar alunos'}</p>`;
            return;
        }

        const alunos = await response.json();

        if (alunos.length === 0) {
            container.innerHTML = `
                <i class="fa-solid fa-users-slash text-6xl mb-4 opacity-30 text-slate-400 dark:text-zinc-600"></i>
                <p class="text-slate-500 dark:text-zinc-400 font-medium">Nenhum aluno encontrado no sistema.</p>`;
            return;
        }

        container.classList.remove('items-center', 'justify-center');
        let html = '<div class="flex flex-col gap-4 w-full">';

        alunos.forEach(aluno => {
            html += `
                <div class="bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 p-5 rounded-2xl flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 hover:border-emerald-500/50 transition-all shadow-xs" data-aluno-id="${aluno.id}" data-aluno-nome="${aluno.nome}">
                    <div class="flex items-center gap-4">
                        <div class="w-12 h-12 bg-emerald-100 dark:bg-zinc-800 text-emerald-700 dark:text-emerald-400 rounded-full flex items-center justify-center font-bold text-xl shrink-0">
                            ${aluno.nome.charAt(0).toUpperCase()}
                        </div>
                        <div class="text-left">
                            <h3 class="text-slate-900 dark:text-white font-bold text-lg leading-tight">${aluno.nome}</h3>
                            <p class="text-slate-500 dark:text-zinc-400 text-sm mt-1">
                                ID: <span class="text-emerald-700 dark:text-emerald-400 font-mono bg-slate-200 dark:bg-zinc-900 px-2 py-0.5 rounded">${aluno.id}</span>
                                | ${aluno.email}
                            </p>
                        </div>
                    </div>
                    <div class="flex flex-wrap sm:flex-nowrap gap-2 w-full sm:w-auto">
                        <button onclick="copiarIdAluno(${aluno.id})"
                                class="bg-slate-200 dark:bg-zinc-800 hover:bg-emerald-600 hover:text-white dark:hover:bg-emerald-500 dark:hover:text-black text-slate-800 dark:text-zinc-200 px-4 py-2 rounded-xl text-sm font-semibold transition-all shadow-xs cursor-pointer">
                            Usar ID
                        </button>
                        <button onclick="abrirGradeSemanal(${aluno.id}, '${aluno.nome}')"
                                class="bg-slate-100 dark:bg-zinc-800 hover:bg-emerald-50 dark:hover:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400 border border-slate-300 dark:border-zinc-700 hover:border-emerald-500/40 px-4 py-2 rounded-xl text-xs font-semibold transition-all flex items-center gap-1.5 justify-center shadow-xs cursor-pointer">
                            <i class="fa-solid fa-calendar-week"></i> Ver Treinos
                        </button>
                        <button onclick="abrirModalObjetivo(${aluno.id}, '${aluno.nome}')"
                                class="bg-slate-100 dark:bg-zinc-800 hover:bg-blue-50 dark:hover:bg-blue-500/20 text-blue-700 dark:text-blue-400 border border-slate-300 dark:border-zinc-700 hover:border-blue-500/40 px-4 py-2 rounded-xl text-xs font-semibold transition-all flex items-center gap-1.5 justify-center shadow-xs cursor-pointer">
                            <i class="fa-solid fa-bullseye"></i> Objetivo
                        </button>
                    </div>
                </div>`;
        });

        html += '</div>';
        container.innerHTML = html;

    } catch {
        container.innerHTML = '<p class="text-red-500">Falha de conexão com o servidor.</p>';
    }
}

function copiarIdAluno(id) {
    const input = document.getElementById('new-treino-id-aluno');
    if (input) input.value = id;
    showToast(`ID ${id} selecionado! Vamos criar o treino.`);
    switchTab(2);
}