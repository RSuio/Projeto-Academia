// ═══════════════════════════════════════════════════════════════
// workouts.js — Aba "Meus Treinos" (aba 0)
// ═══════════════════════════════════════════════════════════════

async function refreshWorkouts() {
    const grid  = document.getElementById('workouts-grid');
    const token = localStorage.getItem('token_academia');
    if (!token) return;

    grid.innerHTML = `
        <div class="col-span-full text-center py-10 text-zinc-400">
            <i class="fa-solid fa-spinner fa-spin"></i> Carregando seus treinos...
        </div>`;

    try {
        const response = await fetch(`${URL_BACKEND}/treinos/meus-treinos`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) {
            const data = await response.json();
            return showToast(`Erro: ${data.detail || "Não foi possível carregar."}`, true);
        }

        const treinos = await response.json();

        if (treinos.length === 0) {
            grid.innerHTML = `
                <div class="col-span-full text-center py-20 text-zinc-400 border border-zinc-800 rounded-3xl bg-zinc-900/50">
                    <i class="fa-solid fa-dumbbell text-6xl mb-4 opacity-30"></i>
                    <p class="text-lg">Nenhum treino carregado ainda.</p>
                    <p class="text-sm mt-2">
                        ${currentRole === 'personal'
                            ? 'Crie o primeiro treino na aba "Criar Treino".'
                            : 'Seus treinos aparecerão aqui assim que o Personal Trainer atribuir.'}
                    </p>
                </div>`;
            return;
        }

        grid.innerHTML = '';
        treinos.forEach(treino => {
            const card = document.createElement('div');
            card.className = "bg-zinc-900 border border-zinc-800 p-6 rounded-3xl hover:border-emerald-500/50 transition-colors card-hover";

            let exerciciosHTML = '<ul class="mt-4 space-y-2">';
            treino.exercicios.forEach(ex => {
                const carga        = ex.carga ? `${ex.carga}kg` : 'Corp.';
                const nomeExercicio = ex.catalogo ? ex.catalogo.nome : "Exercício";

                exerciciosHTML += `
                    <li class="flex justify-between items-center text-sm border-b border-zinc-800/50 pb-2">
                        <span class="text-zinc-300 font-medium truncate pr-2">${nomeExercicio}</span>
                        <span class="text-zinc-500 bg-zinc-950 border border-zinc-800 px-2 py-1 rounded-md text-xs whitespace-nowrap">
                            ${ex.series}x${ex.repeticoes} | ${carga}
                        </span>
                    </li>`;
            });
            exerciciosHTML += '</ul>';

         // 1. Criamos a variável do botão de lixeira (só aparece para personal)
            const btnDeletar = currentRole === 'personal' 
                ? `<button onclick="deletarTreino(${treino.id})" class="ml-3 text-zinc-500 hover:text-red-500 transition-colors" title="Excluir Treino">
                       <i class="fa-solid fa-trash"></i>
                   </button>` 
                : '';

            // 2. Montamos o HTML do card
            card.innerHTML = `
                <div class="flex justify-between items-start mb-2">
                    <h3 class="text-xl font-bold text-white">${treino.nome}</h3>
                    
                    <div class="flex items-center">
                        <span class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs px-3 py-1 rounded-full font-medium">
                            ${treino.objetivo || 'Geral'}
                        </span>
                        ${btnDeletar}
                    </div>
                </div>
                ${exerciciosHTML}`;

            grid.appendChild(card);
        });

    } catch {
        grid.innerHTML = '<div class="col-span-full text-center py-10 text-red-400">Falha de conexão com o servidor.</div>';
    }
}

// Função para excluir um treino
async function deletarTreino(treinoId) {
    if (!confirm("Tem certeza que deseja excluir este treino? Essa ação não pode ser desfeita.")) return;

    const token = localStorage.getItem('token_academia');
    if (!token) return showToast("Você precisa estar logado!", true);

    try {
        const response = await fetch(`${URL_BACKEND}/treinos/${treinoId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            showToast("Treino excluído com sucesso! 🗑️");
            refreshWorkouts(); // Recarrega a lista de treinos automaticamente
        } else {
            const data = await response.json();
            showToast(`Erro: ${data.detail || "Não foi possível excluir o treino."}`, true);
        }
    } catch {
        showToast("Erro de conexão com o servidor ao tentar excluir.", true);
    }
}