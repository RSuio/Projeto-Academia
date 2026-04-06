const URL_BACKEND = "http://127.0.0.1:8000";

let isLoggedIn = false;
let currentUser = null;
let currentRole = null; 

// --- CONTROLE DE MODAIS ---
function showLoginModal() { document.getElementById('login-modal').classList.remove('hidden'); }
function hideLoginModal() { document.getElementById('login-modal').classList.add('hidden'); }
function showRegisterModal() { document.getElementById('register-modal').classList.remove('hidden'); }
function hideRegisterModal() { document.getElementById('register-modal').classList.add('hidden'); }

// --- CADASTRO NO BACKEND ---
async function handleRegister() {
    const nome = document.getElementById('reg-name').value.trim();
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
    } catch (error) {
        showToast("Erro ao conectar com o servidor.", true);
    }
}

// --- LOGIN NO BACKEND ---
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
            
            isLoggedIn = true;
            currentRole = data.is_admin ? "personal" : "aluno";
            currentUser = { nome: email.split('@')[0] }; 

            hideLoginModal();
            updateNavbar();
            navigateTo('dashboard');
            showToast(`Bem-vindo${currentRole === 'personal' ? ', Personal!' : ''}!`);
        } else {
            showToast(`Erro: ${data.detail || "Credenciais inválidas."}`, true);
        }
    } catch (error) {
        showToast("Erro ao conectar com o servidor.", true);
    }
}

// --- LOGOUT ---
function logout() {
    if (confirm('Deseja realmente sair?')) {
        localStorage.removeItem('token_academia');
        localStorage.removeItem('is_admin');
        isLoggedIn = false;
        currentUser = null;
        currentRole = null;
        updateNavbar();
        navigateTo('home');
    }
}

// --- UI E NAVEGAÇÃO ---
function updateNavbar() {
    const nav = document.getElementById('nav-auth');
    if (isLoggedIn && currentUser) {
        nav.innerHTML = `
            <span onclick="navigateTo('dashboard')" class="cursor-pointer font-medium px-5 py-2 hover:text-emerald-400 transition-colors">
                Meu Painel
            </span>
            <button onclick="logout()" class="bg-zinc-800 hover:bg-zinc-700 px-5 py-2 rounded-3xl text-sm transition-colors font-medium border border-zinc-700">Sair</button>
        `;
    } else {
        nav.innerHTML = `
            <button onclick="showLoginModal()" class="font-medium px-6 py-2 hover:text-emerald-400 transition-colors">Entrar</button>
            <button onclick="showRegisterModal()" class="bg-emerald-500 text-black font-semibold px-6 py-2 rounded-3xl hover:bg-emerald-600 transition-colors">Criar conta</button>
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
    document.getElementById('dashboard-title').textContent = currentRole === 'personal' ? 'Painel do Personal Trainer' : 'Meus Treinos';
    document.getElementById('dashboard-subtitle').textContent = currentRole === 'personal' ? 'Gerencie seus treinos e alunos' : 'Acompanhe seus resultados';

    document.getElementById('tab-1-aluno').classList.toggle('hidden', currentRole !== 'aluno');
    document.getElementById('tab-2-personal').classList.toggle('hidden', currentRole !== 'personal');
    document.getElementById('tab-3-personal').classList.toggle('hidden', currentRole !== 'personal');

    switchTab(0);
}

// --- SISTEMA DE ABAS ---
function switchTab(tab) {
    document.querySelectorAll('.dashboard-tab').forEach(t => t.classList.remove('bg-emerald-500', 'text-black'));
    const activeTab = document.getElementById(`tab-${tab}`);
    if (activeTab) activeTab.classList.add('bg-emerald-500', 'text-black');

    document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
    document.getElementById(`content-${tab}`).classList.remove('hidden');

    if (tab === 0) refreshWorkouts();
    if (tab === 3) loadAlunos();
}

// --- BUSCAR TREINOS DO USUÁRIO ---
async function refreshWorkouts() {
    const grid = document.getElementById('workouts-grid');
    const token = localStorage.getItem('token_academia');

    if (!token) return;

    grid.innerHTML = '<div class="col-span-full text-center py-10 text-zinc-400">Carregando seus treinos...</div>';

    try {
        const response = await fetch(`${URL_BACKEND}/treinos/meus-treinos`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const treinos = await response.json();

            if (treinos.length === 0) {
                grid.innerHTML = `
                    <div class="col-span-full text-center py-20 text-zinc-400 border border-zinc-800 rounded-3xl bg-zinc-900/50">
                        <i class="fa-solid fa-dumbbell text-6xl mb-4 opacity-30"></i>
                        <p class="text-lg">Nenhum treino carregado ainda.</p>
                        <p class="text-sm mt-2">Seus treinos aparecerão aqui assim que ${currentRole === 'personal' ? 'você criá-los' : 'o Personal Trainer atribuir'}.</p>
                    </div>
                `;
                return;
            }

            grid.innerHTML = '';
            
            treinos.forEach(treino => {
                const card = document.createElement('div');
                card.className = "bg-zinc-900 border border-zinc-800 p-6 rounded-3xl hover:border-emerald-500/50 transition-colors card-hover";

                let exerciciosHTML = '<ul class="mt-4 space-y-2">';
                treino.exercicios.forEach(ex => {
                    const cargaTexto = ex.carga ? `${ex.carga}kg` : 'Sem peso';
                    exerciciosHTML += `
                        <li class="flex justify-between items-center text-sm border-b border-zinc-800/50 pb-2">
                            <span class="text-zinc-300 font-medium">${ex.nome}</span>
                            <span class="text-zinc-500 bg-zinc-950 border border-zinc-800 px-2 py-1 rounded-md text-xs">
                                ${ex.series}x${ex.repeticoes} | ${cargaTexto}
                            </span>
                        </li>
                    `;
                });
                exerciciosHTML += '</ul>';

                card.innerHTML = `
                    <div class="flex justify-between items-start mb-2">
                        <h3 class="text-xl font-bold text-white">${treino.nome}</h3>
                        <span class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs px-3 py-1 rounded-full font-medium">
                            ${treino.objetivo || 'Geral'}
                        </span>
                    </div>
                    ${exerciciosHTML}
                `;
                
                grid.appendChild(card);
            });

        } else {
            const data = await response.json();
            showToast(`Erro: ${data.detail || "Não foi possível carregar."}`, true);
        }
    } catch (error) {
        grid.innerHTML = '<div class="col-span-full text-center py-10 text-red-400">Falha de conexão com o servidor.</div>';
    }
}

// --- BUSCAR ALUNOS (SÓ PERSONAL) ---
async function loadAlunos() {
    const container = document.querySelector('#content-3 > div:nth-child(2)');
    const token = localStorage.getItem('token_academia');

    if (!token || currentRole !== 'personal') return;

    container.innerHTML = '<p class="text-zinc-400 animate-pulse w-full text-center py-10">Buscando alunos no sistema...</p>';
    container.classList.add('text-center');

    try {
        const response = await fetch(`${URL_BACKEND}/auth/alunos`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const alunos = await response.json();

            if (alunos.length === 0) {
                container.innerHTML = `
                    <i class="fa-solid fa-users-slash text-6xl mb-4 opacity-30"></i>
                    <p class="text-zinc-400">Nenhum aluno encontrado no sistema.</p>
                `;
                return;
            }

            let html = '<div class="flex flex-col gap-4 w-full">';
            alunos.forEach(aluno => {
                html += `
                    <div class="bg-zinc-950 border border-zinc-800 p-5 rounded-2xl flex justify-between items-center hover:border-emerald-500/50 transition-colors">
                        <div class="flex items-center gap-4">
                            <div class="w-12 h-12 bg-zinc-800 rounded-full flex items-center justify-center text-emerald-400 font-bold text-xl">
                                ${aluno.nome.charAt(0).toUpperCase()}
                            </div>
                            <div class="text-left">
                                <h3 class="text-white font-bold text-lg leading-tight">${aluno.nome}</h3>
                                <p class="text-zinc-500 text-sm mt-1">
                                    ID: <span class="text-emerald-400 font-mono bg-zinc-900 px-2 rounded">${aluno.id}</span> | ${aluno.email}
                                </p>
                            </div>
                        </div>
                        <button onclick="copiarIdAluno(${aluno.id})" class="bg-zinc-800 hover:bg-emerald-500 hover:text-black px-4 py-2 rounded-xl text-sm font-medium transition-colors">
                            Usar ID
                        </button>
                    </div>
                `;
            });
            html += '</div>';
            
            container.innerHTML = html;
            container.classList.remove('text-center');

        } else {
            const data = await response.json();
            container.innerHTML = `<p class="text-red-400 w-full text-center py-10">Erro: ${data.detail || 'Falha ao buscar alunos'}</p>`;
        }
    } catch (error) {
        console.error(error);
        container.innerHTML = '<p class="text-red-400 w-full text-center py-10">Falha de conexão com o servidor.</p>';
    }
}

function copiarIdAluno(id) {
    document.getElementById('new-treino-id-aluno').value = id;
    showToast(`ID ${id} selecionado! Vamos criar o treino.`);
    switchTab(2); 
}

// --- LÓGICA DE ADICIONAR LINHA DE EXERCÍCIO ---
function addExercicioRow() {
    const container = document.getElementById('exercicios-container');
    const row = document.createElement('div');
    row.className = "flex gap-2 items-center exercicio-row animate-modalPop";
    row.innerHTML = `
        <input type="text" placeholder="Nome (Ex: Supino)" class="ex-nome flex-1 bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 focus:outline-none focus:border-emerald-400 text-sm">
        <input type="number" placeholder="Sér." class="ex-series w-20 bg-zinc-950 border border-zinc-800 rounded-xl px-2 py-3 focus:outline-none focus:border-emerald-400 text-sm text-center" min="1">
        <input type="number" placeholder="Rep." class="ex-reps w-20 bg-zinc-950 border border-zinc-800 rounded-xl px-2 py-3 focus:outline-none focus:border-emerald-400 text-sm text-center" min="1">
        <input type="text" placeholder="Carga" class="ex-carga w-24 bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-3 focus:outline-none focus:border-emerald-400 text-sm text-center">
        <button onclick="this.parentElement.remove()" class="text-zinc-600 hover:text-red-500 px-3 py-3 transition-colors bg-zinc-900 rounded-xl" title="Remover exercício">
            <i class="fa-solid fa-trash"></i>
        </button>
    `;
    container.appendChild(row);
}

window.addEventListener('DOMContentLoaded', () => {
    addExercicioRow(); 
});

// --- SALVAR TREINO NO BACKEND ---
async function createNewTreino() {
    const idAluno = document.getElementById('new-treino-id-aluno').value;
    const nomeTreino = document.getElementById('new-treino-name').value;
    const objetivo = document.getElementById('new-treino-objetivo').value.trim();
    const token = localStorage.getItem('token_academia');

    if (!token) return showToast("Você precisa estar logado!", true);
    if (!idAluno || !nomeTreino) {
        return showToast("Preencha o ID do aluno e o Nome do treino!", true);
    }

    const exercicioRows = document.querySelectorAll('.exercicio-row');
    const listaExercicios = [];

    exercicioRows.forEach(row => {
        const nome = row.querySelector('.ex-nome').value.trim();
        const series = parseInt(row.querySelector('.ex-series').value) || 0;
        const repeticoes = parseInt(row.querySelector('.ex-reps').value) || 0; 
        const carga = row.querySelector('.ex-carga').value.trim();

        if (nome) {
            listaExercicios.push({ 
                nome: nome, 
                series: series, 
                repeticoes: repeticoes, 
                carga: carga !== "" ? carga : null 
            });
        }
    });

    if (listaExercicios.length === 0) {
        return showToast("Adicione pelo menos um exercício preenchido!", true);
    }

    const payloadTreino = {
        usuario_id: parseInt(idAluno),
        nome: nomeTreino,
        objetivo: objetivo !== "" ? objetivo : null,
        exercicios: listaExercicios
    };

    console.log("Enviando para o Back-end:", payloadTreino);

    const btnSalvar = document.querySelector('button[onclick="createNewTreino()"]');
    const textoOriginal = btnSalvar.innerHTML;
    btnSalvar.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Cadastrando...';
    btnSalvar.disabled = true;

    try {
        const response = await fetch(`${URL_BACKEND}/treinos/cadastrar-completo`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(payloadTreino)
        });

        const data = await response.json();

        if (response.ok) {
            showToast(data.mensagem || "Treino cadastrado com sucesso! 💪");
            
            document.getElementById('new-treino-id-aluno').value = '';
            document.getElementById('new-treino-name').value = '';
            document.getElementById('new-treino-objetivo').value = '';
            document.getElementById('exercicios-container').innerHTML = '';
            addExercicioRow(); 

            setTimeout(() => switchTab(0), 2000);
            
        } else {
            if (response.status === 422) {
                console.error("ERRO 422 (Validação):", data.detail);
                showToast(`Erro de formato! Verifique o console.`, true);
            } else {
                showToast(`Erro: ${data.detail || "Erro ao salvar treino."}`, true);
            }
        }
    } catch (error) {
        console.error("Erro na requisição:", error);
        showToast("Erro de conexão com o servidor.", true);
    } finally {
        btnSalvar.innerHTML = textoOriginal;
        btnSalvar.disabled = false;
    }
}

// --- SISTEMA DE AVISOS (TOAST) ---
function showToast(message, error = false) {
    const toast = document.getElementById('toast');
    const text = document.getElementById('toast-text');
    text.textContent = message;
    toast.style.backgroundColor = error ? '#ef4444' : '#10b981';
    toast.style.color = error ? '#ffffff' : '#000000';
    
    toast.classList.remove('hidden');
    toast.classList.add('animate-bounce');
    
    setTimeout(() => {
        toast.classList.add('hidden');
        toast.classList.remove('animate-bounce');
    }, 3500);
}

// --- INICIALIZAÇÃO (AUTO-LOGIN) ---
window.onload = () => {
    const token = localStorage.getItem('token_academia');
    const isAdmin = localStorage.getItem('is_admin') === 'true';

    if (token) {
        isLoggedIn = true;
        currentRole = isAdmin ? "personal" : "aluno";
        currentUser = { nome: "Usuário" }; 
        navigateTo('dashboard');
    } else {
        updateNavbar();
    }
};