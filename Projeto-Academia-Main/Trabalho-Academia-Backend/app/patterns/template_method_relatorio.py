"""
Padrão de Projeto: TEMPLATE METHOD
─────────────────────────────────────────────────────────────────
Problema: gerar diferentes tipos de relatório de progresso
(por semana, por mês) tem sempre o mesmo esqueleto de passos:
  1. Buscar os registros do banco
  2. Processar / agrupar os dados
  3. Formatar o resultado final

A diferença entre os relatórios está apenas em como cada passo
é executado — o esqueleto é sempre o mesmo.

Solução com Template Method: a classe base define e chama os
passos na ordem certa (método `gerar`). As subclasses só
sobrescrevem os passos que diferem entre si.
─────────────────────────────────────────────────────────────────
"""

from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from app.database.models import TreinoRealizado
from datetime import datetime, timedelta, timezone
from collections import defaultdict
 

class RelatorioProgresso(ABC):

    def __init__(self, usuario_id: int, session: Session):
        self.usuario_id = usuario_id
        self.session    = session

    def gerar(self) -> dict:
        registros  = self._buscar_registros()
        processado = self._processar(registros)
        return self._formatar(processado)

    @abstractmethod
    def _buscar_registros(self) -> list:
        pass

    @abstractmethod
    def _processar(self, registros: list) -> dict:
        pass

    @abstractmethod
    def _formatar(self, dados: dict) -> dict:
        pass


class RelatorioPorSemana(RelatorioProgresso):

    def _buscar_registros(self) -> list:
        sete_dias_atras = datetime.now(timezone.utc) - timedelta(days=7)
        return (
            self.session.query(TreinoRealizado)
            .filter(
                TreinoRealizado.usuario_id == self.usuario_id,
                TreinoRealizado.data_realizacao >= sete_dias_atras
            )
            .all()
        )

    def _processar(self, registros: list) -> dict:
        contagem = defaultdict(int)
        for r in registros:
            data = r.data_realizacao.date()
            contagem[data] += 1
        return contagem

    def _formatar(self, dados: dict) -> dict:
        hoje = datetime.now(timezone.utc).date()
        por_dia = []
        for i in range(7):
            dia = hoje - timedelta(days=i)
            por_dia.append({
                "data": dia.isoformat(),
                "treinos": dados.get(dia, 0)
            })
        return {"tipo": "semanal", "dias": por_dia}


class RelatorioPorMes(RelatorioProgresso):
    def _buscar_registros(self) -> list:
        trinta_dias_atras = datetime.now(timezone.utc) - timedelta(days=30)
        return (
            self.session.query(TreinoRealizado)
            .filter(
                TreinoRealizado.usuario_id == self.usuario_id,
                TreinoRealizado.data_realizacao >= trinta_dias_atras
            )
            .all()
        )

    def _processar(self, registros: list) -> dict:
        por_semana = defaultdict(int)
        for r in registros:
            semana = r.data_realizacao.isocalendar()[1] 
            por_semana[semana] += 1
        return por_semana

    def _formatar(self, dados: dict) -> dict:
        semanas_ordenadas = sorted(dados.keys(), reverse=True)[:4]
        resultado = [
            {"semana": f"Semana {i+1}", "treinos": dados[s]}
            for i, s in enumerate(semanas_ordenadas)
        ]
        return {"tipo": "mensal", "semanas": resultado}