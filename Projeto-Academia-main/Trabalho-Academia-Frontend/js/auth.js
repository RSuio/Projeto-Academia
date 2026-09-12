// ═══════════════════════════════════════════════════════════════
// auth.js — Login, Cadastro e Logout
// ═══════════════════════════════════════════════════════════════

const URL_BACKEND = "http://127.0.0.1:8000";

// Estado global do usuário — lido pelos outros módulos
let isLoggedIn  = false;
let currentUser = null;
let currentRole = null;  // "personal" | "aluno"
let currentUserId = null; // id do usuário logado (decodificado do token)

// Decodifica o "sub" (id) do token JWT armazenado
function buscarIdDoToken() {
    const token = localStorage.getItem('token_academia');
    if (!token) return null;
    try {
        const payload = token.split('.')[1];
        const decoded = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')));
        return decoded.sub ? parseInt(decoded.sub, 10) : null;
    } catch {
        return null;
    }
}

// --- Controle dos modais ---
function showLoginModal()    { document.getElementById('login-modal').classList.remove('hidden'); }
function hideLoginModal()    { document.getElementById('login-modal').classList.add('hidden'); }
function showRegisterModal() {
    document.getElementById('register-modal').classList.remove('hidden');
    selecionarTipoConta('aluno');
}
function hideRegisterModal() { document.getElementById('register-modal').classList.add('hidden'); }

// --- Tipo de conta (aluno / personal) ---
let contaTipo = 'aluno';

function selecionarTipoConta(tipo) {
    contaTipo = tipo;

    const classeAtiva   = ['bg-emerald-600', 'dark:bg-emerald-500', 'text-white', 'dark:text-black', 'shadow-md'];
    const classeInativa = ['bg-white', 'dark:bg-zinc-800', 'text-slate-700', 'dark:text-zinc-300', 'border', 'border-slate-300', 'dark:border-zinc-700'];

    ['aluno', 'personal'].forEach(t => {
        const btn = document.getElementById(`tipo-${t}`);
        if (!btn) return;
        btn.classList.remove(...classeAtiva, ...classeInativa);
        btn.classList.add(...(t === tipo ? classeAtiva : classeInativa));
    });

    const camposPersonal = document.getElementById('reg-personal-fields');
    if (camposPersonal) camposPersonal.classList.toggle('hidden', tipo !== 'personal');
}

// --- Cadastro ---
async function handleRegister() {
    const nome  = document.getElementById('reg-name').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const senha = document.getElementById('reg-password').value;

    const isPersonal    = contaTipo === 'personal';
    const especialidade = isPersonal ? document.getElementById('reg-especialidade').value.trim() : null;
    const bio           = isPersonal ? document.getElementById('reg-bio').value.trim() : null;

    if (!nome || !email || !senha) return showToast("Preencha todos os campos!", true);

    try {
        const response = await fetch(`${URL_BACKEND}/auth/criar_conta`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                nome,
                email,
                senha,
                admin: isPersonal,
                ativo: true,
                especialidade,
                bio
            })
        });
        const data = await response.json();

        if (response.ok) {
            showToast(isPersonal ? 'Conta de Personal criada com sucesso! 🎉 Faça login.' : 'Conta criada com sucesso! 🎉 Faça login.');
            hideRegisterModal();
            setTimeout(showLoginModal, 500);
        } else {
            showToast(`Erro: ${data.detail || "Não foi possível cadastrar."}`, true);
        }
    } catch {
        showToast("Erro ao conectar com o servidor.", true);
    }
}

// --- Login ---
async function handleLogin() {
    const email = document.getElementById('login-email').value.trim();
    const senha = document.getElementById('login-password').value;

    if (!email || !senha) return showToast("Preencha e-mail e senha!", true);

    try {
        const response = await fetch(`${URL_BACKEND}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, senha })
        });
        const data = await response.json();

        if (response.ok) {
            localStorage.setItem('token_academia', data.access_token);
            localStorage.setItem('is_admin', data.is_admin);

            isLoggedIn  = true;
            currentRole = data.is_admin ? "personal" : "aluno";
            currentUser = { nome: email.split('@')[0] };
            currentUserId = buscarIdDoToken();

            hideLoginModal();
            updateNavbar();
            navigateTo('dashboard');
            showToast(`Bem-vindo${currentRole === 'personal' ? ', Personal!' : ''}!`);
        } else {
            showToast(`Erro: ${data.detail || "Credenciais inválidas."}`, true);
        }
    } catch {
        showToast("Erro ao conectar com o servidor.", true);
    }
}

// --- Logout ---
function logout() {
    if (!confirm('Deseja realmente sair?')) return;

    localStorage.removeItem('token_academia');
    localStorage.removeItem('is_admin');
    isLoggedIn  = false;
    currentUser = null;
    currentRole = null;
    currentUserId = null;
    updateNavbar();
    navigateTo('home');
}

// --- Auto-login ao carregar a página ---
window.onload = () => {
    const token   = localStorage.getItem('token_academia');
    const isAdmin = localStorage.getItem('is_admin') === 'true';

    if (token) {
        isLoggedIn  = true;
        currentRole = isAdmin ? "personal" : "aluno";
        currentUser = { nome: "Usuário" };
        currentUserId = buscarIdDoToken();
        updateNavbar();       // garante botão de tema mesmo após reload
        navigateTo('dashboard');
    } else {
        updateNavbar();
    }
};