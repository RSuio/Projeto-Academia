// ═══════════════════════════════════════════════════════════════
// schedule.js — Grade semanal com drag and drop (personal trainer)
// ═══════════════════════════════════════════════════════════════

const DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"];

let treinosDoAluno  = [];   // cache dos treinos carregados
let draggedTreinoId = null; // id do card sendo arrastado


// ── Abre o modal com a grade semanal de um aluno ──────────────
async function abrirGradeSemanal(alunoId, nomeAluno) {
    const token = localStorage.getItem('token_academia');

    // Cria o modal
    document.getElementById('modal-grade')?.remove();
    const modal = document.createElement('div');
    modal.id        = 'modal-grade';
    modal.className = 'fixed inset-0 bg-slate-900/80 dark:bg-black/90 backdrop-blur-xs z-50 flex flex-col overflow-hidden';
    modal.innerHTML = `
        <div class="flex items-center justify-between px-6 py-4 bg-white dark:bg-zinc-900 border-b border-slate-200 dark:border-zinc-800 shrink-0">
            <div>
                <h2 class="text-xl font-bold text-slate-900 dark:text-white">Grade Semanal</h2>
                <p class="text-sm text-slate-500 dark:text-zinc-400">Aluno: <span class="text-emerald-600 dark:text-emerald-400 font-semibold">${nomeAluno}</span>
                   <span class="text-slate-400 dark:text-zinc-600 ml-3 text-xs">Arraste os treinos entre os dias</span>
                </p>
            </div>
            <button onclick="fecharGradeSemanal()"
                    class="text-slate-400 hover:text-slate-700 dark:text-zinc-500 dark:hover:text-white p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer">
                <i class="fa-solid fa-xmark text-xl"></i>
            </button>
        </div>
        <div id="grade-loading" class="flex-1 flex items-center justify-center text-slate-500 dark:text-zinc-400">
            <i class="fa-solid fa-spinner fa-spin text-2xl"></i>
        </div>
        <div id="grade-content" class="hidden flex-1 overflow-x-auto overflow-y-hidden p-4 bg-slate-50 dark:bg-zinc-950">
            <div id="grade-colunas" class="flex gap-3 h-full min-w-max"></div>
        </div>`;
    const scrollPos = window.scrollY;   // salva posição atual do scroll
    document.body.appendChild(modal);
    document.body.style.overflow = 'hidden';
    window.scrollTo(0, scrollPos);      // restaura posição imediatamente

    // Busca treinos do aluno
    try {
        const response = await fetch(`${URL_BACKEND}/treinos/aluno/${alunoId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error();
        treinosDoAluno = await response.json();
    } catch {
        document.getElementById('grade-loading').innerHTML =
            '<p class="text-red-500 font-medium">Erro ao carregar treinos do aluno.</p>';
        return;
    }

    document.getElementById('grade-loading').classList.add('hidden');
    document.getElementById('grade-content').classList.remove('hidden');
    renderizarGrade();
}


// ── Renderiza as colunas da semana ────────────────────────────
function renderizarGrade() {
    const container = document.getElementById('grade-colunas');
    container.innerHTML = '';

    // Coluna "Sem dia" + colunas dos dias
    const colunas = ['Sem dia', ...DIAS];

    colunas.forEach(dia => {
        const treinos = treinosDoAluno.filter(t =>
            dia === 'Sem dia' ? !t.dia_semana : t.dia_semana === dia
        );

        const col = document.createElement('div');
        col.className  = 'flex flex-col w-56 shrink-0 h-full';
        col.dataset.dia = dia;

        col.innerHTML = `
            <div class="flex items-center gap-2 mb-3 px-1">
                <span class="font-bold text-sm ${dia === 'Sem dia' ? 'text-slate-400 dark:text-zinc-500' : 'text-emerald-600 dark:text-emerald-400'}">
                    ${dia === 'Sem dia' ? '— Sem dia —' : dia}
                </span>
                <span class="text-xs text-slate-400 dark:text-zinc-600 font-medium">(${treinos.length})</span>
            </div>
            <div class="drop-zone flex-1 rounded-2xl border-2 border-dashed border-slate-300 dark:border-zinc-800 bg-white/50 dark:bg-zinc-900/40 p-2 space-y-2 min-h-32 transition-all overflow-y-auto"
                 data-dia="${dia}"
                 ondragover="onDragOver(event)"
                 ondragleave="onDragLeave(event)"
                 ondrop="onDrop(event, '${dia}')">
            </div>`;

        container.appendChild(col);

        const zona = col.querySelector('.drop-zone');
        treinos.forEach(t => zona.appendChild(criarCardArrastavel(t)));
    });
}


// ── Cria um card arrastável ───────────────────────────────────
function criarCardArrastavel(treino) {
    const card = document.createElement('div');
    card.className   = 'bg-white dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 rounded-xl p-3 cursor-grab active:cursor-grabbing select-none hover:border-emerald-500 shadow-xs transition-all';
    card.draggable   = true;
    card.dataset.id  = treino.id;

    card.innerHTML = `
        <div class="flex items-start justify-between gap-2">
            <div class="flex-1 min-w-0">
                <p class="text-slate-900 dark:text-white font-semibold text-sm truncate">${treino.nome}</p>
                <p class="text-slate-500 dark:text-zinc-400 text-xs mt-0.5">${treino.objetivo || 'Sem objetivo'}</p>
            </div>
            <i class="fa-solid fa-grip-vertical text-slate-400 dark:text-zinc-600 mt-0.5 shrink-0"></i>
        </div>
        <p class="text-slate-400 dark:text-zinc-500 text-xs mt-2 font-medium">${treino.exercicios?.length ?? 0} exercícios</p>`;

    card.addEventListener('dragstart', e => {
        draggedTreinoId = treino.id;
        card.classList.add('opacity-40', 'scale-95');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', treino.id.toString());
    });

    card.addEventListener('dragend', () => {
        card.classList.remove('opacity-40', 'scale-95');
        draggedTreinoId = null;
    });

    return card;
}


// ── Eventos de drag and drop nas zonas ───────────────────────
function onDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    e.dataTransfer.dropEffect = 'move';
    e.currentTarget.classList.add('border-emerald-500', 'bg-emerald-500/10');
    e.currentTarget.classList.remove('border-slate-300', 'border-zinc-800');
}

function onDragLeave(e) {
    e.stopPropagation();
    e.currentTarget.classList.remove('border-emerald-500', 'bg-emerald-500/10');
    e.currentTarget.classList.add('border-slate-300', 'dark:border-zinc-800');
}

async function onDrop(e, dia) {
    e.preventDefault();
    e.stopPropagation();
    const zona = e.currentTarget;
    zona.classList.remove('border-emerald-500', 'bg-emerald-500/10');
    zona.classList.add('border-slate-300', 'dark:border-zinc-800');

    if (!draggedTreinoId) return;

    const token      = localStorage.getItem('token_academia');
    const novoDia    = dia === 'Sem dia' ? null : dia;
    const treinoId   = draggedTreinoId;

    // Atualiza otimisticamente no cache local
    const treino = treinosDoAluno.find(t => t.id === treinoId);
    if (!treino) return;
    treino.dia_semana = novoDia;

    // Agenda a atualização do DOM e API para o próximo ciclo de eventos,
    // garantindo que o navegador termine de processar o evento de drop nativo
    // sem disparar comportamentos padrão (como recarregamento de página).
    setTimeout(async () => {
        // Re-renderiza a grade
        renderizarGrade();

        // Persiste no backend
        try {
            const response = await fetch(`${URL_BACKEND}/treinos/${treinoId}/dia`, {
                method:  'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ dia_semana: novoDia })
            });

            if (!response.ok) {
                showToast('Erro ao salvar o dia do treino.', true);
            } else {
                showToast(`Treino movido para ${novoDia || 'sem dia definido'}.`);
            }
        } catch {
            showToast('Erro de conexão.', true);
        }
    }, 0);
}


// Fecha o modal e restaura o scroll da página
function fecharGradeSemanal() {
    document.getElementById('modal-grade')?.remove();
    document.body.style.overflow = '';
}

// Previne comportamento padrão de abrir elementos arrastados como links/pesquisas quando soltos fora das colunas
window.addEventListener("dragover", function(e) {
    e.preventDefault();
}, false);
window.addEventListener("drop", function(e) {
    e.preventDefault();
}, false);