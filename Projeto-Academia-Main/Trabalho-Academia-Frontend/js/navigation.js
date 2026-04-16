// ═══════════════════════════════════════════════════════════════
// navigation.js — Navbar, Rotas e Abas do Dashboard
// ═══════════════════════════════════════════════════════════════

function updateNavbar() {
    const nav = document.getElementById('nav-auth');

    if (isLoggedIn && currentUser) {
        nav.innerHTML = `
            <span onclick="navigateTo('dashboard')"
                  class="cursor-pointer font-medium px-5 py-2 hover:text-emerald-400 transition-colors">
                Meu Painel
            </span>
            <button onclick="logout()"
                    class="bg-zinc-800 hover:bg-zinc-700 px-5 py-2 rounded-3xl text-sm transition-colors font-medium border border-zinc-700">
                Sair
            </button>
        `;
    } else {
        nav.innerHTML = `
            <button onclick="showLoginModal()"
                    class="font-medium px-6 py-2 hover:text-emerald-400 transition-colors">
                Entrar
            </button>
            <button onclick="showRegisterModal()"
                    class="bg-emerald-500 text-black font-semibold px-6 py-2 rounded-3xl hover:bg-emerald-600 transition-colors">
                Criar conta
            </button>
        `;
    }
}

function navigateTo(view) {
    document.getElementById('home-view').classList.add('hidden');
    document.getElementById('dashboard-view').classList.add('hidden');

    if (view === 'home') {
        document.getElementById('home-view').classList.remove('hidden');
    } else if (view === 'dashboard' && isLoggedIn) {
        document.getElementById('dashboard-view').classList.remove('hidden');
        renderDashboard();
    }
}

function renderDashboard() {
    const isPersonal = currentRole === 'personal';

    document.getElementById('dashboard-title').textContent    = isPersonal ? 'Painel do Personal Trainer' : 'Meus Treinos';
    document.getElementById('dashboard-subtitle').textContent = isPersonal ? 'Gerencie seus treinos e alunos' : 'Acompanhe seus resultados';

    // Mostra/oculta as abas de acordo com o perfil
    document.getElementById('tab-1-aluno').classList.toggle('hidden', isPersonal);
    document.getElementById('tab-2-personal').classList.toggle('hidden', !isPersonal);
    document.getElementById('tab-3-personal').classList.toggle('hidden', !isPersonal);

    switchTab(0);
}

function switchTab(tab) {
    // Remove destaque de todas as abas
    document.querySelectorAll('.dashboard-tab').forEach(t => t.classList.remove('bg-emerald-500', 'text-black'));

    // Destaca a aba ativa
    const activeTab = document.getElementById(`tab-${tab}`);
    if (activeTab) activeTab.classList.add('bg-emerald-500', 'text-black');

    // Oculta todos os conteúdos e exibe o correto
    document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
    document.getElementById(`content-${tab}`).classList.remove('hidden');

    // Carregamentos específicos por aba
    if (tab === 0) refreshWorkouts();
    if (tab === 2) carregarCategoriasNoSelect();
    if (tab === 3) loadAlunos();
}