// ═══════════════════════════════════════════════════════════════
// workouts.js — Aba "Meus Treinos" (aba 0) & Demonstração em Vídeo
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

    let exerciciosHTML = '<ul class="mt-4 space-y-2.5">';
    treino.exercicios.forEach(ex => {
        const carga         = ex.carga ? `${ex.carga}kg` : 'Corp.';
        const nomeExercicio = ex.nome_exercicio || ex.nome || 'Exercício';
        const videoUrl      = ex.video_url || '';

        const safeNome  = encodeURIComponent(nomeExercicio);
        const safeVideo = encodeURIComponent(videoUrl);

        exerciciosHTML += `
            <li class="flex justify-between items-center text-sm border-b border-slate-100 dark:border-zinc-800/60 pb-2.5 gap-2">
                <div class="flex items-center gap-2 min-w-0 flex-1">
                    <button type="button" onclick="abrirModalVideo('${safeNome}', '${safeVideo}')"
                            title="Ver vídeo demonstrativo"
                            class="shrink-0 flex items-center justify-center w-7 h-7 rounded-lg bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 hover:bg-emerald-600 hover:text-white dark:hover:bg-emerald-500 dark:hover:text-black transition-all cursor-pointer shadow-2xs">
                        <i class="fa-solid fa-play text-xs pl-0.5"></i>
                    </button>
                    <span class="text-slate-700 dark:text-zinc-300 font-medium truncate">${nomeExercicio}</span>
                </div>
                <span class="text-slate-500 dark:text-zinc-400 bg-slate-100 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 px-2.5 py-1 rounded-lg text-xs font-mono whitespace-nowrap shrink-0">
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


// ═══════════════════════════════════════════════════════════════
// MODAL DE VÍDEO / DEMONSTRAÇÃO DO EXERCÍCIO
// ═══════════════════════════════════════════════════════════════

function formatarUrlVideo(url, nomeExercicio) {
    if (!url) {
        // Fallback: Busca vídeo de execução no YouTube
        return `https://www.youtube.com/embed?listType=search&list=execucao+correta+exercicio+${encodeURIComponent(nomeExercicio)}`;
    }

    // YouTube: formato padrão watch?v=
    if (url.includes('youtube.com/watch?v=')) {
        const videoId = url.split('v=')[1]?.split('&')[0];
        return `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`;
    }

    // YouTube: formato encurtado youtu.be/
    if (url.includes('youtu.be/')) {
        const videoId = url.split('youtu.be/')[1]?.split('?')[0];
        return `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`;
    }

    // YouTube: Shorts
    if (url.includes('youtube.com/shorts/')) {
        const videoId = url.split('shorts/')[1]?.split('?')[0];
        return `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`;
    }

    return url;
}

function abrirModalVideo(safeNome, safeVideoUrl) {
    const nomeExercicio = decodeURIComponent(safeNome);
    const rawVideoUrl   = decodeURIComponent(safeVideoUrl);
    const videoUrl      = formatarUrlVideo(rawVideoUrl, nomeExercicio);
    const isDirectFile  = videoUrl.endsWith('.mp4') || videoUrl.endsWith('.webm');

    document.getElementById('modal-video')?.remove();

    const modal = document.createElement('div');
    modal.id        = 'modal-video';
    modal.className = 'fixed inset-0 bg-slate-900/80 dark:bg-black/90 backdrop-blur-sm flex items-center justify-center p-4 z-[9999]';
    
    const mediaContent = isDirectFile
        ? `<video src="${videoUrl}" controls autoplay loop class="w-full h-full object-cover rounded-2xl bg-black"></video>`
        : `<iframe src="${videoUrl}" 
                   title="Demonstração do Exercício"
                   class="w-full h-full rounded-2xl border-0" 
                   allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                   allowfullscreen>
           </iframe>`;

    modal.innerHTML = `
        <div class="bg-white dark:bg-zinc-900 rounded-3xl w-full max-w-2xl overflow-hidden border border-slate-200 dark:border-zinc-800 shadow-2xl flex flex-col">
            <!-- Cabeçalho do Modal -->
            <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100 dark:border-zinc-800 bg-slate-50/50 dark:bg-zinc-900/50">
                <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-xl bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400 flex items-center justify-center font-bold">
                        <i class="fa-solid fa-play text-sm"></i>
                    </div>
                    <div>
                        <h3 class="text-lg font-bold text-slate-900 dark:text-white leading-tight">${nomeExercicio}</h3>
                        <p class="text-xs text-slate-500 dark:text-zinc-400">Guia de Execução Correta</p>
                    </div>
                </div>
                <button type="button" onclick="fecharModalVideo()"
                        class="text-slate-400 hover:text-slate-700 dark:text-zinc-500 dark:hover:text-white p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer">
                    <i class="fa-solid fa-xmark text-lg"></i>
                </button>
            </div>

            <!-- Player de Vídeo Responsivo (16:9) -->
            <div class="p-5 bg-slate-900">
                <div class="aspect-video w-full rounded-2xl overflow-hidden bg-black shadow-inner">
                    ${mediaContent}
                </div>
            </div>

            <!-- Rodapé com Dicas de Postura -->
            <div class="p-5 bg-white dark:bg-zinc-900 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs text-slate-500 dark:text-zinc-400 border-t border-slate-100 dark:border-zinc-800">
                <div class="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-medium">
                    <i class="fa-solid fa-circle-check"></i>
                    <span>Mantenha a postura e respire de forma controlada</span>
                </div>
                <a href="https://www.youtube.com/results?search_query=como+fazer+exercicio+${encodeURIComponent(nomeExercicio)}" 
                   target="_blank" rel="noopener noreferrer"
                   class="hover:text-red-500 flex items-center gap-1.5 transition-colors font-medium cursor-pointer">
                    <i class="fa-brands fa-youtube text-red-500 text-sm"></i> Ver mais no YouTube
                </a>
            </div>
        </div>`;

    document.body.appendChild(modal);
}

function fecharModalVideo() {
    document.getElementById('modal-video')?.remove();
}