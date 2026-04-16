// ═══════════════════════════════════════════════════════════════
// create-workout.js — Aba "Criar Treino" (aba 2)
// ═══════════════════════════════════════════════════════════════

// --- Carrega as categorias no <select> (só uma vez) ---
async function carregarCategoriasNoSelect() {
    const select = document.getElementById('new-treino-categoria');
    if (!select) return;

    // Já carregou antes: não refaz a requisição
    if (select.options.length > 1) return;

    try {
        const response = await fetch(`${URL_BACKEND}/exercicios/catalogo/categorias`);
        const categorias = await response.json();

        select.innerHTML = '<option value="" disabled selected>Selecione o Grupo Muscular...</option>';

        categorias.forEach(cat => {
            const opt = document.createElement('option');
            opt.value       = cat;
            opt.textContent = cat;
            select.appendChild(opt);
        });
    } catch (error) {
        console.error("Erro ao carregar categorias:", error);
        select.innerHTML = '<option value="" disabled selected>Erro ao carregar categorias</option>';
    }
}

// --- Busca exercícios da categoria selecionada e renderiza os cards ---
async function carregarExerciciosPorCategoria(categoria) {
    const containerCards = document.getElementById('cards-exercicios-container');
    const gridCards      = document.getElementById('grid-cards');
    const inputBusca     = document.getElementById('input-busca-exercicio');

    if (inputBusca) inputBusca.value = '';

    if (!categoria) {
        containerCards.classList.add('hidden');
        return;
    }

    containerCards.classList.remove('hidden');
    gridCards.innerHTML = `
        <p class="text-zinc-500 col-span-full text-center py-4">
            <i class="fa-solid fa-spinner fa-spin"></i> Buscando exercícios...
        </p>`;

    try {
        const response = await fetch(`${URL_BACKEND}/exercicios/catalogo?categoria=${encodeURIComponent(categoria)}&limit=50`);
        if (!response.ok) throw new Error('Erro ao buscar exercícios');

        const exercicios = await response.json();
        gridCards.innerHTML = '';

        if (exercicios.length === 0) {
            gridCards.innerHTML = '<p class="text-zinc-500 col-span-full text-center py-4">Nenhum exercício encontrado nesta categoria.</p>';
            return;
        }

        exercicios.forEach(ex => {
            const card = document.createElement('div');
            card.className = "bg-zinc-800 border border-zinc-700 hover:border-emerald-500 rounded-xl p-3 cursor-pointer transition-all text-center flex flex-col items-center gap-2 group hover:-translate-y-1";

            card.onclick = () => adicionarExercicioAoTreino(ex.id, ex.nome);

            card.innerHTML = `
                <div class="w-10 h-10 bg-zinc-900 rounded-full flex items-center justify-center text-zinc-400 group-hover:text-emerald-500 group-hover:bg-emerald-500/10 transition-colors">
                    <i class="fa-solid fa-dumbbell"></i>
                </div>
                <span class="text-xs font-medium text-zinc-300 group-hover:text-white leading-tight">${ex.nome}</span>
                <span class="text-[10px] text-zinc-500 w-full line-clamp-1" title="${ex.equipamento || 'Livre'}">${ex.equipamento || 'Livre'}</span>
            `;

            gridCards.appendChild(card);
        });

    } catch (error) {
        console.error(error);
        gridCards.innerHTML = '<p class="text-red-500 col-span-full text-center py-4">Erro de conexão com o servidor.</p>';
    }
}

// --- Filtra visualmente os cards já renderizados ---
function filtrarExercicios() {
    const inputBusca = document.getElementById('input-busca-exercicio');
    if (!inputBusca) return;

    const termo    = inputBusca.value.toLowerCase();
    const gridCards = document.getElementById('grid-cards');

    Array.from(gridCards.children).forEach(card => {
        if (card.tagName.toLowerCase() !== 'div') return;

        const spanNome = card.querySelector('span.text-xs');
        if (!spanNome) return;

        const nome = spanNome.textContent.toLowerCase();
        card.style.display = nome.includes(termo) ? '' : 'none';
    });
}

// --- Adiciona exercício clicado à lista de selecionados ---
function adicionarExercicioAoTreino(id, nomeExercicio) {
    const container = document.getElementById('exercicios-container');

    const linha = document.createElement('div');
    linha.className = "exercicio-row flex items-center gap-2 sm:gap-3 bg-zinc-800/50 p-2 sm:p-3 rounded-xl border border-zinc-700/50";

    linha.innerHTML = `
        <input type="hidden" class="ex-catalogo-id" value="${id}">
        <div class="flex-1 min-w-[120px]">
            <input type="text" value="${nomeExercicio}" readonly
                   class="w-full bg-transparent border-none text-emerald-400 font-medium focus:outline-none cursor-default text-sm sm:text-base truncate">
        </div>
        <input type="number" placeholder="Sér." min="1" required
               class="ex-series w-14 sm:w-16 bg-zinc-900 border border-zinc-700 rounded-lg px-1 sm:px-2 py-2 text-center text-sm focus:outline-none focus:border-emerald-400 text-white">
        <input type="number" placeholder="Rep." min="1" required
               class="ex-reps w-14 sm:w-16 bg-zinc-900 border border-zinc-700 rounded-lg px-1 sm:px-2 py-2 text-center text-sm focus:outline-none focus:border-emerald-400 text-white">
        <input type="text" placeholder="Kg"
               class="ex-carga w-14 sm:w-16 bg-zinc-900 border border-zinc-700 rounded-lg px-1 sm:px-2 py-2 text-center text-sm focus:outline-none focus:border-emerald-400 text-white">
        <button type="button" onclick="this.parentElement.remove()"
                class="text-zinc-500 hover:text-red-500 px-2 transition-colors">
            <i class="fa-solid fa-trash"></i>
        </button>
    `;

    container.appendChild(linha);
    showToast(`${nomeExercicio} adicionado!`);
}

// --- Envia o treino completo para o backend ---
async function createNewTreino() {
    const idAluno   = document.getElementById('new-treino-id-aluno')?.value.trim();
    const nomeTreino = document.getElementById('new-treino-name')?.value.trim();
    const objetivo  = document.getElementById('new-treino-objetivo')?.value.trim();
    const token     = localStorage.getItem('token_academia');

    if (!token)               return showToast("Você precisa estar logado!", true);
    if (!idAluno || !nomeTreino) return showToast("Preencha o ID do aluno e o Nome do treino!", true);

    const listaExercicios = [];
    document.querySelectorAll('.exercicio-row').forEach((row, index) => {
        const catalogoId = row.querySelector('.ex-catalogo-id')?.value;
        const series     = parseInt(row.querySelector('.ex-series')?.value) || 0;
        const reps       = parseInt(row.querySelector('.ex-reps')?.value) || 0;
        const cargaVal   = row.querySelector('.ex-carga')?.value.trim();

        if (catalogoId && series > 0 && reps > 0) {
            listaExercicios.push({
                exercicio_catalogo_id: parseInt(catalogoId),
                series,
                repeticoes: reps,
                carga: cargaVal !== "" ? parseFloat(cargaVal) : null,
                ordem: index + 1
            });
        }
    });

    if (listaExercicios.length === 0)
        return showToast("Adicione ao menos um exercício e preencha Séries/Reps!", true);

    const payload = {
        usuario_id: parseInt(idAluno),
        nome: nomeTreino,
        objetivo: objetivo || null,
        exercicios: listaExercicios
    };

    const btnSalvar   = document.querySelector('button[onclick="createNewTreino()"]');
    const textoOriginal = btnSalvar.innerHTML;
    btnSalvar.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Salvando...';
    btnSalvar.disabled  = true;

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

            // Limpa o formulário
            document.getElementById('new-treino-id-aluno').value  = '';
            document.getElementById('new-treino-name').value      = '';
            document.getElementById('new-treino-objetivo').value  = '';
            document.getElementById('exercicios-container').innerHTML = '';
            document.getElementById('new-treino-categoria').selectedIndex = 0;
            document.getElementById('cards-exercicios-container').classList.add('hidden');

            setTimeout(() => switchTab(0), 1500);
        } else {
            showToast(`Erro: ${data.detail || "Erro ao salvar treino."}`, true);
        }
    } catch {
        showToast("Erro de conexão com o servidor.", true);
    } finally {
        btnSalvar.innerHTML = textoOriginal;
        btnSalvar.disabled  = false;
    }
}