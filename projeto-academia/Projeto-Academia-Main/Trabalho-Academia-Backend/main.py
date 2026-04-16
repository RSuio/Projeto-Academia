from fastapi import FastAPI
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
from routes.routes_exercicios import router as exercicios_router

load_dotenv()

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

from routes.auth_routes import auth_routes
from routes.treinos_routes import treinos_routes

app.include_router(auth_routes)
app.include_router(treinos_routes)
app.include_router(exercicios_router)


# para rodar o nosso codigo, executrar no terminal: uvicorn main:app --reload

# endpoint:
# dominio.com/pedidos

# Rest API
# Get -> leitura/pegar
# Post -> enviar/criar
# Put/Patch -> edição
# Delete -> deletar

#if __name__ == '__main__':
 #   import uvicorn

#    uvicorn.run("main:app", host="0.0.0.0", port=8000,
 #               log_level="debug", reload=True)