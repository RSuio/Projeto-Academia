// ═══════════════════════════════════════════════════════════════
// meu-personal.js — Aluno logado visualiza o personal vinculado
// ═══════════════════════════════════════════════════════════════

async function carregarMeuPersonal() {
    const container = document.getElementById('meu-personal-container');
    if (!container) return;

    container.innerHTML = `
        <div class="bg-white dark:bg-zinc-900 rounded-3xl p-8 border border-slate-200 dark:border-zinc-800 shadow-sm flex flex-col items-center justify-center min-h-[300px]">
            <i class="fa-solid fa-spinner fa-spin text-2xl text-emerald-600 dark:text-emerald-400"></i>
            <p class="mt-3 text-slate-500 dark:text-zinc-400">Carregando seu personal...</p>
        </div>`;

    try {
        const response = await fetch(`${URL_BACKEND}/alunos/meu-personal`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token_academia')}` }
        });

        if (!response.ok) {
            const data = await response.json();
            if (response.status === 401) {
                container.innerHTML = '<p class="text-center text-red-500 font-medium">Sessão expirada. Faça login novamente.</p>';
                return;
            }
            container.innerHTML = `<p class="text-center text-red-500">Erro: ${data.detail || 'Falha ao carregar.'}</p>`;
            return;
        }

        const personal = await response.json();

        if (!personal) {
            container.innerHTML = `
                <div class="bg-white dark:bg-zinc-900 rounded-3xl p-10 border border-slate-200 dark:border-zinc-800 shadow-sm flex flex-col items-center justify-center text-center min-h-[300px]">
                    <i class="fa-solid fa-user-plus text-6xl mb-4 text-emerald-600 dark:text-emerald-400 opacity-30"></i>
                    <p class="text-lg font-semibold text-slate-800 dark:text-white">Você ainda não está vinculado a um personal.</p>
                    <p class="text-sm mt-2 text-slate-500 dark:text-zinc-400 max-w-md">
                        Converse com a equipe da academia para ser acompanhado por um personal trainer.
                    </p>
                </div>`;
            return;
        }

        container.innerHTML = '';
        container.appendChild(criarCardPersonal(personal));
    } catch {
        container.innerHTML = '<p class="text-center text-red-500 font-medium">Falha de conexão com o servidor.</p>';
    }
}