from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from typing import List, Optional

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

class ExercicioCreate(BaseModel):
    nome: str
    series: int
    repeticoes: int
    carga: Optional[int] = None


class TreinoCreate(BaseModel):
    nome: str
    objetivo: str
    usuario_id: int
    exercicios: List[ExercicioCreate]

    model_config = {
        "json_schema_extra": {
            "example": {
                "nome": "Treino A - Superior",
                "objetivo": "Hipertrofia",
                "usuario_id": 1,
                "exercicios": [
                    {"nome": "Supino Reto", "series": 4, "repeticoes": 10, "carga": 20},
                    {"nome": "Crucifixo", "series": 3, "repeticoes": 12, "carga": 10},
                    {"nome": "Tríceps Corda", "series": 4, "repeticoes": 15, "carga": 5}
                ]
            }
        }
    }

class ExercicioRead(BaseModel):
    id: int
    nome: str
    series: int
    repeticoes: int
    carga: float | None = None

    class Config:
        from_attributes = True

class TreinoRead(BaseModel):
    id: int
    nome: str
    objetivo: str
    exercicios: List[ExercicioRead]

    class Config:
        from_attributes = True