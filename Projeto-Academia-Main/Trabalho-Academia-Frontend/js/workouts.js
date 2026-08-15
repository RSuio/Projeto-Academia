// ═══════════════════════════════════════════════════════════════
// workouts.js — Aba "Meus Treinos" (aba 0)
// ═══════════════════════════════════════════════════════════════

const ORDEM_DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"];

async function refreshWorkouts() {
    const grid  = document.getElementById('workouts-grid');
    const token = localStorage.getItem('token_academia');
    if (!token) return;

    grid.innerHTML = `
        <div class="col-span-full text-center py-10 text-slate-500 dark:text-zinc-400">
            <i class="fa-solid fa-spinner fa-spin text-xl"></i> Carregando seus treinos...
        </div>`;

    try {
        const response = await fetch(`${URL_BACKEND}/treinos/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) {
            const data = await response.json();
            return showToast(`Erro: ${data.detail || "Não foi possível carregar."}`, true);
        }

        const treinos = await response.json();

        if (treinos.length === 0) {
            grid.innerHTML = `
                <div class="col-span-full text-center py-16 text-slate-500 dark:text-zinc-400 border border-slate-200 dark:border-zinc-800 rounded-3xl bg-white/70 dark:bg-zinc-900/50 shadow-xs">
                    <i class="fa-solid fa-dumbbell text-6xl mb-4 opacity-30 text-emerald-600 dark:text-emerald-400"></i>
                    <p class="text-lg font-semibold text-slate-800 dark:text-white">Nenhum treino carregado ainda.</p>
                    <p class="text-sm mt-2 text-slate-500 dark:text-zinc-400">
                        ${currentRole === 'personal'
                            ? 'Crie o primeiro treino na aba "Criar Treino".'
                            : 'Seus treinos aparecerão aqui assim que o Personal Trainer atribuir.'}
                    </p>
                </div>`;
            return;
        }

        grid.innerHTML = '';

        // Agrupa por dia da semana
        const comDia = treinos.filter(t => t.dia_semana);
        const semDia = treinos.filter(t => !t.dia_semana);
        const porDia = {};
        comDia.forEach(t => {
            if (!porDia[t.dia_semana]) porDia[t.dia_semana] = [];
            porDia[t.dia_semana].push(t);
        });

        // Renderiza na ordem da semana
        ORDEM_DIAS.forEach(dia => {
            if (!porDia[dia]) return;

            const header = document.createElement('div');
            header.className = "col-span-full flex items-center gap-3 mt-4 mb-1";
            header.innerHTML = `
                <span class="text-emerald-600 dark:text-emerald-400 font-bold text-sm uppercase tracking-widest">${dia}</span>
                <div class="flex-1 h-px bg-slate-200 dark:bg-zinc-800"></div>`;
            grid.appendChild(header);

            porDia[dia].forEach(treino => grid.appendChild(criarCardTreino(treino)));
        });

        // Treinos sem dia
        if (semDia.length > 0) {
            if (comDia.length > 0) {
                const header = document.createElement('div');
                header.className = "col-span-full flex items-center gap-3 mt-4 mb-1";
                header.innerHTML = `
                    <span class="text-slate-400 dark:text-zinc-500 font-bold text-sm uppercase tracking-widest">Sem dia definido</span>
                    <div class="flex-1 h-px bg-slate-200 dark:bg-zinc-800"></div>`;
                grid.appendChild(header);
            }
            semDia.forEach(treino => grid.appendChild(criarCardTreino(treino)));
        }

    } catch {
        grid.innerHTML = '<div class="col-span-full text-center py-10 text-red-500 font-medium">Falha de conexão com o servidor.</div>';
    }
}

function criarCardTreino(treino) {
    const card = document.createElement('div');
    card.className = "bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 p-6 rounded-3xl hover:border-emerald-500/60 transition-all shadow-xs hover:shadow-md card-hover";

    let exerciciosHTML = '<ul class="mt-4 space-y-2">';
    treino.exercicios.forEach(ex => {
        const carga         = ex.carga ? `${ex.carga}kg` : 'Corp.';
        const nomeExercicio = ex.nome_exercicio || ex.nome || 'Exercício';
        exerciciosHTML += `
            <li class="flex justify-between items-center text-sm border-b border-slate-100 dark:border-zinc-800/60 pb-2">
                <span class="text-slate-700 dark:text-zinc-300 font-medium truncate pr-2">${nomeExercicio}</span>
                <span class="text-slate-500 dark:text-zinc-400 bg-slate-100 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 px-2.5 py-1 rounded-lg text-xs font-mono whitespace-nowrap">
                    ${ex.series}x${ex.repeticoes} | ${carga}
                </span>
            </li>`;
    });
    exerciciosHTML += '</ul>';

    const botaoMarcar = currentRole === 'aluno' ? `
        <button
            onclick="marcarTreinoFeito(${treino.id}, this)"
            class="mt-5 w-full flex items-center justify-center gap-2 bg-slate-100 dark:bg-zinc-800 hover:bg-emerald-600 hover:text-white dark:hover:bg-emerald-500 dark:hover:text-black text-slate-700 dark:text-zinc-300 text-sm font-semibold px-4 py-3 rounded-2xl transition-all border border-slate-200 dark:border-zinc-700 shadow-xs cursor-pointer">
            <i class="fa-solid fa-circle-check"></i>
            Marcar como feito
        </button>` : '';

    card.innerHTML = `
        <div class="flex justify-between items-start mb-2">
            <h3 class="text-xl font-bold text-slate-900 dark:text-white">${treino.nome}</h3>
            <span class="bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20 text-xs px-3 py-1 rounded-full font-semibold whitespace-nowrap ml-2">
                ${treino.objetivo || 'Geral'}
            </span>
        </div>
        ${exerciciosHTML}
        ${botaoMarcar}`;

    return card;
}