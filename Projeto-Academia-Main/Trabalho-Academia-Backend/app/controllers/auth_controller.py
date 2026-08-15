from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.database.models import Usuario
from app.schemas.schemas import UsuarioSchema, LoginSchema
from app.core.security import bcrypt_context, ALGORITHM, SECRET_KEY
from jose import jwt

def criar_token(id_usuario: int) -> str:
    tempo_expiracao = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {
        "sub": str(id_usuario),
        "exp": tempo_expiracao
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def autenticar_usuario(email: str, senha: str, session: Session):
    usuario = session.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return False
    if not bcrypt_context.verify(senha, usuario.senha):
        return False
    return usuario


def store(usuario_schema: UsuarioSchema, session: Session):
    usuario_existente = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail do usuário já cadastrado."
        )

    senha_criptografada = bcrypt_context.hash(usuario_schema.senha)
    novo_usuario = Usuario(
        nome=usuario_schema.nome,
        email=usuario_schema.email,
        senha=senha_criptografada,
        admin=usuario_schema.admin,
        ativo=usuario_schema.ativo
    )
    session.add(novo_usuario)
    session.commit()
    return {"mensagem": f"Usuário cadastrado com sucesso: {usuario_schema.email}."}


def fazer_login(login_schema: LoginSchema, session: Session):
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não existe ou credenciais inválidas."
        )
    access_token = criar_token(usuario.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 86400,
        "is_admin": usuario.admin,
    }


def fazer_login_form(username: str, password: str, session: Session):
    usuario = autenticar_usuario(username, password, session)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não existe ou credenciais inválidas."
        )
    access_token = criar_token(usuario.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "is_admin": usuario.admin,
    }


def index(usuario_logado: Usuario, session: Session):
    if not getattr(usuario_logado, "admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas personais podem ver a lista de alunos."
        )

    alunos = session.query(Usuario).filter(Usuario.admin == False).all()
    return [{"id": a.id, "nome": a.nome, "email": a.email} for a in alunos]