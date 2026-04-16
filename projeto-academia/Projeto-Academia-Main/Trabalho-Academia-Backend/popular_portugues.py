"""
Script para:
1. APAGAR todos os exercícios antigos do catálogo
2. POPULAR com lista curada 100% em português

Como usar:
    python popular_portugues.py              # apaga tudo e reinsere
    python popular_portugues.py --apenas-inserir  # mantém os atuais e adiciona novos
"""

import argparse
from sqlalchemy.orm import sessionmaker
from database.models import db, ExercicioCatalogo, Base

# ──────────────────────────────────────────────────────────────
# LISTA DE EXERCÍCIOS EM PORTUGUÊS
# Formato: (nome, categoria, equipamento, musculo_principal, musculo_secundario)
# ──────────────────────────────────────────────────────────────
EXERCICIOS = [

    # ═══════════════════ PEITO ═══════════════════
    ("Supino Reto com Barra",          "Peito",   "Barra",    "Peitoral Maior",       "Tríceps, Deltóide Anterior"),
    ("Supino Inclinado com Barra",     "Peito",   "Barra",    "Peitoral Superior",    "Tríceps, Deltóide Anterior"),
    ("Supino Declinado com Barra",     "Peito",   "Barra",    "Peitoral Inferior",    "Tríceps"),
    ("Supino Reto com Halteres",       "Peito",   "Halteres", "Peitoral Maior",       "Tríceps, Deltóide Anterior"),
    ("Supino Inclinado com Halteres",  "Peito",   "Halteres", "Peitoral Superior",    "Tríceps"),
    ("Supino Declinado com Halteres",  "Peito",   "Halteres", "Peitoral Inferior",    "Tríceps"),
    ("Crucifixo Reto com Halteres",    "Peito",   "Halteres", "Peitoral Maior",       "Deltóide Anterior"),
    ("Crucifixo Inclinado",            "Peito",   "Halteres", "Peitoral Superior",    "Deltóide Anterior"),
    ("Crucifixo Declinado",            "Peito",   "Halteres", "Peitoral Inferior",    None),
    ("Crossover no Cabo Alto",         "Peito",   "Cabo",     "Peitoral Inferior",    "Deltóide Anterior"),
    ("Crossover no Cabo Baixo",        "Peito",   "Cabo",     "Peitoral Superior",    "Deltóide Anterior"),
    ("Peck Deck (Voador)",             "Peito",   "Máquina",  "Peitoral Maior",       None),
    ("Flexão de Braço",                "Peito",   "Peso Corporal", "Peitoral Maior",  "Tríceps, Core"),
    ("Flexão com Pés Elevados",        "Peito",   "Peso Corporal", "Peitoral Superior","Tríceps"),
    ("Pullover com Halter",            "Peito",   "Halteres", "Peitoral Maior",       "Serrátil, Latíssimo"),
    ("Mergulho em Paralelas (Peito)",  "Peito",   "Peso Corporal", "Peitoral Inferior","Tríceps"),

    # ═══════════════════ COSTAS ═══════════════════
    ("Puxada Frontal na Polia",        "Costas",  "Cabo",     "Latíssimo do Dorso",   "Bíceps, Rombóide"),
    ("Puxada por Trás",                "Costas",  "Cabo",     "Latíssimo do Dorso",   "Bíceps"),
    ("Remada Curvada com Barra",       "Costas",  "Barra",    "Latíssimo do Dorso",   "Rombóide, Trapézio"),
    ("Remada Curvada com Halteres",    "Costas",  "Halteres", "Latíssimo do Dorso",   "Rombóide"),
    ("Remada Unilateral com Halter",   "Costas",  "Halteres", "Latíssimo do Dorso",   "Rombóide, Bíceps"),
    ("Remada Sentada na Polia",        "Costas",  "Cabo",     "Latíssimo do Dorso",   "Rombóide, Trapézio Médio"),
    ("Remada na Máquina",              "Costas",  "Máquina",  "Latíssimo do Dorso",   "Rombóide"),
    ("Levantamento Terra",             "Costas",  "Barra",    "Eretores da Espinha",  "Glúteos, Isquiotibiais, Trapézio"),
    ("Levantamento Terra Romeno",      "Costas",  "Barra",    "Eretores da Espinha",  "Isquiotibiais, Glúteos"),
    ("Pull-up (Barra Fixa)",           "Costas",  "Peso Corporal", "Latíssimo do Dorso","Bíceps, Rombóide"),
    ("Chin-up (Pegada Supinada)",      "Costas",  "Peso Corporal", "Latíssimo do Dorso","Bíceps"),
    ("Extensão Lombar (Hyperextension)","Costas", "Peso Corporal", "Eretores da Espinha","Glúteos"),
    ("Remada Alta com Barra",          "Costas",  "Barra",    "Trapézio",             "Deltóide Lateral, Bíceps"),
    ("Encolhimento de Ombros com Barra","Costas", "Barra",    "Trapézio Superior",    None),
    ("Encolhimento com Halteres",      "Costas",  "Halteres", "Trapézio Superior",    None),
    ("Face Pull",                      "Costas",  "Cabo",     "Trapézio Médio",       "Rombóide, Deltóide Posterior"),
    ("Serrátil no Cabo",               "Costas",  "Cabo",     "Serrátil Anterior",    None),

    # ═══════════════════ OMBROS ═══════════════════
    ("Desenvolvimento com Barra",      "Ombros",  "Barra",    "Deltóide",             "Tríceps, Trapézio"),
    ("Desenvolvimento com Halteres",   "Ombros",  "Halteres", "Deltóide",             "Tríceps"),
    ("Desenvolvimento na Máquina",     "Ombros",  "Máquina",  "Deltóide",             "Tríceps"),
    ("Elevação Lateral com Halteres",  "Ombros",  "Halteres", "Deltóide Lateral",     None),
    ("Elevação Lateral no Cabo",       "Ombros",  "Cabo",     "Deltóide Lateral",     None),
    ("Elevação Frontal com Halteres",  "Ombros",  "Halteres", "Deltóide Anterior",    None),
    ("Elevação Frontal com Barra",     "Ombros",  "Barra",    "Deltóide Anterior",    None),
    ("Crucifixo Inverso com Halteres", "Ombros",  "Halteres", "Deltóide Posterior",   "Rombóide"),
    ("Crucifixo Inverso na Máquina",   "Ombros",  "Máquina",  "Deltóide Posterior",   "Rombóide"),
    ("Arnold Press",                   "Ombros",  "Halteres", "Deltóide",             "Tríceps"),
    ("Desenvolvimento Militar",        "Ombros",  "Barra",    "Deltóide Anterior",    "Tríceps"),

    # ═══════════════════ BÍCEPS ═══════════════════
    ("Rosca Direta com Barra",         "Bíceps",  "Barra",    "Bíceps Braquial",      "Braquiorradial"),
    ("Rosca Alternada com Halteres",   "Bíceps",  "Halteres", "Bíceps Braquial",      "Braquiorradial"),
    ("Rosca Martelo",                  "Bíceps",  "Halteres", "Braquiorradial",       "Bíceps Braquial"),
    ("Rosca Concentrada",              "Bíceps",  "Halteres", "Bíceps Braquial",      None),
    ("Rosca Scott com Barra",          "Bíceps",  "Barra",    "Bíceps Braquial",      None),
    ("Rosca Scott com Halteres",       "Bíceps",  "Halteres", "Bíceps Braquial",      None),
    ("Rosca no Cabo Baixo",            "Bíceps",  "Cabo",     "Bíceps Braquial",      None),
    ("Rosca 21",                       "Bíceps",  "Barra",    "Bíceps Braquial",      None),
    ("Rosca Inversa",                  "Bíceps",  "Barra",    "Braquiorradial",       "Extensores do Punho"),
    ("Rosca Inclinada com Halteres",   "Bíceps",  "Halteres", "Bíceps Braquial",      None),

    # ═══════════════════ TRÍCEPS ═══════════════════
    ("Tríceps Corda no Pulley",        "Tríceps", "Cabo",     "Tríceps",              None),
    ("Tríceps Barra no Pulley",        "Tríceps", "Cabo",     "Tríceps",              None),
    ("Tríceps Testa com Barra",        "Tríceps", "Barra",    "Tríceps",              None),
    ("Tríceps Testa com Halteres",     "Tríceps", "Halteres", "Tríceps",              None),
    ("Tríceps Francês com Halteres",   "Tríceps", "Halteres", "Tríceps",              None),
    ("Tríceps Francês com Barra",      "Tríceps", "Barra",    "Tríceps",              None),
    ("Tríceps no Banco (Mergulho)",    "Tríceps", "Peso Corporal","Tríceps",          "Deltóide Anterior, Peito"),
    ("Supino Fechado",                 "Tríceps", "Barra",    "Tríceps",              "Peitoral, Deltóide Anterior"),
    ("Kickback de Tríceps",            "Tríceps", "Halteres", "Tríceps",              None),
    ("Tríceps Unilateral no Cabo",     "Tríceps", "Cabo",     "Tríceps",              None),

    # ═══════════════════ PERNAS ═══════════════════
    ("Agachamento Livre com Barra",    "Pernas",  "Barra",    "Quadríceps",           "Glúteos, Isquiotibiais"),
    ("Agachamento Sumô",               "Pernas",  "Barra",    "Adutores",             "Quadríceps, Glúteos"),
    ("Agachamento Frontal",            "Pernas",  "Barra",    "Quadríceps",           "Core, Glúteos"),
    ("Agachamento Hack",               "Pernas",  "Máquina",  "Quadríceps",           "Glúteos"),
    ("Agachamento Búlgaro",            "Pernas",  "Halteres", "Quadríceps",           "Glúteos, Isquiotibiais"),
    ("Leg Press 45°",                  "Pernas",  "Máquina",  "Quadríceps",           "Glúteos, Isquiotibiais"),
    ("Leg Press Horizontal",           "Pernas",  "Máquina",  "Quadríceps",           "Glúteos"),
    ("Extensão de Quadríceps",         "Pernas",  "Máquina",  "Quadríceps",           None),
    ("Flexão de Isquiotibiais Deitado","Pernas",  "Máquina",  "Isquiotibiais",        None),
    ("Flexão de Isquiotibiais em Pé",  "Pernas",  "Máquina",  "Isquiotibiais",        None),
    ("Stiff (Terra Rumeno com Halteres)","Pernas","Halteres", "Isquiotibiais",        "Glúteos, Eretores"),
    ("Avanço com Halteres",            "Pernas",  "Halteres", "Quadríceps",           "Glúteos, Isquiotibiais"),
    ("Avanço Caminhando",              "Pernas",  "Halteres", "Quadríceps",           "Glúteos"),
    ("Cadeira Adutora",                "Pernas",  "Máquina",  "Adutores",             None),
    ("Cadeira Abdutora",               "Pernas",  "Máquina",  "Abdutores",            "Glúteo Médio"),
    ("Panturrilha em Pé (Máquina)",    "Pernas",  "Máquina",  "Gastrocnêmio",         "Sóleo"),
    ("Panturrilha Sentado",            "Pernas",  "Máquina",  "Sóleo",                None),
    ("Panturrilha no Leg Press",       "Pernas",  "Máquina",  "Gastrocnêmio",         None),
    ("Afundo com Barra",               "Pernas",  "Barra",    "Quadríceps",           "Glúteos"),
    ("Good Morning",                   "Pernas",  "Barra",    "Isquiotibiais",        "Eretores da Espinha"),

    # ═══════════════════ GLÚTEOS ═══════════════════
    ("Hip Thrust com Barra",           "Glúteos", "Barra",    "Glúteo Máximo",        "Isquiotibiais"),
    ("Hip Thrust Unilateral",          "Glúteos", "Peso Corporal","Glúteo Máximo",    "Isquiotibiais"),
    ("Elevação Pélvica no Solo",       "Glúteos", "Peso Corporal","Glúteo Máximo",    None),
    ("Glúteo no Cabo (Kickback)",      "Glúteos", "Cabo",     "Glúteo Máximo",        "Isquiotibiais"),
    ("Agachamento Sumô com Halter",    "Glúteos", "Halteres", "Glúteo Máximo",        "Adutores"),
    ("Step Up no Banco",               "Glúteos", "Halteres", "Glúteo Máximo",        "Quadríceps"),
    ("Glúteo no Smith (Donkey Kick)",  "Glúteos", "Máquina",  "Glúteo Máximo",        None),

    # ═══════════════════ ABDÔMEN ═══════════════════
    ("Abdominal Crunch",               "Abdômen", "Peso Corporal","Reto Abdominal",   None),
    ("Abdominal Remador",              "Abdômen", "Peso Corporal","Reto Abdominal",   "Oblíquos"),
    ("Prancha Abdominal",              "Abdômen", "Peso Corporal","Core",             "Transverso Abdominal"),
    ("Prancha Lateral",                "Abdômen", "Peso Corporal","Oblíquos",         "Core"),
    ("Elevação de Pernas Deitado",     "Abdômen", "Peso Corporal","Reto Abdominal",   "Iliopsoas"),
    ("Elevação de Pernas na Barra",    "Abdômen", "Peso Corporal","Reto Abdominal",   "Iliopsoas"),
    ("Abdominal no Cabo",              "Abdômen", "Cabo",     "Reto Abdominal",       None),
    ("Rotação Russa",                  "Abdômen", "Peso Corporal","Oblíquos",         "Reto Abdominal"),
    ("Mountain Climber",               "Abdômen", "Peso Corporal","Core",             "Deltóide, Quadríceps"),
    ("Dead Bug",                       "Abdômen", "Peso Corporal","Transverso Abdominal","Core"),
    ("Roda Abdominal",                 "Abdômen", "Equipamento","Reto Abdominal",     "Latíssimo, Ombros"),
    ("Abdominal Bicicleta",            "Abdômen", "Peso Corporal","Oblíquos",         "Reto Abdominal"),
    ("Superman",                       "Abdômen", "Peso Corporal","Eretores da Espinha","Glúteos"),

    # ═══════════════════ CARDIO / FUNCIONAL ═══════════════════
    ("Burpee",                         "Funcional","Peso Corporal","Full Body",        None),
    ("Polichinelo",                    "Funcional","Peso Corporal","Deltóide",        "Gastrocnêmio"),
    ("Agachamento com Salto",          "Funcional","Peso Corporal","Quadríceps",      "Glúteos"),
    ("Corrida Estacionária",           "Cardio",  "Peso Corporal","Gastrocnêmio",     "Quadríceps"),
    ("Corda Battle Rope",              "Cardio",  "Equipamento","Full Body",          None),
    ("Kettlebell Swing",               "Funcional","Kettlebell","Glúteos",            "Isquiotibiais, Core"),
    ("Kettlebell Clean and Press",     "Funcional","Kettlebell","Full Body",          None),
    ("Kettlebell Goblet Squat",        "Pernas",  "Kettlebell","Quadríceps",          "Glúteos, Core"),
    ("Caminhar na Esteira (Inclinado)","Cardio",  "Máquina",  "Gastrocnêmio",         "Glúteos"),
    ("Bicicleta Ergométrica",          "Cardio",  "Máquina",  "Quadríceps",           "Isquiotibiais"),
    ("Elíptico",                       "Cardio",  "Máquina",  "Full Body",            None),
    ("Remo Ergométrico",               "Cardio",  "Máquina",  "Costas",               "Pernas, Bíceps"),
    ("Corda de Pular",                 "Cardio",  "Equipamento","Gastrocnêmio",       "Core"),

    # ═══════════════════ MOBILIDADE / ALONGAMENTO ═══════════════════
    ("Alongamento de Isquiotibiais",   "Mobilidade","Peso Corporal","Isquiotibiais",  None),
    ("Alongamento de Quadríceps em Pé","Mobilidade","Peso Corporal","Quadríceps",     None),
    ("Alongamento de Piriforme",       "Mobilidade","Peso Corporal","Glúteo Médio",   None),
    ("Hip Flexor Stretch (Ajoelhado)", "Mobilidade","Peso Corporal","Iliopsoas",      None),
    ("Cat-Cow (Gato e Vaca)",          "Mobilidade","Peso Corporal","Eretores da Espinha","Core"),
    ("Rotação Torácica",               "Mobilidade","Peso Corporal","Coluna Torácica",None),
    ("Agachamento Profundo (Parado)",  "Mobilidade","Peso Corporal","Quadríceps",     "Tornozelo"),
]


# ──────────────────────────────────────────────────────────────
# FUNÇÕES
# ──────────────────────────────────────────────────────────────

def apagar_catalogo(session):
    """Remove todos os registros de exercicios_catalogo."""
    deletados = session.query(ExercicioCatalogo).delete()
    session.commit()
    print(f"🗑️  {deletados} exercícios removidos do catálogo.")


def popular_catalogo(session):
    """Insere todos os exercícios da lista (ignora duplicatas por nome)."""
    nomes_existentes = {e.nome for e in session.query(ExercicioCatalogo.nome).all()}
    novos = 0

    for i, (nome, categoria, equipamento, musculo_principal, musculo_secundario) in enumerate(EXERCICIOS, start=1):
        if nome in nomes_existentes:
            continue

        ex = ExercicioCatalogo(
            api_id=10000 + i,       # IDs locais a partir de 10000 (não conflita com wger)
            nome=nome,
            nome_en=None,
            descricao=None,
            categoria=categoria,
            equipamento=equipamento,
            musculo_principal=musculo_principal,
            musculo_secundario=musculo_secundario,
        )
        session.add(ex)
        novos += 1

    session.commit()
    print(f"✅ {novos} exercícios adicionados ao catálogo.")


def main(apenas_inserir=False):
    Base.metadata.create_all(bind=db)
    Session = sessionmaker(bind=db)
    session = Session()

    if not apenas_inserir:
        print("⚠️  Apagando catálogo existente...")
        apagar_catalogo(session)

    print("📥 Populando com exercícios em português...")
    popular_catalogo(session)
    session.close()
    print("\n🎉 Pronto! Catálogo atualizado com sucesso.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apenas-inserir",
        action="store_true",
        help="Não apaga os exercícios existentes; apenas adiciona os novos."
    )
    args = parser.parse_args()
    main(apenas_inserir=args.apenas_inserir)