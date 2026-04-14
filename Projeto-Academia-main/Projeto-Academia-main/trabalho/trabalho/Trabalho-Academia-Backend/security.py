
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer


SECRET_KEY = "LaS1cSaz7S6lZJ1khvZHd38X2KpEJtI7Lil2g9aEFkh"
ALGORITHM = "HS256"


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login")