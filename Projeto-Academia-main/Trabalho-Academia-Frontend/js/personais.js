// ═══════════════════════════════════════════════════════════════
// personais.js — Vitrine pública de Personal Trainers
// ═══════════════════════════════════════════════════════════════

let personaisCarregados = [];   // cache da última busca
let academiasCarregadas = [];   // cache do filtro

async function initPersonaisView() {
    carregarAcademiasFiltro();
    carregarPersonais();
}

// ── Popula o select de academias ─────────────────────────────
async function carregarAcademiasFiltro() {
    const select = document.getElementById('filtro-academia');
    if (!select) return;

    try {
        const response = await fetch(`${URL_BACKEND}/academias/`);
        if (!response.ok) return;
        academiasCarregadas = await response.json();
        select.innerHTML = '<option value="">Todas as academias</option>' +
            academiasCarregadas.map(a => `<option value="${a.id}">${a.nome}</option>`).join('');
    } catch {
        // Deixa o filtro em branco; a listagem funciona sem ele
    }
}

// ── Busca os personais no backend ────────────────────────────
async function carregarPersonais() {
    const grid   = document.getElementById('personais-grid');
    const select = document.getElementById('filtro-academia');
    const academiaId = select ? select.value : '';

    if (!grid) return;

    grid.innerHTML = `
        <div class="col-span-full text-center py-12 text-slate-500 dark:text-zinc-400">
            <i class="fa-solid fa-spinner fa-spin text-xl"></i> Carregando personais...
        </div>`;

    try {
        const url = `${URL_BACKEND}/personais/${academiaId ? `?academia_id=${academiaId}` : ''}`;
        const response = await fetch(url);
        if (!response.ok) {
            const data = await response.json();
            grid.innerHTML = `<p class="col-span-full text-center text-red-500">Erro: ${data.detail || 'Falha ao carregar personais.'}</p>`;
            return;
        }
        personaisCarregados = await response.json();
        renderPersonais();
    } catch {
        grid.innerHTML = '<p class="col-span-full text-center text-red-500 font-medium">Falha de conexão com o servidor.</p>';
    }
}

// ── Filtro de busca (nome/especialidade), aplicado no cliente ─
function filtrarPersonais() {
    renderPersonais();
}

function renderPersonais() {
    const grid   = document.getElementById('personais-grid');
    const busca  = (document.getElementById('filtro-busca') || {}).value?.trim().toLowerCase() || '';

    if (!grid) return;

    const filtrados = personaisCarregados.filter(p => {
        if (!busca) return true;
        const alvo = `${p.nome} ${p.especialidade || ''} ${p.bio || ''}`.toLowerCase();
        return alvo.includes(busca);
    });

    if (filtrados.length === 0) {
        grid.innerHTML = `
            <div class="col-span-full text-center py-16 text-slate-500 dark:text-zinc-400 border border-slate-200 dark:border-zinc-800 rounded-3xl bg-white/70 dark:bg-zinc-900/50 shadow-xs">
                <i class="fa-solid fa-user-tie text-6xl mb-4 opacity-30 text-emerald-600 dark:text-emerald-400"></i>
                <p class="text-lg font-semibold text-slate-800 dark:text-white">Nenhum personal encontrado.</p>
                <p class="text-sm mt-2 text-slate-500 dark:text-zinc-400">Tente outra academia ou busca diferente.</p>
            </div>`;
        return;
    }

    grid.innerHTML = '';
    filtrados.forEach(p => grid.appendChild(criarCardPersonal(p)));
}

// ── Card de um personal trainer ──────────────────────────────
function criarCardPersonal(p) {
    const card = document.createElement('div');
    card.className = "bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 p-6 rounded-3xl hover:border-emerald-500/60 transition-all shadow-xs hover:shadow-md flex flex-col gap-4";

    const academiasHTML = p.academias.map(a => {
        const local = [a.academia.cidade, a.academia.endereco].filter(Boolean).join(' · ');
        return `
            <div class="bg-slate-50 dark:bg-zinc-800/60 border border-slate-200 dark:border-zinc-700 rounded-2xl p-4">
                <div class="flex items-center gap-2 text-slate-900 dark:text-white font-semibold">
                    <i class="fa-solid fa-dumbbell text-emerald-600 dark:text-emerald-400"></i>
                    ${a.academia.nome}
                </div>
                ${local ? `<p class="text-xs text-slate-500 dark:text-zinc-400 mt-1">${local}</p>` : ''}
                <div class="mt-3 space-y-1.5 text-sm text-slate-600 dark:text-zinc-300">
                    <p class="flex items-center gap-2">
                        <i class="fa-regular fa-calendar text-emerald-600 dark:text-emerald-400 w-4 text-center"></i>
                        <span>${a.dias_semana || 'A combinar'}</span>
                    </p>
                    ${a.horario_inicio ? `
                        <p class="flex items-center gap-2">
                            <i class="fa-regular fa-clock text-emerald-600 dark:text-emerald-400 w-4 text-center"></i>
                            <span>${a.horario_inicio} – ${a.horario_fim}</span>
                        </p>` : ''}
                </div>
            </div>`;
    }).join('');

    card.innerHTML = `
        <div class="flex items-start gap-4">
            <div class="w-14 h-14 shrink-0 bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400 rounded-2xl flex items-center justify-center font-bold text-2xl">
                ${p.nome.charAt(0).toUpperCase()}
            </div>
            <div class="min-w-0">
                <h3 class="text-xl font-bold text-slate-900 dark:text-white truncate">${p.nome}</h3>
                ${p.especialidade ? `
                    <span class="inline-block mt-1.5 bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20 text-xs px-3 py-1 rounded-full font-semibold">
                        ${p.especialidade}
                    </span>` : ''}
            </div>
        </div>
        ${p.bio ? `<p class="text-sm text-slate-600 dark:text-zinc-400 leading-relaxed">${p.bio}</p>` : ''}
        <div class="space-y-3">${academiasHTML}</div>
    `;

    return card;
}