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
    // Se o painel já estiver visível, não faz nada para não resetar a aba ativa do usuário
    if (view === 'dashboard' && isLoggedIn) {
        const dbView = document.getElementById('dashboard-view');
        if (dbView && !dbView.classList.contains('hidden')) {
            return;
        }
    }

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
    document.getElementById('tab-1').classList.toggle('hidden', isPersonal);
    document.getElementById('tab-2').classList.toggle('hidden', !isPersonal);
    document.getElementById('tab-3').classList.toggle('hidden', !isPersonal);

    // Personal inicia na aba de Alunos (3), Aluno na aba de Treinos (0)
    switchTab(isPersonal ? 3 : 0);
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
    if (tab === 1) { carregarProgresso(); carregarObjetivo(); }
    if (tab === 2) carregarCategoriasNoSelect();
    if (tab === 3) loadAlunos();
}