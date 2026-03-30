from fastapi import FastAPI
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACESS_TOKEN_EXPIRE_MINUTES = str(os.getenv("ACESS_TOKEN_EXPIRE_MINUTES"))

app = FastAPI()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")

from routes.auth_routes import auth_routes
from routes.treinos_routes import treinos_routes

app.include_router(auth_routes)
app.include_router(treinos_routes)


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