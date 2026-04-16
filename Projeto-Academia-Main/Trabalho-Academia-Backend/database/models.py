from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

db = create_engine("sqlite:///database/banco.db")
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
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    exercicios = relationship("TreinoExercicio", backref="treino", cascade="all, delete-orphan")

    def __init__(self, nome, objetivo, usuario_id):
        self.nome = nome
        self.objetivo = objetivo
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


Base.metadata.create_all(bind=db)