// ═══════════════════════════════════════════════════════════════
// navigation.js — Navbar, Alternador de Tema, Rotas e Abas
// ═══════════════════════════════════════════════════════════════

function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }
    updateThemeToggleButton();
}

function toggleTheme() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    updateThemeToggleButton();
}

function updateThemeToggleButton() {
    const buttons = document.querySelectorAll('.theme-toggle-btn');
    const isDark = document.documentElement.classList.contains('dark');
    
    buttons.forEach(btn => {
        const isFullWidth = btn.classList.contains('w-full');

        if (isFullWidth) {
            btn.innerHTML = isDark 
                ? `<span class="flex items-center gap-3"><i class="fa-solid fa-sun text-amber-400"></i> Modo Claro</span><span class="text-xs text-zinc-400 bg-zinc-800 px-2.5 py-1 rounded-full border border-zinc-700">Ativo</span>` 
                : `<span class="flex items-center gap-3"><i class="fa-solid fa-moon text-slate-600"></i> Modo Escuro</span><span class="text-xs text-slate-500 bg-slate-100 px-2.5 py-1 rounded-full border border-slate-300">Ativo</span>`;
        } else {
            btn.innerHTML = isDark 
                ? `<i class="fa-solid fa-sun text-amber-400"></i><span class="hidden sm:inline">Modo Claro</span>` 
                : `<i class="fa-solid fa-moon text-slate-600"></i><span class="hidden sm:inline">Modo Escuro</span>`;
                
            btn.className = isDark
                ? `theme-toggle-btn flex items-center gap-2 px-3.5 py-2 rounded-full text-xs font-semibold bg-zinc-800 text-zinc-200 hover:bg-zinc-700 transition-all border border-zinc-700 shadow-xs cursor-pointer`
                : `theme-toggle-btn flex items-center gap-2 px-3.5 py-2 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 transition-all border border-slate-300 shadow-xs cursor-pointer`;
        }
    });
}

function updateNavbar() {
    const nav = document.getElementById('nav-auth');

    const themeBtnHTML = `
        <button class="theme-toggle-btn" onclick="toggleTheme()" type="button" aria-label="Alternar Tema"></button>
    `;

    if (isLoggedIn && currentUser) {
        nav.innerHTML = `
            ${themeBtnHTML}
            <span onclick="navigateTo('dashboard')"
                  class="cursor-pointer font-medium px-4 py-2 text-slate-700 dark:text-zinc-300 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors">
                Meu Painel
            </span>
        `;
    } else {
        nav.innerHTML = `
            ${themeBtnHTML}
            <button onclick="showLoginModal()"
                    class="font-medium px-4 py-2 text-slate-700 dark:text-zinc-300 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors">
                Entrar
            </button>
            <button onclick="showRegisterModal()"
                    class="bg-emerald-600 hover:bg-emerald-700 dark:bg-emerald-500 dark:hover:bg-emerald-600 text-white dark:text-black font-semibold px-5 py-2 rounded-full transition-colors shadow-sm">
                Criar conta
            </button>
        `;
    }
    updateThemeToggleButton();
}

function navigateTo(view) {
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

    updateThemeToggleButton();

    // Personal inicia na aba de Alunos (3), Aluno na aba de Treinos (0)
    switchTab(isPersonal ? 3 : 0);
}

function switchTab(tab) {
    // Remove destaque de todas as abas
    document.querySelectorAll('.dashboard-tab').forEach(t => {
        t.classList.remove('bg-emerald-600', 'dark:bg-emerald-500', 'text-white', 'dark:text-black', 'shadow-md');
        t.classList.add('bg-white', 'dark:bg-zinc-900', 'text-slate-700', 'dark:text-zinc-300', 'border', 'border-slate-200', 'dark:border-zinc-800');
    });

    // Destaca a aba ativa
    const activeTab = document.getElementById(`tab-${tab}`);
    if (activeTab) {
        activeTab.classList.remove('bg-white', 'dark:bg-zinc-900', 'text-slate-700', 'dark:text-zinc-300', 'border-slate-200', 'dark:border-zinc-800');
        activeTab.classList.add('bg-emerald-600', 'dark:bg-emerald-500', 'text-white', 'dark:text-black', 'shadow-md');
    }

    // Oculta todos os conteúdos e exibe o correto
    document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
    document.getElementById(`content-${tab}`).classList.remove('hidden');

    // Carregamentos específicos por aba
    if (tab === 0) refreshWorkouts();
    if (tab === 1) { carregarProgresso(); carregarObjetivo(); }
    if (tab === 2) carregarCategoriasNoSelect();
    if (tab === 3) loadAlunos();
}

// Inicializa tema ao carregar script
document.addEventListener('DOMContentLoaded', initTheme);