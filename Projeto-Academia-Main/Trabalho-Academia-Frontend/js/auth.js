// ═══════════════════════════════════════════════════════════════
// auth.js — Login, Cadastro e Logout
// ═══════════════════════════════════════════════════════════════

const URL_BACKEND = "http://127.0.0.1:8000";

// Estado global do usuário — lido pelos outros módulos
let isLoggedIn  = false;
let currentUser = null;
let currentRole = null;  // "personal" | "aluno"

// --- Controle dos modais ---
function showLoginModal()    { document.getElementById('login-modal').classList.remove('hidden'); }
function hideLoginModal()    { document.getElementById('login-modal').classList.add('hidden'); }
function showRegisterModal() { document.getElementById('register-modal').classList.remove('hidden'); }
function hideRegisterModal() { document.getElementById('register-modal').classList.add('hidden'); }

// --- Cadastro ---
async function handleRegister() {
    const nome  = document.getElementById('reg-name').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const senha = document.getElementById('reg-password').value;

    if (!nome || !email || !senha) return showToast("Preencha todos os campos!", true);

    try {
        const response = await fetch(`${URL_BACKEND}/auth/criar_conta`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nome, email, senha, admin: false, ativo: true })
        });
        const data = await response.json();

        if (response.ok) {
            showToast('Conta criada com sucesso! 🎉 Faça login.');
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
        navigateTo('dashboard');
    } else {
        updateNavbar();
    }
};