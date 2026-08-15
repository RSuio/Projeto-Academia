// ═══════════════════════════════════════════════════════════════
// objetivo.js — Barra de progresso do aluno + formulário do personal
// ═══════════════════════════════════════════════════════════════


// ── ALUNO: carrega e exibe o objetivo com barra de progresso ──

async function carregarObjetivo() {
    const token     = localStorage.getItem('token_academia');
    const container = document.getElementById('objetivo-container');
    if (!token || !container) return;

    try {
        const response = await fetch(`${URL_BACKEND}/objetivos/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.status === 404) {
            container.innerHTML = `
                <div class="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-3xl p-8 text-center text-slate-500 dark:text-zinc-500 shadow-xs">
                    <i class="fa-solid fa-bullseye text-4xl mb-3 opacity-30 text-emerald-600 dark:text-emerald-400"></i>
                    <p class="font-medium text-slate-700 dark:text-zinc-300">Nenhum objetivo definido ainda.</p>
                    <p class="text-xs mt-1 text-slate-400 dark:text-zinc-500">Fale com seu Personal Trainer.</p>
                </div>`;
            return;
        }

        if (!response.ok) return;

        const dados = await response.json();
        renderizarObjetivo(dados, container);

    } catch {
        container.innerHTML = `<p class="text-red-500 text-sm">Erro ao carregar objetivo.</p>`;
    }
}

function renderizarObjetivo(dados, container) {
    const obj       = dados.objetivo;
    const pct       = dados.percentual;
    const feitos    = dados.treinos_realizados;
    const meta      = obj.meta_treinos;
    const diasRest  = dados.dias_restantes;
    const concluido = dados.concluido;

    const dataFim   = new Date(obj.data_fim).toLocaleDateString('pt-BR');
    const dataInicio = new Date(obj.data_inicio).toLocaleDateString('pt-BR');

    // Cor da barra muda conforme progresso
    const corBarra = concluido
        ? 'bg-emerald-600 dark:bg-emerald-500'
        : pct >= 75 ? 'bg-emerald-500 dark:bg-emerald-400'
        : pct >= 40 ? 'bg-amber-500 dark:bg-yellow-400'
        : 'bg-orange-500 dark:bg-orange-400';

    const badgeCor = concluido
        ? 'bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-500/20'
        : diasRest <= 7
        ? 'bg-red-50 dark:bg-red-500/10 text-red-700 dark:text-red-400 border-red-200 dark:border-red-500/20'
        : 'bg-slate-100 dark:bg-zinc-800 text-slate-600 dark:text-zinc-400 border-slate-300 dark:border-zinc-700';

    container.innerHTML = `
        <div class="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-3xl p-6 shadow-xs">

            <!-- Cabeçalho -->
            <div class="flex justify-between items-start mb-4">
                <div>
                    <h3 class="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <i class="fa-solid fa-bullseye text-emerald-600 dark:text-emerald-400"></i>
                        ${obj.descricao || 'Objetivo do Período'}
                    </h3>
                    <p class="text-xs text-slate-500 dark:text-zinc-500 mt-1">${dataInicio} → ${dataFim}</p>
                </div>
                <span class="text-xs font-semibold px-3 py-1 rounded-full border ${badgeCor}">
                    ${concluido ? '✅ Concluído!' : `${diasRest}d restantes`}
                </span>
            </div>

            <!-- Contadores -->
            <div class="flex items-end justify-between mb-3">
                <div>
                    <span class="text-4xl font-bold text-slate-900 dark:text-white">${feitos}</span>
                    <span class="text-slate-500 dark:text-zinc-400 text-lg"> / ${meta}</span>
                    <span class="text-slate-400 dark:text-zinc-500 text-sm ml-1">treinos</span>
                </div>
                <span class="text-2xl font-bold ${concluido ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-700 dark:text-zinc-300'}">${pct}%</span>
            </div>

            <!-- Barra de progresso -->
            <div class="w-full bg-slate-100 dark:bg-zinc-800 rounded-full h-4 overflow-hidden">
                <div
                    class="${corBarra} h-4 rounded-full transition-all duration-700 ease-out"
                    style="width: ${pct}%">
                </div>
            </div>

            <!-- Mensagem motivacional -->
            <p class="text-xs text-slate-500 dark:text-zinc-500 mt-3 text-center font-medium">
                ${mensagemMotivacional(pct, concluido, diasRest, meta - feitos)}
            </p>
        </div>
    `;
}

function mensagemMotivacional(pct, concluido, diasRest, faltam) {
    if (concluido)      return '🏆 Parabéns! Você atingiu seu objetivo!';
    if (diasRest === 0) return '⏰ Prazo encerrado. Continue se dedicando!';
    if (pct === 0)      return '💪 Vamos começar! Seu primeiro treino te espera.';
    if (pct < 25)       return `🚀 Bom começo! Faltam ${faltam} treinos para a meta.`;
    if (pct < 50)       return `🔥 No caminho certo! Faltam ${faltam} treinos.`;
    if (pct < 75)       return `⚡ Mais da metade! Faltam apenas ${faltam} treinos.`;
    if (pct < 100)      return `🎯 Quase lá! Só mais ${faltam} treino${faltam > 1 ? 's' : ''}!`;
    return '';
}


// ── PERSONAL: abre o modal para definir objetivo de um aluno ──

function abrirModalObjetivo(alunoId, nomeAluno) {
    // Remove modal antigo se existir
    document.getElementById('modal-objetivo')?.remove();

    const modal = document.createElement('div');
    modal.id        = 'modal-objetivo';
    modal.className = 'fixed inset-0 bg-slate-900/60 dark:bg-black/80 backdrop-blur-xs flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white dark:bg-zinc-900 rounded-3xl w-full max-w-md p-8 relative border border-slate-200 dark:border-zinc-800 shadow-2xl">
            <button onclick="document.getElementById('modal-objetivo').remove()"
                    class="absolute top-5 right-5 text-slate-400 hover:text-slate-700 dark:text-zinc-500 dark:hover:text-white transition-colors">
                <i class="fa-solid fa-xmark text-xl"></i>
            </button>

            <h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-1">Definir Objetivo</h2>
            <p class="text-sm text-slate-500 dark:text-zinc-400 mb-6">Aluno: <span class="text-emerald-600 dark:text-emerald-400 font-semibold">${nomeAluno}</span></p>

            <div class="space-y-4">

                <div>
                    <label class="text-xs font-semibold text-slate-600 dark:text-zinc-400 mb-1 block">Número de treinos a completar</label>
                    <input id="obj-meta" type="number" min="1" placeholder="Ex: 24"
                           class="w-full bg-slate-100 dark:bg-zinc-800 border border-slate-300 dark:border-zinc-700 text-slate-900 dark:text-white rounded-2xl px-4 py-3 focus:outline-none focus:border-emerald-500">
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="text-xs font-semibold text-slate-600 dark:text-zinc-400 mb-1 block">Data início</label>
                        <input id="obj-inicio" type="date"
                               class="w-full bg-slate-100 dark:bg-zinc-800 border border-slate-300 dark:border-zinc-700 text-slate-900 dark:text-white rounded-2xl px-4 py-3 focus:outline-none focus:border-emerald-500">
                    </div>
                    <div>
                        <label class="text-xs font-semibold text-slate-600 dark:text-zinc-400 mb-1 block">Data fim (prazo)</label>
                        <input id="obj-fim" type="date"
                               class="w-full bg-slate-100 dark:bg-zinc-800 border border-slate-300 dark:border-zinc-700 text-slate-900 dark:text-white rounded-2xl px-4 py-3 focus:outline-none focus:border-emerald-500">
                    </div>
                </div>

                <div>
                    <label class="text-xs font-semibold text-slate-600 dark:text-zinc-400 mb-1 block">Descrição (opcional)</label>
                    <input id="obj-descricao" type="text" placeholder="Ex: Foco em hipertrofia"
                           class="w-full bg-slate-100 dark:bg-zinc-800 border border-slate-300 dark:border-zinc-700 text-slate-900 dark:text-white rounded-2xl px-4 py-3 focus:outline-none focus:border-emerald-500">
                </div>

                <button onclick="salvarObjetivo(${alunoId})"
                        class="w-full bg-emerald-600 hover:bg-emerald-700 dark:bg-emerald-500 dark:hover:bg-emerald-600 text-white dark:text-black font-bold py-4 rounded-2xl transition-colors shadow-md shadow-emerald-500/20 mt-2">
                    SALVAR OBJETIVO
                </button>
            </div>
        </div>
    `;

    // Preenche data início com hoje por padrão
    document.body.appendChild(modal);
    document.getElementById('obj-inicio').value = new Date().toISOString().split('T')[0];
}

async function salvarObjetivo(alunoId) {
    const token     = localStorage.getItem('token_academia');
    const meta      = parseInt(document.getElementById('obj-meta').value);
    const inicio    = document.getElementById('obj-inicio').value;
    const fim       = document.getElementById('obj-fim').value;
    const descricao = document.getElementById('obj-descricao').value.trim();

    if (!meta || meta < 1)  return showToast('Informe um número de treinos válido.', true);
    if (!inicio || !fim)    return showToast('Preencha as datas de início e fim.', true);
    if (fim <= inicio)      return showToast('A data fim deve ser posterior ao início.', true);

    const btn = document.querySelector('#modal-objetivo button[onclick^="salvarObjetivo"]');
    const textoOriginal = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Salvando...';
    btn.disabled  = true;

    try {
        const response = await fetch(`${URL_BACKEND}/objetivos/`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({
                usuario_id:   alunoId,
                meta_treinos: meta,
                data_inicio:  `${inicio}T00:00:00`,
                data_fim:     `${fim}T23:59:59`,
                descricao:    descricao || null
            })
        });

        const data = await response.json();

        if (response.ok) {
            showToast(data.mensagem || 'Objetivo salvo!');
            document.getElementById('modal-objetivo').remove();
        } else {
            showToast(data.detail || 'Erro ao salvar objetivo.', true);
            btn.innerHTML = textoOriginal;
            btn.disabled  = false;
        }
    } catch {
        showToast('Erro de conexão.', true);
        btn.innerHTML = textoOriginal;
        btn.disabled  = false;
    }
}


// ── Abre o modal de objetivo a partir do formulário de criar treino ──
function abrirObjetivoPeloForm() {
    const idAluno = document.getElementById('new-treino-id-aluno')?.value.trim();

    if (!idAluno) {
        showToast('Preencha o ID do aluno primeiro.', true);
        return;
    }

    // Tenta pegar o nome do aluno pelo ID se já estiver carregado
    const cardAluno = document.querySelector(`[data-aluno-id="${idAluno}"]`);
    const nome = cardAluno?.dataset.alunoNome || `Aluno ID ${idAluno}`;

    abrirModalObjetivo(parseInt(idAluno), nome);
}