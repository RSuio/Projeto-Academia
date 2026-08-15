"""
Controller do catálogo de exercícios.
Usa o padrão Strategy (patterns/strategy_filtros.py) para aplicar
os filtros de busca de forma desacoplada.
"""

from sqlalchemy.orm import Session
from app.database.models import ExercicioCatalogo
from app.patterns.strategy_filtros import construir_filtros
from fastapi import HTTPException, status


def listar_catalogo(
    session: Session,
    busca: str = "",
    categoria: str = "",
    equipamento: str = "",
    limit: int = 10,
    offset: int = 0
):
    query = session.query(ExercicioCatalogo)
    context = construir_filtros(busca, categoria, equipamento)
    query   = context.executar(query)

    return query.order_by(ExercicioCatalogo.nome).offset(offset).limit(limit).all()


def listar_categorias(session: Session):
    rows = (
        session.query(ExercicioCatalogo.categoria)
        .filter(ExercicioCatalogo.categoria.isnot(None))
        .distinct()
        .order_by(ExercicioCatalogo.categoria)
        .all()
    )
    return [r[0] for r in rows]



def criar_exercicio(session: Session, dados_exercicio):
    novo_exercicio = ExercicioCatalogo(
        nome=dados_exercicio.nome,
        categoria=dados_exercicio.categoria,
        equipamento=dados_exercicio.equipamento,
        api_id=dados_exercicio.api_id
    )
    session.add(novo_exercicio)
    session.commit()
    session.refresh(novo_exercicio)
    return novo_exercicio

def buscar_exercicio_por_id(session: Session, exercicio_id: int):
    exercicio = session.query(ExercicioCatalogo).filter(ExercicioCatalogo.id == exercicio_id).first()
    if not exercicio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercício não encontrado.")
    return exercicio

def atualizar_exercicio(session: Session, exercicio_id: int, dados_exercicio):
    exercicio = buscar_exercicio_por_id(session, exercicio_id)
    
    exercicio.nome = dados_exercicio.nome
    exercicio.categoria = dados_exercicio.categoria
    exercicio.equipamento = dados_exercicio.equipamento
    
    session.commit()
    session.refresh(exercicio)
    return exercicio

def deletar_exercicio(session: Session, exercicio_id: int):
    exercicio = buscar_exercicio_por_id(session, exercicio_id)
    session.delete(exercicio)
    session.commit()
    return {"mensagem": f"Exercício '{exercicio.nome}' deletado com sucesso."}

def atualizar_exercicio_parcial(session: Session, exercicio_id: int, dados_parciais: dict):
    exercicio = buscar_exercicio_por_id(session, exercicio_id)
    for chave, valor in dados_parciais.items():
        if valor is not None and hasattr(exercicio, chave):
            setattr(exercicio, chave, valor)
            
    session.commit()
    session.refresh(exercicio)
    return exercicio
