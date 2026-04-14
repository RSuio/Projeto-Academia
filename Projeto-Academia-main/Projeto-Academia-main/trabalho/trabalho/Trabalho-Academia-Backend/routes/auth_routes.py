from fastapi import APIRouter, Depends, HTTPException, status
from database.models import Usuario
from routes.dependeces import pegar_sessao, verificar_token
from schemas import UsuarioSchema, LoginSchema
from sqlalchemy.orm import Session
from security import bcrypt_context, ALGORITHM, SECRET_KEY
from jose import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm

auth_routes = APIRouter(prefix="/auth", tags=["auth"])

def criar_token(id_usuario: int):
    # coloquei agora o token com 24 horas de duração.
    tempo_expiracao = datetime.now(timezone.utc) + timedelta(hours=24)
    
    payload = {
        "sub": str(id_usuario),
        "exp": tempo_expiracao
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def autenticar_usuario(email, senha, session):
    usuario = session.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return False
    elif not bcrypt_context.verify(senha, usuario.senha):
        return False
    return usuario

@auth_routes.get("/")
async def home():
    return {"mensagem": "voce acessou a rota padrão de autenticação.", "autenticado":False}

@auth_routes.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, session: Session = Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()
    if usuario:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail="E-mail do usuário já cadastrado")
    else:
        senha_criptografada = bcrypt_context.hash(usuario_schema.senha)
        novo_usuario = Usuario(nome = usuario_schema.nome, email = usuario_schema.email, senha = senha_criptografada, admin = usuario_schema.admin, ativo = usuario_schema.ativo)
        session.add(novo_usuario)
        session.commit()
        return {"mensagem":f"Usuário cadastrado com sucesso {usuario_schema.email}."}
    
# login -> email e senha -> token JWT (Json Web Toekn) hiudsahiushd12y3812dagsdyugasdy

@auth_routes.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(pegar_sessao)):
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
    if not usuario:
        raise HTTPException(status_code = 401, detail="Esse usuario não existe ou credenciais invalidas.")
    # apenas um token com validade de 24h
    access_token = criar_token(usuario.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 86400,
        "is_admin": usuario.admin,
    }

@auth_routes.post("/login-form")
async def login_form(dados_formulario: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):
    usuario = autenticar_usuario(dados_formulario.username, dados_formulario.password, session)
    if not usuario:
        raise HTTPException(status_code = 401, detail="Esse usuario não existe ou credenciais invalidas.")
    # apenas um token com validade de 24h
    access_token = criar_token(usuario.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "is_admin": usuario.admin,
    }

@auth_routes.get("/alunos")
async def listar_alunos(
    usuario_logado = Depends(verificar_token),
    session: Session = Depends(pegar_sessao)
):
    if not usuario_logado or not getattr(usuario_logado, "admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso negado. Apenas personais podem ver a lista de alunos."
        )
    
    alunos_db = session.query(Usuario).filter(Usuario.admin == False).all()
    
    lista_alunos = []
    for aluno in alunos_db:
        lista_alunos.append({
            "id": aluno.id,
            "nome": aluno.nome,
            "email": aluno.email
        })
        
    return lista_alunos
