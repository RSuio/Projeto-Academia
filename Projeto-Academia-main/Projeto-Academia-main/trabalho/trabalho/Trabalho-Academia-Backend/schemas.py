from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


# ─────────────────────────────────────────────
# USUÁRIO
# ─────────────────────────────────────────────
class UsuarioSchema(BaseModel):
    nome: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    senha: str
    ativo: bool = True
    admin: bool = False

    class Config:
        from_attributes = True


class LoginSchema(BaseModel):
    email: str
    senha: str

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# CATÁLOGO DE EXERCÍCIOS (somente leitura — vem da API)
# ─────────────────────────────────────────────
class ExercicioCatalogoRead(BaseModel):
    """
    Usado para listar os exercícios disponíveis no catálogo.
    O personal consulta esses dados antes de montar um treino.
    """
    id: int
    api_id: int
    nome: str
    nome_en: Optional[str] = None
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    equipamento: Optional[str] = None
    musculo_principal: Optional[str] = None
    musculo_secundario: Optional[str] = None

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# TREINO EXERCÍCIO (parâmetros definidos pelo personal)
# ─────────────────────────────────────────────
class TreinoExercicioCreate(BaseModel):
    """
    O personal informa apenas o ID do exercício do catálogo
    + os parâmetros de execução. Nada de digitar nome.
    """
    exercicio_catalogo_id: int
    series: int = Field(..., ge=1)
    repeticoes: int = Field(..., ge=1)
    carga: Optional[float] = Field(None, description="Em kg. Deixe vazio para exercícios com peso corporal.")
    ordem: Optional[int] = None
    observacao: Optional[str] = None


class TreinoExercicioRead(BaseModel):
    id: int
    exercicio_catalogo_id: int
    nome_exercicio: Optional[str] = None    # populado via join no endpoint
    series: int
    repeticoes: int
    carga: Optional[float] = None
    ordem: Optional[int] = None
    observacao: Optional[str] = None

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# TREINO
# ─────────────────────────────────────────────
class TreinoCreate(BaseModel):
    nome: str
    objetivo: str
    usuario_id: int
    exercicios: List[TreinoExercicioCreate]

    model_config = {
        "json_schema_extra": {
            "example": {
                "nome": "Treino A - Superior",
                "objetivo": "Hipertrofia",
                "usuario_id": 1,
                "exercicios": [
                    {"exercicio_catalogo_id": 12, "series": 4, "repeticoes": 10, "carga": 60.0, "ordem": 1},
                    {"exercicio_catalogo_id": 34, "series": 3, "repeticoes": 12, "carga": 20.0, "ordem": 2},
                    {"exercicio_catalogo_id": 87, "series": 4, "repeticoes": 15, "ordem": 3}
                ]
            }
        }
    }


class TreinoRead(BaseModel):
    id: int
    nome: str
    objetivo: str
    exercicios: List[TreinoExercicioRead]

    class Config:
        from_attributes = True