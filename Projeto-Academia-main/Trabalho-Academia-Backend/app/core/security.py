from dotenv import load_dotenv
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM  = os.getenv("ALGORITHM")
ACESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACESS_TOKEN_EXPIRE_MINUTES", "1440"))

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_schema  = OAuth2PasswordBearer(tokenUrl="/auth/login-form")
# Usado pelo chatbot: o token é opcional (permite conversar sem login).
oauth2_schema_opcional = OAuth2PasswordBearer(tokenUrl="/auth/login-form", auto_error=False)