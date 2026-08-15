from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.api.dependencies import pegar_sessao
from app.schemas.schemas import UsuarioSchema, LoginSchema
from app.controllers import auth_controller

auth = APIRouter(prefix="/auth", tags=["auth"])

@auth.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, session: Session = Depends(pegar_sessao)):
    return auth_controller.store(usuario_schema, session)


@auth.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(pegar_sessao)):
    return auth_controller.fazer_login(login_schema, session)


@auth.post("/login-form")
async def login_form(dados_formulario: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):
    return auth_controller.fazer_login_form(dados_formulario.username, dados_formulario.password, session)