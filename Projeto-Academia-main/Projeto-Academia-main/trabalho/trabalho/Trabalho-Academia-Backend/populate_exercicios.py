"""
Script de importação do catálogo de exercícios via API pública wger.
https://wger.de/api/v2/

Como usar:
    python populate_exercicios.py

O script busca todos os exercícios disponíveis na wger e salva na tabela
`exercicios_catalogo` do banco local. Exercícios já existentes (por api_id)
são ignorados para evitar duplicatas.
"""

import requests
from sqlalchemy.orm import sessionmaker
from database.models import db, ExercicioCatalogo, Base

# ─────────────────────────────────────────────
# Configuração
# ─────────────────────────────────────────────
BASE_URL = "https://wger.de/api/v2"
PAGE_LIMIT = 100   # máximo de itens por página da wger

# Códigos de idioma na wger
LANG_PT = 11   # Português
LANG_EN = 2    # Inglês (fallback)

Session = sessionmaker(bind=db)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def buscar_todos(endpoint: str, params: dict) -> list:
    """Percorre todas as páginas de uma rota da wger e retorna todos os itens."""
    resultados = []
    url = f"{BASE_URL}/{endpoint}/"
    params["limit"] = PAGE_LIMIT
    params["offset"] = 0

    while url:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        resultados.extend(data["results"])
        url = data.get("next")          # None quando acabar
        params = {}                     # next já vem com os params na URL
        print(f"  {len(resultados)} exercícios carregados...")

    return resultados


def buscar_mapa(endpoint: str) -> dict:
    """Retorna {id: nome} para tabelas de referência (músculo, equipamento, categoria)."""
    items = buscar_todos(endpoint, {"format": "json", "language": LANG_EN})
    return {item["id"]: item.get("name", "") for item in items}


# ─────────────────────────────────────────────
# Importação principal
# ─────────────────────────────────────────────
def importar_exercicios():
    Base.metadata.create_all(bind=db)
    session = Session()

    print("🔄 Buscando tabelas de referência...")
    categorias = buscar_mapa("exercisecategory")
    equipamentos = buscar_mapa("equipment")
    musculos = buscar_mapa("muscle")
    print(f"   {len(categorias)} categorias | {len(equipamentos)} equipamentos | {len(musculos)} músculos\n")

    print("🔄 Buscando exercícios (info completa)...")
    # exerciseinfo retorna tudo de uma vez: traduções, músculos, equipamentos
    exercicios_info = buscar_todos("exerciseinfo", {"format": "json", "language": LANG_PT})
    print(f"\n✅ Total bruto: {len(exercicios_info)} exercícios\n")

    novos = 0
    ignorados = 0

    for ex in exercicios_info:
        api_id = ex["id"]

        # Pula se já existe
        if session.query(ExercicioCatalogo).filter_by(api_id=api_id).first():
            ignorados += 1
            continue

        # ── Nome em português (translations[])
        nome_pt = None
        nome_en = None
        for t in ex.get("translations", []):
            if t["language"] == LANG_PT and t.get("name"):
                nome_pt = t["name"]
            if t["language"] == LANG_EN and t.get("name"):
                nome_en = t["name"]

        nome_final = nome_pt or nome_en
        if not nome_final:
            ignorados += 1
            continue   # exercício sem nome em nenhum idioma → descarta

        # ── Categoria
        cat_id = ex.get("category", {})
        if isinstance(cat_id, dict):
            cat_id = cat_id.get("id")
        categoria = categorias.get(cat_id, None)

        # ── Equipamento (lista de dicts; pega o id do primeiro)
        equip_raw = ex.get("equipment", [])
        if equip_raw:
            primeiro_equip = equip_raw[0]
            equip_id = primeiro_equip["id"] if isinstance(primeiro_equip, dict) else primeiro_equip
            equipamento = equipamentos.get(equip_id, None)
        else:
            equipamento = None

        # ── Músculos (lista de dicts ou lista de ids)
        def extrair_id(item):
            return item["id"] if isinstance(item, dict) else item

        musculos_principais = [extrair_id(m) for m in ex.get("muscles", [])]
        musculos_secundarios = [extrair_id(m) for m in ex.get("muscles_secondary", [])]

        musculo_principal = (
            musculos.get(musculos_principais[0], None) if musculos_principais else None
        )
        musculo_secundario = (
            ", ".join(musculos.get(m, "") for m in musculos_secundarios) or None
        )

        # ── Descrição (usa a versão em PT, senão EN)
        descricao = None
        for t in ex.get("translations", []):
            if t["language"] == LANG_PT and t.get("description"):
                descricao = t["description"]
                break
        if not descricao:
            for t in ex.get("translations", []):
                if t["language"] == LANG_EN and t.get("description"):
                    descricao = t["description"]
                    break

        novo = ExercicioCatalogo(
            api_id=api_id,
            nome=nome_final,
            nome_en=nome_en,
            descricao=descricao,
            categoria=categoria,
            equipamento=equipamento,
            musculo_principal=musculo_principal,
            musculo_secundario=musculo_secundario,
        )
        session.add(novo)
        novos += 1

    session.commit()
    session.close()

    print(f"🎉 Importação concluída!")
    print(f"   ✅ {novos} exercícios adicionados ao catálogo")
    print(f"   ⏭  {ignorados} ignorados (já existentes ou sem nome)")


if __name__ == "__main__":
    importar_exercicios()