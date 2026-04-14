const URL_BACKEND = "http://127.0.0.1:8000";

let isLoggedIn = false;
let currentUser = null;
let currentRole = null;

// --- CONTROLE DE MODAIS ---
function showLoginModal() { document.getElementById('login-modal').classList.remove('hidden'); }
function hideLoginModal() { document.getElementById('login-modal').classList.add('hidden'); }
function showRegisterModal() { document.getElementById('register-modal').classList.remove('hidden'); }
function hideRegisterModal() { document.getElementById('register-modal').classList.add('hidden'); }

// --- CADASTRO ---
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
    } catch {
        showToast("Erro ao conectar com o servidor.", true);
    }
}

// --- LOGIN ---
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
    } catch {
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

// --- NAVBAR ---
function updateNavbar() {
    const nav = document.getElementById('nav-auth');
    if (isLoggedIn && currentUser) {
        nav.innerHTML = `
            <span onclick="navigateTo('dashboard')" class="cursor-pointer font-medium px-5 py-2 hover:text-emerald-400 transition-colors">Meu Painel</span>
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

function switchTab(tab) {
    document.querySelectorAll('.dashboard-tab').forEach(t => t.classList.remove('bg-emerald-500', 'text-black'));
    const activeTab = document.getElementById(`tab-${tab}`);
    if (activeTab) activeTab.classList.add('bg-emerald-500', 'text-black');
    document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
    document.getElementById(`content-${tab}`).classList.remove('hidden');
    if (tab === 0) refreshWorkouts();
    if (tab === 3) loadAlunos();
}

// --- TREINOS ---
async function refreshWorkouts() {
    const grid = document.getElementById('workouts-grid');
    const token = localStorage.getItem('token_academia');
    if (!token) return;

    grid.innerHTML = '<div class="col-span-full text-center py-10 text-zinc-400">Carregando seus treinos...</div>';

    try {
        const response = await fetch(`${URL_BACKEND}/treinos/meus-treinos`, {
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
                    </div>`;
                return;
            }

            grid.innerHTML = '';
            treinos.forEach(treino => {
                const card = document.createElement('div');
                card.className = "bg-zinc-900 border border-zinc-800 p-6 rounded-3xl hover:border-emerald-500/50 transition-colors card-hover";

                let exerciciosHTML = '<ul class="mt-4 space-y-2">';
                treino.exercicios.forEach(ex => {
                    const cargaTexto = ex.carga ? `${ex.carga}kg` : 'Peso corporal';
                    // Suporta tanto o schema antigo (ex.nome) quanto o novo (ex.nome_exercicio)
                    const nomeExercicio = ex.nome_exercicio || ex.nome || 'Exercício';
                    exerciciosHTML += `
                        <li class="flex justify-between items-center text-sm border-b border-zinc-800/50 pb-2">
                            <span class="text-zinc-300 font-medium">${nomeExercicio}</span>
                            <span class="text-zinc-500 bg-zinc-950 border border-zinc-800 px-2 py-1 rounded-md text-xs">
                                ${ex.series}x${ex.repeticoes} | ${cargaTexto}
                            </span>
                        </li>`;
                });
                exerciciosHTML += '</ul>';

                card.innerHTML = `
                    <div class="flex justify-between items-start mb-2">
                        <h3 class="text-xl font-bold text-white">${treino.nome}</h3>
                        <span class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs px-3 py-1 rounded-full font-medium">
                            ${treino.objetivo || 'Geral'}
                        </span>
                    </div>
                    ${exerciciosHTML}`;
                grid.appendChild(card);
            });
        } else {
            const data = await response.json();
            showToast(`Erro: ${data.detail || "Não foi possível carregar."}`, true);
        }
    } catch {
        grid.innerHTML = '<div class="col-span-full text-center py-10 text-red-400">Falha de conexão com o servidor.</div>';
    }
}

// --- ALUNOS ---
async function loadAlunos() {
    const container = document.querySelector('#content-3 > div:nth-child(2)');
    const token = localStorage.getItem('token_academia');
    if (!token || currentRole !== 'personal') return;

    container.innerHTML = '<p class="text-zinc-400 animate-pulse w-full text-center py-10">Buscando alunos no sistema...</p>';
    container.classList.add('text-center');

    try {
        const response = await fetch(`${URL_BACKEND}/auth/alunos`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const alunos = await response.json();
            if (alunos.length === 0) {
                container.innerHTML = `<i class="fa-solid fa-users-slash text-6xl mb-4 opacity-30"></i><p class="text-zinc-400">Nenhum aluno encontrado.</p>`;
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
                    </div>`;
            });
            html += '</div>';
            container.innerHTML = html;
            container.classList.remove('text-center');
        } else {
            const data = await response.json();
            container.innerHTML = `<p class="text-red-400 w-full text-center py-10">Erro: ${data.detail || 'Falha ao buscar alunos'}</p>`;
        }
    } catch {
        container.innerHTML = '<p class="text-red-400 w-full text-center py-10">Falha de conexão com o servidor.</p>';
    }
}

function copiarIdAluno(id) {
    document.getElementById('new-treino-id-aluno').value = id;
    showToast(`ID ${id} selecionado! Vamos criar o treino.`);
    switchTab(2);
}


// ═══════════════════════════════════════════════════════════════
// AUTOCOMPLETE DE EXERCÍCIOS DO CATÁLOGO
// ═══════════════════════════════════════════════════════════════

// Guarda o debounce de cada input para não disparar a cada tecla
const debounceTimers = new WeakMap();

/**
 * Cria uma linha de exercício com campo de busca + autocomplete.
 * O campo de texto busca no catálogo; ao selecionar, guarda o exercicio_catalogo_id.
 */
function addExercicioRow() {
    const container = document.getElementById('exercicios-container');
    const rowId = `ex-row-${Date.now()}`;

    const row = document.createElement('div');
    row.className = "exercicio-row animate-modalPop";
    row.id = rowId;

    row.innerHTML = `
        <div class="flex gap-2 items-start">

            <!-- Campo de busca com autocomplete -->
            <div class="flex-1 relative">
                <input
                    type="text"
                    placeholder="Buscar exercício (ex: supino)..."
                    class="ex-busca w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 focus:outline-none focus:border-emerald-400 text-sm"
                    autocomplete="off"
                    oninput="onBuscaInput(this, '${rowId}')"
                    onfocus="onBuscaInput(this, '${rowId}')"
                >
                <!-- Dropdown de resultados -->
                <div class="ex-dropdown hidden absolute top-full left-0 right-0 mt-1 bg-zinc-900 border border-zinc-700 rounded-xl z-50 max-h-52 overflow-y-auto shadow-xl">
                </div>
                <!-- Exercício selecionado (fica visível após escolha) -->
                <div class="ex-selecionado hidden mt-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 rounded-xl flex items-center justify-between">
                    <span class="ex-selecionado-nome text-sm text-emerald-400 font-medium"></span>
                    <button onclick="limparSelecao('${rowId}')" class="text-zinc-500 hover:text-red-400 text-xs ml-2 transition-colors">
                        <i class="fa-solid fa-xmark"></i> trocar
                    </button>
                </div>
                <!-- ID selecionado (oculto, vai no payload) -->
                <input type="hidden" class="ex-catalogo-id">
            </div>

            <!-- Séries / Reps / Carga -->
            <input type="number" placeholder="Sér." min="1"
                   class="ex-series w-20 bg-zinc-950 border border-zinc-800 rounded-xl px-2 py-3 focus:outline-none focus:border-emerald-400 text-sm text-center">
            <input type="number" placeholder="Rep." min="1"
                   class="ex-reps w-20 bg-zinc-950 border border-zinc-800 rounded-xl px-2 py-3 focus:outline-none focus:border-emerald-400 text-sm text-center">
            <input type="text" placeholder="Carga"
                   class="ex-carga w-24 bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-3 focus:outline-none focus:border-emerald-400 text-sm text-center">
            <button onclick="document.getElementById('${rowId}').remove()"
                    class="text-zinc-600 hover:text-red-500 px-3 py-3 transition-colors bg-zinc-900 rounded-xl" title="Remover">
                <i class="fa-solid fa-trash"></i>
            </button>
        </div>
    `;

    container.appendChild(row);
}

/**
 * Dispara a busca com debounce de 300ms para não sobrecarregar o backend.
 */
function onBuscaInput(input, rowId) {
    const row = document.getElementById(rowId);
    if (!row) return;

    // Cancela timer anterior deste input
    if (debounceTimers.has(input)) clearTimeout(debounceTimers.get(input));

    const timer = setTimeout(() => buscarNoCatalogo(input, rowId), 300);
    debounceTimers.set(input, timer);
}

/**
 * Chama GET /exercicios/catalogo?busca=... e renderiza o dropdown.
 */
async function buscarNoCatalogo(input, rowId) {
    const row = document.getElementById(rowId);
    if (!row) return;

    const termo = input.value.trim();
    const dropdown = row.querySelector('.ex-dropdown');

    // Oculta dropdown se busca muito curta
    if (termo.length < 2) {
        dropdown.classList.add('hidden');
        dropdown.innerHTML = '';
        return;
    }

    const token = localStorage.getItem('token_academia');

    try {
        const response = await fetch(
            `${URL_BACKEND}/exercicios/catalogo?busca=${encodeURIComponent(termo)}&limit=10`,
            { headers: { 'Authorization': `Bearer ${token}` } }
        );

        if (!response.ok) return;

        const resultados = await response.json();
        renderizarDropdown(resultados, dropdown, rowId);

    } catch {
        // Silencia erro de rede para não poluir UX
    }
}

/**
 * Renderiza os itens do dropdown.
 */
function renderizarDropdown(resultados, dropdown, rowId) {
    dropdown.innerHTML = '';

    if (resultados.length === 0) {
        dropdown.innerHTML = `<p class="text-zinc-500 text-xs text-center py-4">Nenhum exercício encontrado.</p>`;
        dropdown.classList.remove('hidden');
        return;
    }

    resultados.forEach(ex => {
        const item = document.createElement('button');
        item.type = 'button';
        item.className = "w-full text-left px-4 py-3 hover:bg-zinc-800 transition-colors border-b border-zinc-800/50 last:border-0";

        const musculo = ex.musculo_principal ? `<span class="text-emerald-400/70">${ex.musculo_principal}</span>` : '';
        const categoria = ex.categoria ? `<span class="text-zinc-600">${ex.categoria}</span>` : '';

        item.innerHTML = `
            <p class="text-sm text-white font-medium leading-tight">${ex.nome}</p>
            <p class="text-xs mt-0.5 flex gap-2">${musculo}${categoria}</p>
        `;

        item.onclick = () => selecionarExercicio(rowId, ex);
        dropdown.appendChild(item);
    });

    dropdown.classList.remove('hidden');

    // Fecha dropdown ao clicar fora
    setTimeout(() => {
        document.addEventListener('click', function fechar(e) {
            const row = document.getElementById(rowId);
            if (row && !row.contains(e.target)) {
                dropdown.classList.add('hidden');
                document.removeEventListener('click', fechar);
            }
        });
    }, 0);
}

/**
 * Registra a escolha do personal: guarda o id, exibe o nome, oculta o campo de busca.
 */
function selecionarExercicio(rowId, exercicio) {
    const row = document.getElementById(rowId);
    if (!row) return;

    row.querySelector('.ex-catalogo-id').value = exercicio.id;
    row.querySelector('.ex-selecionado-nome').textContent = exercicio.nome;
    row.querySelector('.ex-selecionado').classList.remove('hidden');
    row.querySelector('.ex-busca').classList.add('hidden');
    row.querySelector('.ex-dropdown').classList.add('hidden');
}

/**
 * Limpa a seleção e mostra o campo de busca de novo.
 */
function limparSelecao(rowId) {
    const row = document.getElementById(rowId);
    if (!row) return;

    row.querySelector('.ex-catalogo-id').value = '';
    row.querySelector('.ex-selecionado-nome').textContent = '';
    row.querySelector('.ex-selecionado').classList.add('hidden');

    const busca = row.querySelector('.ex-busca');
    busca.classList.remove('hidden');
    busca.value = '';
    busca.focus();
}


// ═══════════════════════════════════════════════════════════════
// SALVAR TREINO
// ═══════════════════════════════════════════════════════════════

async function createNewTreino() {
    const idAluno = document.getElementById('new-treino-id-aluno').value;
    const nomeTreino = document.getElementById('new-treino-name').value.trim();
    const objetivo = document.getElementById('new-treino-objetivo').value.trim();
    const token = localStorage.getItem('token_academia');

    if (!token) return showToast("Você precisa estar logado!", true);
    if (!idAluno || !nomeTreino) return showToast("Preencha o ID do aluno e o Nome do treino!", true);

    const listaExercicios = [];
    let erroValidacao = false;

    document.querySelectorAll('.exercicio-row').forEach(row => {
        const catalogoId = row.querySelector('.ex-catalogo-id')?.value;
        const series    = parseInt(row.querySelector('.ex-series')?.value) || 0;
        const reps      = parseInt(row.querySelector('.ex-reps')?.value) || 0;
        const cargaVal  = row.querySelector('.ex-carga')?.value.trim();

        if (!catalogoId) {
            // Linha sem exercício selecionado — destaca visualmente
            row.querySelector('.ex-busca')?.classList.add('border-red-500');
            erroValidacao = true;
            return;
        }

        listaExercicios.push({
            exercicio_catalogo_id: parseInt(catalogoId),
            series,
            repeticoes: reps,
            carga: cargaVal !== "" ? parseFloat(cargaVal) : null,
            ordem: listaExercicios.length + 1
        });
    });

    if (erroValidacao) return showToast("Selecione um exercício do catálogo em cada linha!", true);
    if (listaExercicios.length === 0) return showToast("Adicione pelo menos um exercício!", true);

    const payload = {
        usuario_id: parseInt(idAluno),
        nome: nomeTreino,
        objetivo: objetivo || null,
        exercicios: listaExercicios
    };

    const btnSalvar = document.querySelector('button[onclick="createNewTreino()"]');
    const textoOriginal = btnSalvar.innerHTML;
    btnSalvar.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Salvando...';
    btnSalvar.disabled = true;

    try {
        const response = await fetch(`${URL_BACKEND}/treinos/cadastrar-completo`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
            showToast(data.mensagem || "Treino criado com sucesso! 💪");
            document.getElementById('new-treino-id-aluno').value = '';
            document.getElementById('new-treino-name').value = '';
            document.getElementById('new-treino-objetivo').value = '';
            document.getElementById('exercicios-container').innerHTML = '';
            addExercicioRow();
            setTimeout(() => switchTab(0), 2000);
        } else {
            if (response.status === 422) {
                console.error("ERRO 422:", data.detail);
                showToast("Erro de formato! Verifique o console.", true);
            } else {
                showToast(`Erro: ${data.detail || "Erro ao salvar treino."}`, true);
            }
        }
    } catch {
        showToast("Erro de conexão com o servidor.", true);
    } finally {
        btnSalvar.innerHTML = textoOriginal;
        btnSalvar.disabled = false;
    }
}

// --- TOAST ---
function showToast(message, error = false) {
    const toast = document.getElementById('toast');
    const text = document.getElementById('toast-text');
    text.textContent = message;
    toast.style.backgroundColor = error ? '#ef4444' : '#10b981';
    toast.style.color = error ? '#ffffff' : '#000000';
    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), 3500);
}

// --- INICIALIZAÇÃO ---
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

window.addEventListener('DOMContentLoaded', () => addExercicioRow());

// 1. Função chamada quando o usuário escolhe um objetivo no select
async function carregarExerciciosPorObjetivo(objetivo) {
    const containerCards = document.getElementById('cards-exercicios-container');
    const gridCards = document.getElementById('grid-cards');

    if (!objetivo) {
        containerCards.classList.add('hidden');
        return;
    }

    // Mostra a área de cards e exibe um "Carregando..."
    containerCards.classList.remove('hidden');
    gridCards.innerHTML = '<p class="text-zinc-500 col-span-full text-center py-4">Buscando exercícios...</p>';

    try {
        // ASSIM SERÁ A SUA REQUISIÇÃO REAL PARA O BACKEND QUANDO A ROTA ESTIVER PRONTA:
        // const response = await fetch(`http://127.0.0.1:8000/exercicios/buscar?objetivo=${objetivo}`);
        // const exercicios = await response.json();

        // -------------------------------------------------------------
        // MOCK TEMPORÁRIO: (Para você já ver funcionando na tela hoje)
        const exerciciosBancoDeDados = {
            hipertrofia: ['Supino Reto', 'Agachamento Livre', 'Rosca Direta', 'Leg Press 45', 'Crucifixo'],
            emagrecimento: ['Burpee', 'Polichinelo', 'Corda', 'Mountain Climber'],
            forca: ['Levantamento Terra', 'Supino Força', 'Agachamento Pesado'],
            resistencia: ['Prancha', 'Flexão de Braço', 'Corrida Estática']
        };
        // Simulando um delay de internet
        await new Promise(r => setTimeout(r, 500)); 
        const exercicios = exerciciosBancoDeDados[objetivo] || [];
        // -------------------------------------------------------------

        // Limpa o grid para colocar os cards reais
        gridCards.innerHTML = ''; 

        if (exercicios.length === 0) {
            gridCards.innerHTML = '<p class="text-zinc-500 col-span-full text-center">Nenhum exercício encontrado.</p>';
            return;
        }

        // Desenha um card HTML para cada exercício que veio do banco
        exercicios.forEach(nomeExercicio => {
            const card = document.createElement('div');
            // Classes do Tailwind para fazer o card ficar bonito e clicável
            card.className = "bg-zinc-800 border border-zinc-700 hover:border-emerald-500 rounded-xl p-3 cursor-pointer transition-all text-center flex flex-col items-center gap-2 group hover:-translate-y-1";
            card.onclick = () => adicionarExercicioAoTreino(nomeExercicio);
            
            card.innerHTML = `
                <div class="w-10 h-10 bg-zinc-900 rounded-full flex items-center justify-center text-zinc-400 group-hover:text-emerald-500 group-hover:bg-emerald-500/10 transition-colors">
                    <i class="fa-solid fa-dumbbell"></i>
                </div>
                <span class="text-xs font-medium text-zinc-300 group-hover:text-white">${nomeExercicio}</span>
            `;
            
            gridCards.appendChild(card);
        });

    } catch (error) {
        console.error(error);
        gridCards.innerHTML = '<p class="text-red-500 col-span-full text-center">Erro ao buscar exercícios.</p>';
    }
}

// 2. Função chamada quando o usuário clica em um Card
function adicionarExercicioAoTreino(nomeExercicio) {
    const container = document.getElementById('exercicios-container');
    
    const linhaExercicio = document.createElement('div');
    linhaExercicio.className = "flex items-center gap-2 sm:gap-3 bg-zinc-800/50 p-2 sm:p-3 rounded-xl border border-zinc-700/50 animate-fade-in";
    
    // Constrói a linha com o nome bloqueado e os inputs de Sér/Rep/Carga vazios
    linhaExercicio.innerHTML = `
        <div class="flex-1 min-w-[120px]">
            <input type="text" value="${nomeExercicio}" readonly 
                   class="w-full bg-transparent border-none text-emerald-400 font-medium focus:outline-none cursor-default text-sm sm:text-base">
        </div>
        <input type="number" placeholder="Sér." required
               class="w-14 sm:w-16 bg-zinc-900 border border-zinc-700 rounded-lg px-1 sm:px-2 py-2 text-center text-sm focus:outline-none focus:border-emerald-400 text-white">
        <input type="number" placeholder="Rep." required
               class="w-14 sm:w-16 bg-zinc-900 border border-zinc-700 rounded-lg px-1 sm:px-2 py-2 text-center text-sm focus:outline-none focus:border-emerald-400 text-white">
        <input type="text" placeholder="Kg" required
               class="w-14 sm:w-16 bg-zinc-900 border border-zinc-700 rounded-lg px-1 sm:px-2 py-2 text-center text-sm focus:outline-none focus:border-emerald-400 text-white">
        <button type="button" onclick="this.parentElement.remove()" 
                class="text-zinc-500 hover:text-red-500 px-2 transition-colors">
            <i class="fa-solid fa-trash"></i>
        </button>
    `;
    
    container.appendChild(linhaExercicio);

    // Se você tiver uma função de Toast rodando, pode chamar para avisar o usuário:
    if(typeof showToast === "function") {
        showToast(`${nomeExercicio} adicionado!`);
    }
}