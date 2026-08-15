from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import sessionmaker
import os

from app.api.routes.auth_routes       import auth
from app.api.routes.alunos_routes     import alunos
from app.api.routes.treinos_routes    import treinos
from app.api.routes.exercicios_routes import router as exercicios
from app.api.routes.progresso_routes  import progresso
from app.api.routes.objetivo_routes   import objetivos
from app.database.models              import db, ExercicioCatalogo
from popular_portugues                import popular_catalogo

ACESS_TOKEN_EXPIRE_MINUTES = str(os.getenv("ACESS_TOKEN_EXPIRE_MINUTES"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-popula o catálogo de exercícios se estiver vazio ao iniciar o aplicativo
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        qtd = session.query(ExercicioCatalogo).count()
        if qtd == 0:
            print("🏋️ Banco de exercícios vazio. Populando catálogo em português automaticamente...")
            popular_catalogo(session)
        else:
            print(f"✅ Catálogo de exercícios pronto com {qtd} itens.")
        session.close()
    except Exception as e:
        print(f"⚠️ Aviso ao verificar catálogo no startup: {e}")
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5500", 
    "http://127.0.0.1:5500",
    "http://localhost:8000", 
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           
    allow_credentials=True,           
    allow_methods=["*"],             
    allow_headers=["*"],              
)

app.include_router(auth)
app.include_router(alunos)
app.include_router(treinos)
app.include_router(exercicios)
app.include_router(progresso)
app.include_router(objetivos)

# para rodar o nosso codigo, executrar no terminal: py -3.11 -m uvicorn main:app --reload