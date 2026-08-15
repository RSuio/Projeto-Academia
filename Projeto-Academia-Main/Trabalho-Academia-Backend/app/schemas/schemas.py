from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import List, Optional
from datetime import datetime


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


class ExercicioCatalogoRead(BaseModel):
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


class TreinoExercicioCreate(BaseModel):
    exercicio_catalogo_id: int
    series: int = Field(..., ge=1)
    repeticoes: int = Field(..., ge=1)
    carga: Optional[float] = Field(None, description="Em kg. Deixe vazio para exercícios com peso corporal.")
    ordem: Optional[int] = None
    observacao: Optional[str] = None


class TreinoExercicioRead(BaseModel):
    id: int
    exercicio_catalogo_id: int
    nome_exercicio: Optional[str] = None
    series: int
    repeticoes: int
    carga: Optional[float] = None
    ordem: Optional[int] = None
    observacao: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def preencher_nome(cls, data):
        if hasattr(data, "catalogo") and data.catalogo:
            return {
                "id":                     data.id,
                "exercicio_catalogo_id":  data.exercicio_catalogo_id,
                "nome_exercicio":         data.catalogo.nome,
                "series":                 data.series,
                "repeticoes":             data.repeticoes,
                "carga":                  data.carga,
                "ordem":                  data.ordem,
                "observacao":             getattr(data, "observacao", None),
            }
        return data

    class Config:
        from_attributes = True


DIAS_SEMANA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

class TreinoCreate(BaseModel):
    nome: str
    objetivo: str
    usuario_id: int
    dia_semana: Optional[str] = None
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
    dia_semana: Optional[str] = None
    exercicios: List[TreinoExercicioRead]

    class Config:
        from_attributes = True


class TreinoRealizadoCreate(BaseModel):
    treino_id: int
    observacao: Optional[str] = None


class TreinoRealizadoRead(BaseModel):
    id: int
    treino_id: int
    usuario_id: int
    data_realizacao: datetime
    observacao: Optional[str] = None

    class Config:
        from_attributes = True


class DashboardProgresso(BaseModel):

    total_realizados: int
    streak_atual: int        
    por_semana: List[int]       
    ultimo_treino: Optional[datetime] = None

class ObjetivoCreate(BaseModel):
    usuario_id:   int
    meta_treinos: int   = Field(..., ge=1, description="Número de treinos a completar")
    data_inicio:  datetime
    data_fim:     datetime
    descricao:    Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "usuario_id":   1,
                "meta_treinos": 24,
                "data_inicio":  "2025-01-01T00:00:00",
                "data_fim":     "2025-06-30T23:59:59",
                "descricao":    "Completar 24 treinos em 6 meses"
            }
        }
    }


class ObjetivoRead(BaseModel):
    id:           int
    usuario_id:   int
    meta_treinos: int
    data_inicio:  datetime
    data_fim:     datetime
    descricao:    Optional[str] = None

    class Config:
        from_attributes = True


class ObjetivoProgresso(BaseModel):

    objetivo:           ObjetivoRead
    treinos_realizados: int      
    percentual:         float        
    dias_restantes:     int
    concluido:          bool
