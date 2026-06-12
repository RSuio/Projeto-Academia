// ═══════════════════════════════════════════════════════════════
// progress.js — Aba "Progresso" (aba 1) e botão "Marcar como feito"
// ═══════════════════════════════════════════════════════════════

// --- Carrega o dashboard completo ---
async function carregarProgresso() {
    const token = localStorage.getItem('token_academia');
    if (!token) return;

    const container = document.getElementById('progresso-container');
    container.innerHTML = `
        <div class="flex justify-center py-16 text-zinc-400">
            <i class="fa-solid fa-spinner fa-spin text-2xl"></i>
        </div>`;

    try {
        const response = await fetch(`${URL_BACKEND}/progresso/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) {
            container.innerHTML = `<p class="text-red-400 text-center py-10">Erro ao carregar progresso.</p>`;
            return;
        }

        const dados = await response.json();
        renderizarDashboard(dados);

    } catch {
        container.innerHTML = `<p class="text-red-400 text-center py-10">Falha de conexão com o servidor.</p>`;
    }
}


// --- Renderiza os cards de estatísticas + gráfico ---
function renderizarDashboard(dados) {
    const container = document.getElementById('progresso-container');

    const ultimoTreino = dados.ultimo_treino
        ? new Date(dados.ultimo_treino).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })
        : 'Nenhum ainda';

    // Cards de resumo
    const cardsHTML = `
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">

            <div class="bg-zinc-900 border border-zinc-800 rounded-3xl p-6 flex flex-col items-center gap-2 hover:border-emerald-500/40 transition-colors">
                <div class="w-14 h-14 bg-emerald-500/10 rounded-2xl flex items-center justify-center">
                    <i class="fa-solid fa-dumbbell text-emerald-400 text-2xl"></i>
                </div>
                <span class="text-4xl font-bold text-white">${dados.total_realizados}</span>
                <span class="text-sm text-zinc-400 text-center">Treinos Realizados</span>
            </div>

            <div class="bg-zinc-900 border border-zinc-800 rounded-3xl p-6 flex flex-col items-center gap-2 hover:border-emerald-500/40 transition-colors">
                <div class="w-14 h-14 bg-orange-500/10 rounded-2xl flex items-center justify-center">
                    <i class="fa-solid fa-fire text-orange-400 text-2xl"></i>
                </div>
                <span class="text-4xl font-bold text-white">${dados.streak_atual}</span>
                <span class="text-sm text-zinc-400 text-center">Dias Seguidos 🔥</span>
            </div>

            <div class="bg-zinc-900 border border-zinc-800 rounded-3xl p-6 flex flex-col items-center gap-2 hover:border-emerald-500/40 transition-colors">
                <div class="w-14 h-14 bg-blue-500/10 rounded-2xl flex items-center justify-center">
                    <i class="fa-solid fa-calendar-check text-blue-400 text-2xl"></i>
                </div>
                <span class="text-lg font-bold text-white">${ultimoTreino}</span>
                <span class="text-sm text-zinc-400 text-center">Último Treino</span>
            </div>

        </div>
    `;

    // Gráfico de barras — últimos 7 dias
    const maxValor = Math.max(...dados.por_semana, 1);
    const diasSemana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
    const hoje = new Date();

    const barrasHTML = dados.por_semana.map((qtd, i) => {
        const dia = new Date(hoje);
        dia.setDate(hoje.getDate() - i);
        const nomeDia = i === 0 ? 'Hoje' : diasSemana[dia.getDay()];
        const altura  = maxValor > 0 ? Math.max((qtd / maxValor) * 100, qtd > 0 ? 8 : 2) : 2;
        const ativo   = qtd > 0;

        return `
            <div class="flex flex-col items-center gap-2 flex-1">
                <span class="text-xs font-medium ${ativo ? 'text-emerald-400' : 'text-zinc-600'}">${qtd > 0 ? qtd : ''}</span>
                <div class="w-full flex items-end justify-center" style="height: 80px;">
                    <div class="w-full rounded-t-lg transition-all duration-500 ${ativo ? 'bg-emerald-500' : 'bg-zinc-800'}"
                         style="height: ${altura}%;">
                    </div>
                </div>
                <span class="text-[10px] text-zinc-500">${nomeDia}</span>
            </div>`;
    }).reverse().join('');   // reverse: índice 0 = hoje → fica à direita

    const graficoHTML = `
        <div class="bg-zinc-900 border border-zinc-800 rounded-3xl p-6">
            <h3 class="text-base font-semibold text-white mb-1">Frequência — Últimos 7 dias</h3>
            <p class="text-xs text-zinc-500 mb-6">Cada barra = número de treinos naquele dia</p>
            <div class="flex items-end gap-2">
                ${barrasHTML}
            </div>
        </div>
    `;

    container.innerHTML = cardsHTML + graficoHTML;
}


// --- Marca um treino como realizado ---
async function marcarTreinoFeito(treinoId, btnEl) {
    const token = localStorage.getItem('token_academia');
    if (!token) return showToast('Você precisa estar logado!', true);

    const textoOriginal = btnEl.innerHTML;
    btnEl.disabled = true;
    btnEl.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';

    try {
        const response = await fetch(`${URL_BACKEND}/progresso/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ treino_id: treinoId })
        });

        const data = await response.json();

        if (response.ok) {
            showToast('Treino marcado como feito! 💪');
            btnEl.innerHTML = '<i class="fa-solid fa-circle-check"></i> Feito!';
            btnEl.classList.replace('bg-zinc-800', 'bg-emerald-500/10');
            btnEl.classList.replace('hover:bg-emerald-500', 'border-emerald-500/30');
            btnEl.style.color = '#34d399';
        } else {
            showToast(data.detail || 'Erro ao marcar treino.', true);
            btnEl.innerHTML = textoOriginal;
            btnEl.disabled  = false;
        }

    } catch {
        showToast('Erro de conexão com o servidor.', true);
        btnEl.innerHTML = textoOriginal;
        btnEl.disabled  = false;
    }
}