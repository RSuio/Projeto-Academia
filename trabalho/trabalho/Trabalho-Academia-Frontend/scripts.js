const URL_BACKEND = "http://127.0.0.1:8000";


const loginForm = document.getElementById('loginForm');
const cadastroForm = document.getElementById('cadastroForm');
const irParaCadastro = document.getElementById('irParaCadastro');
const irParaLogin = document.getElementById('irParaLogin');

irParaCadastro.addEventListener('click', () => {
    loginForm.classList.add('hidden');
    cadastroForm.classList.remove('hidden');
});

irParaLogin.addEventListener('click', () => {
    cadastroForm.classList.add('hidden');
    loginForm.classList.remove('hidden');
});


document.getElementById('formCadastro').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const nome = document.getElementById('nome').value;
    const email = document.getElementById('emailCadastro').value;
    const senha = document.getElementById('senhaCadastro').value;

    try {
        const response = await fetch(`${URL_BACKEND}/auth/criar_conta`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nome, email, senha })
        });

        const data = await response.json();

        if (response.ok) {
            alert("Conta criada com sucesso! Faça seu login.");
            irParaLogin.click(); 
        } else {
            alert(`Erro: ${data.detail || "Não foi possível cadastrar."}`);
        }
    } catch (error) {
        alert("Erro ao conectar com o servidor.");
    }
});


document.getElementById('formLogin').addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('emailLogin').value;
    const senha = document.getElementById('senhaLogin').value;

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
            alert("Login realizado com sucesso!");

            if (data.is_admin === true) {
                window.location.href = "admin.html";
            } else {
                window.location.href = "dashboard.html";
            }
        } else {
            alert(`Erro: ${data.detail || "E-mail ou senha inválidos."}`);
        }

    } catch (error) {
        console.error("Erro na requisição:", error);
        alert("Erro ao conectar com o servidor.");
    }
});