// ═══════════════════════════════════════════════════════════════
// toast.js — Utilitário de avisos visuais
// ═══════════════════════════════════════════════════════════════

let _toastTimeout = null;

function showToast(message, error = false) {
    const toast = document.getElementById('toast');
    const text  = document.getElementById('toast-text');
    if (!toast || !text) return;

    text.textContent = message;
    toast.style.backgroundColor = error ? '#ef4444' : '#10b981';
    toast.style.color            = error ? '#ffffff' : '#000000';
    toast.style.zIndex           = '99999';

    toast.classList.remove('hidden');

    if (_toastTimeout) clearTimeout(_toastTimeout);
    _toastTimeout = setTimeout(() => {
        toast.classList.add('hidden');
    }, 3500);
}