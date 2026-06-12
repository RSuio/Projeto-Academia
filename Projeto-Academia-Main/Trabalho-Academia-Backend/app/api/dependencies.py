from app.database.models import db, Usuario
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from app.core.security import oauth2_schema, SECRET_KEY, ALGORITHM

def pegar_sessao():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close()

def verificar_token(token: str = Depends(oauth2_schema), session: Session = Depends(pegar_sessao)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario: str = payload.get("sub")
        if id_usuario is None:
            raise HTTPException(status_code=401, detail="Token inválido.")
        usuario = session.query(Usuario).filter(Usuario.id == int(id_usuario)).first()
        if usuario is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado.")
        return usuario
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão expirada. Por favor, faça login novamente.")


def verificar_admin(usuario_atual = Depends(verificar_token)):
    if not usuario_atual.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: Apenas administradores podem realizar esta ação."
        )
    return usuario_atual