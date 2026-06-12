# 🏋️ ForgeFit — Sistema de Gestão de Academia Digital

Sistema web desenvolvido para academias com o objetivo de digitalizar o acompanhamento de treinos e melhorar a comunicação entre alunos e personal trainers.

A plataforma permite que alunos acessem seus treinos de forma prática, enquanto os personal trainers gerenciam, criam e atualizam treinos de forma rápida e centralizada.

---

## 🚀 Tecnologias Utilizadas

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.11 + FastAPI |
| Frontend | HTML, Tailwind CSS, JavaScript |
| Banco de Dados | SQLite + SQLAlchemy |
| Autenticação | JWT (JSON Web Token) + bcrypt |
| Versionamento | Git / GitHub |

---

## ⚙️ Funcionalidades

✅ Cadastro e autenticação de usuários (alunos e personal trainers)  
✅ Criação e gerenciamento de treinos personalizados  
✅ Catálogo de exercícios integrado (sem digitação manual)  
✅ Visualização de treinos pelos alunos  
✅ Controle de acesso por perfil (admin / aluno) via JWT  
✅ Integração completa entre frontend e backend via API REST  

---

## 📡 Arquitetura do Sistema

O sistema segue o modelo **cliente-servidor** com separação em camadas:

```
Frontend (HTML + JS)
       ↓ requisições HTTP
Backend (FastAPI)
  ├── routes/        → define as URLs e delega
  ├── controllers/   → lógica de negócio
  ├── models.py      → tabelas do banco
  └── schemas.py     → validação dos dados
       ↓
Banco de Dados (SQLite)
```

---

## 🔑 Como rodar o projeto

**1. Clone o repositório**
```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

**2. Crie e ative o ambiente virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

**4. Configure o arquivo `.env`**

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:
```env
SECRET_KEY=sua_chave_secreta_aqui
ALGORITHM=HS256
DATABASE_URL=sqlite:///app/database/banco.db    
```

> 💡 Gere uma chave segura em: https://jwtsecretkeygenerator.com/

**5. Popular o banco com exercícios**
```bash
python popular_portugues.py
```

**6. Inicie o servidor**
```bash
uvicorn main:app --reload
```

---

## 🌐 Acessando a aplicação

| O que | URL |
|---|---|
| Frontend | Abra o arquivo `index.html` no navegador |
| API | http://127.0.0.1:8000 |
| Documentação Swagger | http://127.0.0.1:8000/docs |

---

## 🧪 Testes

```bash
pip install pytest
pytest tests/test_cadastro.py -v
```

---

## 👥 Perfis de Usuário

| Perfil | Pode fazer |
|---|---|
| **Personal Trainer** | Criar treinos, gerenciar alunos, excluir treinos |
| **Aluno** | Visualizar treinos atribuídos pelo personal |

---

## 📷 Demonstração


