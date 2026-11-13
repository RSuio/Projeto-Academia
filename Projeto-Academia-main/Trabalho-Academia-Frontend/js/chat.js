// ═══════════════════════════════════════════════════════════════
// chat.js — Chatbot flutuante (regras + IA opcional no backend)
// ═══════════════════════════════════════════════════════════════

let chatAberto = false;
let chatEnviando = false;
let chatHistorico = [];   // [{ papel: "user" | "assistant", conteudo: "..." }]

const CHAT_BOAS_VINDAS =
    "Olá! 👋 Sou o assistente do ForgeFit.\n" +
    "Posso ajudar com seus treinos, progresso, objetivo e personal.\n" +
    "O que você quer saber?";

// ── Abrir / fechar o painel ──────────────────────────────────
function toggleChat() {
    chatAberto = !chatAberto;
    const painel = document.getElementById('chat-panel');
    if (!painel) return;

    painel.classList.toggle('hidden', !chatAberto);

    const icone = document.querySelector('#chat-toggle i');
    if (icone) {
        icone.className = chatAberto
            ? 'fa-solid fa-xmark text-xl'
            : 'fa-solid fa-comments text-xl';
    }

    if (chatAberto) {
        if (chatHistorico.length === 0) {
            adicionarMensagemChat('bot', CHAT_BOAS_VINDAS);
        }
        setTimeout(() => document.getElementById('chat-input')?.focus(), 50);
    }
}

// ── Adiciona uma bolha no histórico visual ───────────────────
function adicionarMensagemChat(autor, texto) {
    const container = document.getElementById('chat-messages');
    if (!container) return null;

    const isBot = autor === 'bot';

    const linha = document.createElement('div');
    linha.className = `flex ${isBot ? 'justify-start' : 'justify-end'}`;

    const bolha = document.createElement('div');
    bolha.className = isBot
        ? 'max-w-[85%] px-4 py-2.5 rounded-2xl rounded-bl-md bg-white dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 text-sm whitespace-pre-line break-words'
        : 'max-w-[85%] px-4 py-2.5 rounded-2xl rounded-br-md bg-emerald-600 text-white text-sm whitespace-pre-line break-words';
    bolha.textContent = texto;

    linha.appendChild(bolha);
    container.appendChild(linha);
    container.scrollTop = container.scrollHeight;
    return bolha;
}

// ── Envia a mensagem para o backend ──────────────────────────
async function enviarMensagemChat(event) {
    if (event) event.preventDefault();
    if (chatEnviando) return;

    const input = document.getElementById('chat-input');
    const mensagem = (input?.value || '').trim();
    if (!mensagem) return;

    input.value = '';
    adicionarMensagemChat('user', mensagem);
    chatHistorico.push({ papel: 'user', conteudo: mensagem });

    chatEnviando = true;
    const pensando = adicionarMensagemChat('bot', 'Pensando...');
    if (pensando) pensando.classList.add('animate-pulse', 'text-slate-400', 'dark:text-zinc-500');

    try {
        const token = localStorage.getItem('token_academia');
        const headers = { 'Content-Type': 'application/json' };
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const response = await fetch(`${URL_BACKEND}/chat/`, {
            method: 'POST',
            headers,
            body: JSON.stringify({
                mensagem,
                // Envia o histórico anterior (sem a mensagem atual)
                historico: chatHistorico.slice(-10, -1)
            })
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        pensando?.remove();

        const resposta = (data.resposta || '').trim() || 'Não consegui gerar uma resposta agora.';
        adicionarMensagemChat('bot', resposta);
        chatHistorico.push({ papel: 'assistant', conteudo: resposta.slice(0, 2000) });

        // Mantém o histórico curto para não crescer indefinidamente
        if (chatHistorico.length > 20) {
            chatHistorico = chatHistorico.slice(-20);
        }
    } catch {
        pensando?.remove();
        adicionarMensagemChat(
            'bot',
            'Não consegui falar com o servidor agora. Verifique se o backend está rodando e tente novamente.'
        );
    } finally {
        chatEnviando = false;
    }
}

// ── Fecha o chat com ESC ─────────────────────────────────────
document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && chatAberto) toggleChat();
});
