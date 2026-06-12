from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.auth_routes       import auth
from app.api.routes.alunos_routes     import alunos
from app.api.routes.treinos_routes    import treinos
from app.api.routes.exercicios_routes import exercicios
from app.api.routes.progresso_routes  import progresso
from app.api.routes.objetivo_routes   import objetivos
import os

ACESS_TOKEN_EXPIRE_MINUTES = str(os.getenv("ACESS_TOKEN_EXPIRE_MINUTES"))

app = FastAPI()

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

# para rodar o nosso codigo, executrar no terminal: uvicorn main:app --reload