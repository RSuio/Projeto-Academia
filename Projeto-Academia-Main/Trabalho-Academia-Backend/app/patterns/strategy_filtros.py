"""
Padrão de Projeto: STRATEGY
─────────────────────────────────────────────────────────────────
Problema original: o controller de exercícios tinha vários `if`
encadeados para cada tipo de filtro (nome, categoria, equipamento).
Isso tornava o código difícil de estender — cada novo filtro exigia
mexer no meio do controller.

Solução com Strategy: cada tipo de filtro vira uma classe separada
com o mesmo método `aplicar(query)`. O controller só recebe uma lista
de estratégias e as aplica em sequência, sem saber os detalhes de
nenhuma delas.

Para adicionar um novo filtro no futuro (ex: por músculo), basta
criar uma nova classe — sem tocar no controller ou nas existentes.
─────────────────────────────────────────────────────────────────
"""

from abc import ABC, abstractmethod
from sqlalchemy.orm import Query
from app.database.models import ExercicioCatalogo

class FiltroExercicioStrategy(ABC):
    @abstractmethod
    def aplicar(self, query: Query) -> Query:
        pass

class FiltroPorNome(FiltroExercicioStrategy):
    def __init__(self, termo: str):
        self.termo = termo

    def aplicar(self, query: Query) -> Query:
        return query.filter(ExercicioCatalogo.nome.ilike(f"%{self.termo}%"))


class FiltroPorCategoria(FiltroExercicioStrategy):
    def __init__(self, categoria: str):
        self.categoria = categoria

    def aplicar(self, query: Query) -> Query:
        return query.filter(ExercicioCatalogo.categoria.ilike(f"%{self.categoria}%"))


class FiltroPorEquipamento(FiltroExercicioStrategy):
    def __init__(self, equipamento: str):
        self.equipamento = equipamento

    def aplicar(self, query: Query) -> Query:
        return query.filter(ExercicioCatalogo.equipamento.ilike(f"%{self.equipamento}%"))


class FiltroPorMusculo(FiltroExercicioStrategy):
    def __init__(self, musculo: str):
        self.musculo = musculo

    def aplicar(self, query: Query) -> Query:
        return query.filter(ExercicioCatalogo.musculo_principal.ilike(f"%{self.musculo}%"))


class FiltroExercicioContext:
    def __init__(self, estrategias: list[FiltroExercicioStrategy]):
        self.estrategias = estrategias

    def executar(self, query: Query) -> Query:
        for estrategia in self.estrategias:
            query = estrategia.aplicar(query)
        return query


def construir_filtros(busca: str, categoria: str, equipamento: str) -> FiltroExercicioContext:
    estrategias = []

    if busca:
        estrategias.append(FiltroPorNome(busca))
    if categoria:
        estrategias.append(FiltroPorCategoria(categoria))
    if equipamento:
        estrategias.append(FiltroPorEquipamento(equipamento))

    return FiltroExercicioContext(estrategias)