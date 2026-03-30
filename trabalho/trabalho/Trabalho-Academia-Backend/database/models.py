from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy_utils.types import ChoiceType
from sqlalchemy.orm import relationship

# cria a conexã do seu banco de dados
db = create_engine("sqlite:///database/banco.db")

# cria a base do banco de dados
Base = declarative_base()

# cria as classes/tabelas do banco
# usuario
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String)
    email = Column("email", String, nullable=False)
    senha = Column("senha", String)
    ativo = Column("ativo", Boolean)
    admin = Column("admin", Boolean, default=False)
    
    def __init__(self, nome, email, senha, ativo=True, admin=False):
        self.nome = nome
        self.email = email
        self. senha = senha
        self.ativo = ativo
        self.admin = admin

# Tabela de Treinos (O "Título" do grupo de exercícios)
class Treino(Base):
    __tablename__ = "treinos"
    
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String) 
    objetivo = Column("objetivo", String) # Ex: Hipertrofia, Força, Emagrecimento
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    exercicios = relationship("Exercicio", backref="treino", cascade="all, delete-orphan")

    def __init__(self, nome, objetivo, usuario_id):
        self.nome = nome
        self.objetivo = objetivo
        self.usuario_id = usuario_id

class Exercicio(Base):
    __tablename__ = "exercicios"
    
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String)
    series = Column("series", Integer) 
    repeticoes = Column("repeticoes", Integer) 
    carga = Column("carga", Float) 
    treino_id = Column(Integer, ForeignKey("treinos.id"))

    def __init__(self, nome, series, repeticoes, carga, treino_id):
        self.nome = nome
        self.series = series
        self.repeticoes = repeticoes
        self.carga = carga
        self.treino_id = treino_id


#executa a criação do banco de dados


