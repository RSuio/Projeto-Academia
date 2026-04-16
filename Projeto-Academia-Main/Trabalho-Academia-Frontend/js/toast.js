// ═══════════════════════════════════════════════════════════════
// toast.js — Utilitário de avisos visuais
// ═══════════════════════════════════════════════════════════════

function showToast(message, error = false) {
    const toast = document.getElementById('toast');
    const text  = document.getElementById('toast-text');

    text.textContent = message;
    toast.style.backgroundColor = error ? '#ef4444' : '#10b981';
    toast.style.color            = error ? '#ffffff' : '#000000';

    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), 3500);
}