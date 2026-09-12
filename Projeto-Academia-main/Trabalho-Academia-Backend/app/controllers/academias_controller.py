from sqlalchemy.orm import Session
from app.database.models import Academia
from app.schemas.schemas import AcademiaCreate


def index(session: Session):
    return session.query(Academia).order_by(Academia.nome).all()


def store(dados: AcademiaCreate, session: Session):
    nova_academia = Academia(
        nome=dados.nome,
        endereco=dados.endereco,
        cidade=dados.cidade,
        telefone=dados.telefone
    )
    session.add(nova_academia)
    session.commit()
    return {"mensagem": f"Academia '{nova_academia.nome}' cadastrada com sucesso!"}