from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
db = create_engine(f"sqlite:///{BASE_DIR}/banco.db")
Base = declarative_base()


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    senha = Column(String, nullable=False)
    ativo = Column(Boolean, default=True)
    admin = Column(Boolean, default=False)

    treinos = relationship("Treino", backref="usuario", cascade="all, delete-orphan")

    def __init__(self, nome, email, senha, ativo=True, admin=False):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.ativo = ativo
        self.admin = admin


class ExercicioCatalogo(Base):
    __tablename__ = "exercicios_catalogo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_id = Column(Integer, unique=True, nullable=False)   
    nome = Column(String, nullable=False)
    nome_en = Column(String, nullable=True)                
    descricao = Column(Text, nullable=True)
    categoria = Column(String, nullable=True)              
    equipamento = Column(String, nullable=True)           
    musculo_principal = Column(String, nullable=True)
    musculo_secundario = Column(String, nullable=True)

    usos = relationship("TreinoExercicio", backref="catalogo", cascade="all, delete-orphan")

    def __init__(self, api_id, nome, nome_en=None, descricao=None,
                 categoria=None, equipamento=None,
                 musculo_principal=None, musculo_secundario=None):
        self.api_id = api_id
        self.nome = nome
        self.nome_en = nome_en
        self.descricao = descricao
        self.categoria = categoria
        self.equipamento = equipamento
        self.musculo_principal = musculo_principal
        self.musculo_secundario = musculo_secundario


class Treino(Base):
    __tablename__ = "treinos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    objetivo = Column(String, nullable=True) 
    dia_semana = Column(String, nullable=True)  
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)


    exercicios = relationship("TreinoExercicio", backref="treino", cascade="all, delete-orphan")

    def __init__(self, nome, objetivo, usuario_id, dia_semana=None):
        self.nome = nome
        self.objetivo = objetivo
        self.dia_semana = dia_semana
        self.usuario_id = usuario_id


class TreinoExercicio(Base):
    __tablename__ = "treino_exercicios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    treino_id = Column(Integer, ForeignKey("treinos.id"), nullable=False)
    exercicio_catalogo_id = Column(Integer, ForeignKey("exercicios_catalogo.id"), nullable=False)
    series = Column(Integer, nullable=False)
    repeticoes = Column(Integer, nullable=False)
    carga = Column(Float, nullable=True)        
    ordem = Column(Integer, nullable=True)      
    observacao = Column(String, nullable=True) 

    def __init__(self, treino_id, exercicio_catalogo_id,
                 series, repeticoes, carga=None, ordem=None, observacao=None):
        self.treino_id = treino_id
        self.exercicio_catalogo_id = exercicio_catalogo_id
        self.series = series
        self.repeticoes = repeticoes
        self.carga = carga
        self.ordem = ordem
        self.observacao = observacao


class TreinoRealizado(Base):
    __tablename__ = "treinos_realizados"

    id = Column(Integer, primary_key=True, autoincrement=True)
    treino_id  = Column(Integer, ForeignKey("treinos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    data_realizacao = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    observacao = Column(String, nullable=True) 
    treino  = relationship("Treino", backref="realizacoes")
    usuario = relationship("Usuario", backref="treinos_realizados")

    def __init__(self, treino_id, usuario_id, observacao=None):
        self.treino_id      = treino_id
        self.usuario_id     = usuario_id
        self.observacao     = observacao


class ObjetivoAluno(Base):

    __tablename__ = "objetivos_aluno"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id   = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    meta_treinos = Column(Integer, nullable=False)      
    data_inicio  = Column(DateTime, nullable=False)     
    data_fim     = Column(DateTime, nullable=False)    
    descricao    = Column(String, nullable=True)        

    usuario = relationship("Usuario", backref="objetivos")

    def __init__(self, usuario_id, meta_treinos, data_inicio, data_fim, descricao=None):
        self.usuario_id   = usuario_id
        self.meta_treinos = meta_treinos
        self.data_inicio  = data_inicio
        self.data_fim     = data_fim
        self.descricao    = descricao


Base.metadata.create_all(bind=db)



'''
Alterar models.py -> gerar migração -> aplicar no banco

alembic revision --autogenerate -m "descricao do que mudou"

alembic upgrade head

# Ver histórico de migrações
alembic history

# Ver qual migração está aplicada agora
alembic current

# Voltar uma migração (desfaz a última)
alembic downgrade -1

# Voltar para o zero (apaga tudo)
alembic downgrade base

# Aplicar só a próxima migração
alembic upgrade +1
'''
