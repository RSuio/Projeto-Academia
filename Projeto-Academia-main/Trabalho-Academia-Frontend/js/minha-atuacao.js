// ═══════════════════════════════════════════════════════════════
// minha-atuacao.js — Personal gerencia academias, dias e horários
// ═══════════════════════════════════════════════════════════════

let perfilAtuacao = null;   // cache do /personais/me
let vinculoEmEdicao = null; // id em edição inline

function tokenAuth() {
    return { 'Authorization': `Bearer ${localStorage.getItem('token_academia')}` };
}

// ── Carrega perfil, academias e a lista de atuações ───────────
async function carregarMinhaAtuacao() {
    const select  = document.getElementById('atuacao-academia');
    const alerta  = document.getElementById('atuacao-alerta');
    const lista   = document.getElementById('meus-vinculos');

    try {
        const response = await fetch(`${URL_BACKEND}/personais/me`, { headers: tokenAuth() });
        if (!response.ok) {
            if (lista) lista.innerHTML = '<p class="text-red-500 font-medium">Erro ao carregar seu perfil.</p>';
            return;
        }
        perfilAtuacao = await response.json();

        // Alerta de onboarding para quem ainda não tem atuação
        if (alerta) alerta.classList.toggle('hidden', (perfilAtuacao.academias || []).length > 0);

        // Select de academias para novos vínculos
        const respAcad = await fetch(`${URL_BACKEND}/academias/`, { headers: tokenAuth() });
        if (respAcad.ok) {
            const academias = await respAcad.json();
            if (select) {
                select.innerHTML = '<option value="">Selecione a academia...</option>' +
                    academias.map(a => `<option value="${a.id}">${a.nome} (${a.cidade || 'sem cidade'})</option>`).join('');
            }
        }

        renderMinhasAtuacoes();
    } catch {
        if (lista) lista.innerHTML = '<p class="text-red-500 font-medium">Falha de conexão com o servidor.</p>';
    }
}

// ── Lista das atuações atuais ─────────────────────────────────
function renderMinhasAtuacoes() {
    const lista = document.getElementById('meus-vinculos');
    if (!lista) return;

    const vinculos = perfilAtuacao?.academias || [];

    if (vinculos.length === 0) {
        lista.innerHTML = `
            <div class="text-center py-10 text-slate-500 dark:text-zinc-400 border border-dashed border-slate-300 dark:border-zinc-700 rounded-2xl">
                <i class="fa-solid fa-calendar-plus text-4xl mb-3 opacity-40"></i>
                <p>Nenhuma academia cadastrada ainda.</p>
                <p class="text-sm mt-1">Use o formulário ao lado para informar onde e quando você atua.</p>
            </div>`;
        return;
    }

    lista.innerHTML = '';
    vinculos.forEach(v => lista.appendChild(criarLinhaVinculo(v)));
}

function criarLinhaVinculo(v) {
    const row = document.createElement('div');
    row.id = `vinculo-${v.id}`;
    row.className = "border border-slate-200 dark:border-zinc-800 rounded-2xl p-5 flex items-center justify-between gap-4";

    const statusAtivo = v.ativo
        ? '<span class="text-xs bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20 px-2.5 py-1 rounded-full font-semibold">Ativo</span>'
        : '<span class="text-xs bg-slate-100 dark:bg-zinc-800 text-slate-500 dark:text-zinc-400 border border-slate-200 dark:border-zinc-700 px-2.5 py-1 rounded-full font-semibold">Inativo</span>';

    const info = `
        <div class="min-w-0">
            <div class="flex items-center gap-3 flex-wrap">
                <p class="font-semibold text-slate-900 dark:text-white">
                    <i class="fa-solid fa-dumbbell text-emerald-600 dark:text-emerald-400 mr-1.5"></i>
                    ${v.academia.nome}
                </p>
                ${statusAtivo}
            </div>
            <p class="text-sm text-slate-600 dark:text-zinc-400 mt-1.5">
                <i class="fa-regular fa-calendar mr-1.5 text-emerald-600 dark:text-emerald-400"></i>${v.dias_semana || 'A combinar'}
                ${v.horario_inicio ? ` · ${v.horario_inicio} às ${v.horario_fim}` : ''}
            </p>
            <p class="text-xs text-slate-400 dark:text-zinc-500">${v.academia.endereco || ''} ${v.academia.cidade ? '· ' + v.academia.cidade : ''}</p>
        </div>`;

    const botoes = `
        <div class="flex items-center gap-2 shrink-0">
            <button type="button" onclick="editarVinculo(${v.id})"
                    class="text-sm text-slate-600 dark:text-zinc-400 hover:text-emerald-600 dark:hover:text-emerald-400 border border-slate-300 dark:border-zinc-700 hover:border-emerald-400 px-3 py-1.5 rounded-xl transition-colors">
                <i class="fa-solid fa-pen"></i> Editar
            </button>
            <button type="button" onclick="removerVinculo(${v.id})"
                    class="text-sm text-red-500 hover:text-red-600 border border-slate-300 dark:border-zinc-700 hover:border-red-400 dark:hover:border-red-500 px-3 py-1.5 rounded-xl transition-colors">
                <i class="fa-solid fa-trash"></i>
            </button>
        </div>`;

    row.innerHTML = `
        <div class="flex-1 flex items-center justify-between gap-4 flex-wrap">
            <div class="min-w-0">${info}</div>
            ${vinculoEmEdicao === v.id ? '' : botoes}
        </div>`;

    return row;
}

// ── Edição inline de dias/horários ────────────────────────────
function editarVinculo(id) {
    vinculoEmEdicao = (vinculoEmEdicao === id) ? null : id;
    renderMinhasAtuacoes();
    if (vinculoEmEdicao !== id) return;

    const v = perfilAtuacao.academias.find(a => a.id === id);
    if (!v) return;

    const row = document.getElementById(`vinculo-${id}`);
    row.innerHTML = `
        <div class="flex-1">
            <p class="font-semibold text-slate-900 dark:text-white mb-3">
                <i class="fa-solid fa-dumbbell text-emerald-600 dark:text-emerald-400 mr-1.5"></i>
                ${v.academia.nome}
            </p>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-3">
                <input id="edit-vinculo-${id}-dias" type="text" value="${v.dias_semana || ''}" placeholder="Dias (ex: Segunda, Quarta)"
                       class="w-full sm:col-span-1 bg-slate-100 dark:bg-zinc-800 border border-slate-300 dark:border-zinc-700 text-slate-900 dark:text-white rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-emerald-500">
                <input id="edit-vinculo-${id}-inicio" type="time" value="${v.horario_inicio || ''}"
                       class="w-full bg-slate-100 dark:bg-zinc-800 border border-slate-300 dark:border-zinc-700 text-slate-900 dark:text-white rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-emerald-500">
                <input id="edit-vinculo-${id}-fim" type="time" value="${v.horario_fim || ''}"
                       class="w-full bg-slate-100 dark:bg-zinc-800 border border-slate-300 dark:border-zinc-700 text-slate-900 dark:text-white rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-emerald-500">
            </div>
            <div class="flex items-center gap-3">
                <label class="flex items-center gap-2 text-sm text-slate-600 dark:text-zinc-400">
                    <input id="edit-vinculo-${id}-ativo" type="checkbox" ${v.ativo ? 'checked' : ''} class="accent-emerald-600 w-4 h-4">
                    Ativo
                </label>
                <button type="button" onclick="salvarEdicaoVinculo(${id})"
                        class="bg-emerald-600 hover:bg-emerald-700 dark:bg-emerald-500 dark:hover:bg-emerald-600 text-white dark:text-black text-sm font-semibold px-4 py-2 rounded-xl transition-colors">
                    Salvar
                </button>
                <button type="button" onclick="editarVinculo(${id})"
                        class="text-sm text-slate-500 hover:text-slate-700 dark:hover:text-zinc-300 px-3 py-2 rounded-xl transition-colors">
                    Cancelar
                </button>
            </div>
        </div>`;
}

async function salvarEdicaoVinculo(id) {
    const dias   = document.getElementById(`edit-vinculo-${id}-dias`).value.trim();
    const inicio = document.getElementById(`edit-vinculo-${id}-inicio`).value;
    const fim    = document.getElementById(`edit-vinculo-${id}-fim`).value;
    const ativo  = document.getElementById(`edit-vinculo-${id}-ativo`).checked;

    try {
        const response = await fetch(`${URL_BACKEND}/personais/academias/${id}`, {
            method: 'PATCH',
            headers: { ...tokenAuth(), 'Content-Type': 'application/json' },
            body: JSON.stringify({ dias_semana: dias, horario_inicio: inicio, horario_fim: fim, ativo })
        });
        const data = await response.json();
        showToast(response.ok ? (data.mensagem || 'Atuação atualizada!') : `Erro: ${data.detail}`, !response.ok);
        if (response.ok) {
            vinculoEmEdicao = null;
            carregarMinhaAtuacao();
        }
    } catch {
        showToast("Erro ao conectar com o servidor.", true);
    }
}

async function removerVinculo(id) {
    if (!confirm('Remover esta atuação?')) return;
    try {
        const response = await fetch(`${URL_BACKEND}/personais/academias/${id}`, {
            method: 'DELETE',
            headers: tokenAuth()
        });
        const data = await response.json();
        showToast(response.ok ? (data.mensagem || 'Atuação removida!') : `Erro: ${data.detail}`, !response.ok);
        if (response.ok) carregarMinhaAtuacao();
    } catch {
        showToast("Erro ao conectar com o servidor.", true);
    }
}

// ── Cadastra uma academia nova ────────────────────────────────
async function salvarNovaAcademia() {
    const nome      = document.getElementById('nova-academia-nome').value.trim();
    const endereco  = document.getElementById('nova-academia-endereco').value.trim();
    const cidade    = document.getElementById('nova-academia-cidade').value.trim();
    const telefone  = document.getElementById('nova-academia-telefone').value.trim();

    if (!nome) return showToast("Informe ao menos o nome da academia.", true);

    try {
        const response = await fetch(`${URL_BACKEND}/academias/`, {
            method: 'POST',
            headers: { ...tokenAuth(), 'Content-Type': 'application/json' },
            body: JSON.stringify({ nome, endereco, cidade, telefone })
        });
        const data = await response.json();
        showToast(response.ok ? (data.mensagem || 'Academia cadastrada!') : `Erro: ${data.detail || 'Não foi possível cadastrar.'}`, !response.ok);
        if (response.ok) {
            ['nova-academia-nome', 'nova-academia-endereco', 'nova-academia-cidade', 'nova-academia-telefone']
                .forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
            carregarMinhaAtuacao();
        }
    } catch {
        showToast("Erro ao conectar com o servidor.", true);
    }
}

// ── Associa academia + dias + horários ao próprio personal ────
async function salvarAtuacao() {
    const academiaId = document.getElementById('atuacao-academia').value;
    const dias       = document.getElementById('atuacao-dias').value.trim();
    const inicio     = document.getElementById('atuacao-horario-inicio').value;
    const fim        = document.getElementById('atuacao-horario-fim').value;

    if (!academiaId) return showToast('Selecione uma academia.', true);
    if (!dias) return showToast('Informe os dias em que você atua.', true);

    try {
        const response = await fetch(`${URL_BACKEND}/personais/me/academias`, {
            method: 'POST',
            headers: { ...tokenAuth(), 'Content-Type': 'application/json' },
            body: JSON.stringify({ academia_id: Number(academiaId), dias_semana: dias, horario_inicio: inicio, horario_fim: fim })
        });
        const data = await response.json();
        showToast(response.ok ? (data.mensagem || 'Atuação adicionada!') : `Erro: ${data.detail}`, !response.ok);
        if (response.ok) {
            document.getElementById('atuacao-dias').value = '';
            document.getElementById('atuacao-horario-inicio').value = '';
            document.getElementById('atuacao-horario-fim').value = '';
            carregarMinhaAtuacao();
        }
    } catch {
        showToast("Erro ao conectar com o servidor.", true);
    }
}