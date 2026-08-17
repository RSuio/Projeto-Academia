"""
Script para popular o catálogo de exercícios em português com vídeos demonstrativos.

Como usar:
    python popular_portugues.py                   # Atualiza/Insere exercícios e vídeos
    python popular_portugues.py --recriar-tudo    # Apaga tudo e recria do zero
"""

import os
import sys
import argparse

# Garante que o diretório atual do backend está no sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Previne UnicodeEncodeError no Windows (CP1252) ao imprimir no terminal
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.database.models import db, ExercicioCatalogo, Base

# ──────────────────────────────────────────────────────────────
# LISTA DE EXERCÍCIOS EM PORTUGUÊS COM VÍDEOS DEMONSTRATIVOS
# Formato: (nome, categoria, equipamento, musculo_principal, musculo_secundario, video_url)
# ──────────────────────────────────────────────────────────────
EXERCICIOS = [

    # ═══════════════════ PEITO ═══════════════════
    ("Supino Reto com Barra",          "Peito",   "Barra",    "Peitoral Maior",       "Tríceps, Deltóide Anterior", "https://www.youtube.com/watch?v=rT7DgCr-3pg"),
    ("Supino Inclinado com Barra",     "Peito",   "Barra",    "Peitoral Superior",    "Tríceps, Deltóide Anterior", "https://www.youtube.com/watch?v=SrqOu55lrYU"),
    ("Supino Declinado com Barra",     "Peito",   "Barra",    "Peitoral Inferior",    "Tríceps", "https://www.youtube.com/watch?v=LfyQBUKR8SE"),
    ("Supino Reto com Halteres",       "Peito",   "Halteres", "Peitoral Maior",       "Tríceps, Deltóide Anterior", "https://www.youtube.com/watch?v=VmB1G1K7v94"),
    ("Supino Inclinado com Halteres",  "Peito",   "Halteres", "Peitoral Superior",    "Tríceps", "https://www.youtube.com/watch?v=8iPEnn-ltC8"),
    ("Supino Declinado com Halteres",  "Peito",   "Halteres", "Peitoral Inferior",    "Tríceps", "https://www.youtube.com/watch?v=4nEWBtI_jZ0"),
    ("Crucifixo Reto com Halteres",    "Peito",   "Halteres", "Peitoral Maior",       "Deltóide Anterior", "https://www.youtube.com/watch?v=eozdVDA78K0"),
    ("Crucifixo Inclinado",            "Peito",   "Halteres", "Peitoral Superior",    "Deltóide Anterior", "https://www.youtube.com/watch?v=bDaIL_zKbGs"),
    ("Crucifixo Declinado",            "Peito",   "Halteres", "Peitoral Inferior",    None, "https://www.youtube.com/watch?v=4nEWBtI_jZ0"),
    ("Crossover no Cabo Alto",         "Peito",   "Cabo",     "Peitoral Inferior",    "Deltóide Anterior", "https://www.youtube.com/watch?v=taI4XduLpTk"),
    ("Crossover no Cabo Baixo",        "Peito",   "Cabo",     "Peitoral Superior",    "Deltóide Anterior", "https://www.youtube.com/watch?v=vVj2Uek5KCY"),
    ("Peck Deck (Voador)",             "Peito",   "Máquina",  "Peitoral Maior",       None, "https://www.youtube.com/watch?v=eGjt4lkGeZ4"),
    ("Flexão de Braço",                "Peito",   "Peso Corporal", "Peitoral Maior",  "Tríceps, Core", "https://www.youtube.com/watch?v=IODxDxX7oi4"),
    ("Flexão com Pés Elevados",        "Peito",   "Peso Corporal", "Peitoral Superior","Tríceps", "https://www.youtube.com/watch?v=5BRW4bH84Xg"),
    ("Pullover com Halter",            "Peito",   "Halteres", "Peitoral Maior",       "Serrátil, Latíssimo", "https://www.youtube.com/watch?v=FK4rT727XgU"),
    ("Mergulho em Paralelas (Peito)",  "Peito",   "Peso Corporal", "Peitoral Inferior","Tríceps", "https://www.youtube.com/watch?v=2z8JmcrW-As"),

    # ═══════════════════ COSTAS ═══════════════════
    ("Puxada Frontal na Polia",        "Costas",  "Cabo",     "Latíssimo do Dorso",   "Bíceps, Rombóide", "https://www.youtube.com/watch?v=CAwf7n6Luuc"),
    ("Puxada por Trás",                "Costas",  "Cabo",     "Latíssimo do Dorso",   "Bíceps", "https://www.youtube.com/watch?v=JEb-dwU3VF4"),
    ("Remada Curvada com Barra",       "Costas",  "Barra",    "Latíssimo do Dorso",   "Rombóide, Trapézio", "https://www.youtube.com/watch?v=G8l_8chR5BE"),
    ("Remada Curvada com Halteres",    "Costas",  "Halteres", "Latíssimo do Dorso",   "Rombóide", "https://www.youtube.com/watch?v=pYcpY20QaE8"),
    ("Remada Unilateral com Halter",   "Costas",  "Halteres", "Latíssimo do Dorso",   "Rombóide, Bíceps", "https://www.youtube.com/watch?v=dFzUjzfih7U"),
    ("Remada Sentada na Polia",        "Costas",  "Cabo",     "Latíssimo do Dorso",   "Rombóide, Trapézio Médio", "https://www.youtube.com/watch?v=GZbfZ033f74"),
    ("Remada na Máquina",              "Costas",  "Máquina",  "Latíssimo do Dorso",   "Rombóide", "https://www.youtube.com/watch?v=sP_4flChzOQ"),
    ("Levantamento Terra",             "Costas",  "Barra",    "Eretores da Espinha",  "Glúteos, Isquiotibiais, Trapézio", "https://www.youtube.com/watch?v=op9kVnSso6Q"),
    ("Levantamento Terra Romeno",      "Costas",  "Barra",    "Eretores da Espinha",  "Isquiotibiais, Glúteos", "https://www.youtube.com/watch?v=JCXUYuzwNrM"),
    ("Pull-up (Barra Fixa)",           "Costas",  "Peso Corporal", "Latíssimo do Dorso","Bíceps, Rombóide", "https://www.youtube.com/watch?v=eGo4IYlbE5g"),
    ("Chin-up (Pegada Supinada)",      "Costas",  "Peso Corporal", "Latíssimo do Dorso","Bíceps", "https://www.youtube.com/watch?v=b-ACTS_5Gf4"),
    ("Extensão Lombar (Hyperextension)","Costas", "Peso Corporal", "Eretores da Espinha","Glúteos", "https://www.youtube.com/watch?v=ph3pddpKzzw"),
    ("Remada Alta com Barra",          "Costas",  "Barra",    "Trapézio",             "Deltóide Lateral, Bíceps", "https://www.youtube.com/watch?v=IhZLBjGPR8M"),
    ("Encolhimento de Ombros com Barra","Costas", "Barra",    "Trapézio Superior",    None, "https://www.youtube.com/watch?v=48H3vNf4w60"),
    ("Encolhimento com Halteres",      "Costas",  "Halteres", "Trapézio Superior",    None, "https://www.youtube.com/watch?v=g6qbq4Lf1FI"),
    ("Face Pull",                      "Costas",  "Cabo",     "Trapézio Médio",       "Rombóide, Deltóide Posterior", "https://www.youtube.com/watch?v=rep-qVOkqgk"),
    ("Serrátil no Cabo",               "Costas",  "Cabo",     "Serrátil Anterior",    None, "https://www.youtube.com/watch?v=Zf3BhyDkCgU"),

    # ═══════════════════ OMBROS ═══════════════════
    ("Desenvolvimento com Barra",      "Ombros",  "Barra",    "Deltóide",             "Tríceps, Trapézio", "https://www.youtube.com/watch?v=2yjwXTZQDDI"),
    ("Desenvolvimento com Halteres",   "Ombros",  "Halteres", "Deltóide",             "Tríceps", "https://www.youtube.com/watch?v=qEwKCR5JCog"),
    ("Desenvolvimento na Máquina",     "Ombros",  "Máquina",  "Deltóide",             "Tríceps", "https://www.youtube.com/watch?v=Wqq43dKW1TU"),
    ("Elevação Lateral com Halteres",  "Ombros",  "Halteres", "Deltóide Lateral",     None, "https://www.youtube.com/watch?v=3VcKaXpzqRo"),
    ("Elevação Lateral no Cabo",       "Ombros",  "Cabo",     "Deltóide Lateral",     None, "https://www.youtube.com/watch?v=PPrzBWZDOhA"),
    ("Elevação Frontal com Halteres",  "Ombros",  "Halteres", "Deltóide Anterior",    None, "https://www.youtube.com/watch?v=-t7fuZ0KhDA"),
    ("Elevação Frontal com Barra",     "Ombros",  "Barra",    "Deltóide Anterior",    None, "https://www.youtube.com/watch?v=ALq7hFvUfbg"),
    ("Crucifixo Inverso com Halteres", "Ombros",  "Halteres", "Deltóide Posterior",   "Rombóide", "https://www.youtube.com/watch?v=H530fW3KWQQ"),
    ("Crucifixo Inverso na Máquina",   "Ombros",  "Máquina",  "Deltóide Posterior",   "Rombóide", "https://www.youtube.com/watch?v=f9A24jF6l9U"),
    ("Arnold Press",                   "Ombros",  "Halteres", "Deltóide",             "Tríceps", "https://www.youtube.com/watch?v=3ml7BH7mNwQ"),
    ("Desenvolvimento Militar",        "Ombros",  "Barra",    "Deltóide Anterior",    "Tríceps", "https://www.youtube.com/watch?v=2yjwXTZQDDI"),

    # ═══════════════════ BÍCEPS ═══════════════════
    ("Rosca Direta com Barra",         "Bíceps",  "Barra",    "Bíceps Braquial",      "Braquiorradial", "https://www.youtube.com/watch?v=ykJmrZ5v0Oo"),
    ("Rosca Alternada com Halteres",   "Bíceps",  "Halteres", "Bíceps Braquial",      "Braquiorradial", "https://www.youtube.com/watch?v=sAq_ocpRh_I"),
    ("Rosca Martelo",                  "Bíceps",  "Halteres", "Braquiorradial",       "Bíceps Braquial", "https://www.youtube.com/watch?v=zC3nLlEvin4"),
    ("Rosca Concentrada",              "Bíceps",  "Halteres", "Bíceps Braquial",      None, "https://www.youtube.com/watch?v=0AUGkch3tzc"),
    ("Rosca Scott com Barra",          "Bíceps",  "Barra",    "Bíceps Braquial",      None, "https://www.youtube.com/watch?v=fIWP-FRFNU0"),
    ("Rosca Scott com Halteres",       "Bíceps",  "Halteres", "Bíceps Braquial",      None, "https://www.youtube.com/watch?v=YpmnWjI5k2s"),
    ("Rosca no Cabo Baixo",            "Bíceps",  "Cabo",     "Bíceps Braquial",      None, "https://www.youtube.com/watch?v=NFzTWp2qpiE"),
    ("Rosca 21",                       "Bíceps",  "Barra",    "Bíceps Braquial",      None, "https://www.youtube.com/watch?v=qfZ1PqY6Qeo"),
    ("Rosca Inversa",                  "Bíceps",  "Barra",    "Braquiorradial",       "Extensores do Punho", "https://www.youtube.com/watch?v=nVhU3e5H4W4"),
    ("Rosca Inclinada com Halteres",   "Bíceps",  "Halteres", "Bíceps Braquial",      None, "https://www.youtube.com/watch?v=soxrZlIl35U"),

    # ═══════════════════ TRÍCEPS ═══════════════════
    ("Tríceps Corda no Pulley",        "Tríceps", "Cabo",     "Tríceps",              None, "https://www.youtube.com/watch?v=vB5OHsJ3EME"),
    ("Tríceps Barra no Pulley",        "Tríceps", "Cabo",     "Tríceps",              None, "https://www.youtube.com/watch?v=2-LAMcpzODU"),
    ("Tríceps Testa com Barra",        "Tríceps", "Barra",    "Tríceps",              None, "https://www.youtube.com/watch?v=d_KZxkY_0cM"),
    ("Tríceps Testa com Halteres",     "Tríceps", "Halteres", "Tríceps",              None, "https://www.youtube.com/watch?v=ir5Psb4V9v8"),
    ("Tríceps Francês com Halteres",   "Tríceps", "Halteres", "Tríceps",              None, "https://www.youtube.com/watch?v=_gsUck-7M74"),
    ("Tríceps Francês com Barra",      "Tríceps", "Barra",    "Tríceps",              None, "https://www.youtube.com/watch?v=3R8r_4S5h0E"),
    ("Tríceps no Banco (Mergulho)",    "Tríceps", "Peso Corporal","Tríceps",          "Deltóide Anterior, Peito", "https://www.youtube.com/watch?v=0326dy_-CzM"),
    ("Supino Fechado",                 "Tríceps", "Barra",    "Tríceps",              "Peitoral, Deltóide Anterior", "https://www.youtube.com/watch?v=nEF0bv2FW94"),
    ("Kickback de Tríceps",            "Tríceps", "Halteres", "Tríceps",              None, "https://www.youtube.com/watch?v=6SS6K3lAwZ8"),
    ("Tríceps Unilateral no Cabo",     "Tríceps", "Cabo",     "Tríceps",              None, "https://www.youtube.com/watch?v=k_ZkI9lWqG8"),

    # ═══════════════════ PERNAS ═══════════════════
    ("Agachamento Livre com Barra",    "Pernas",  "Barra",    "Quadríceps",           "Glúteos, Isquiotibiais", "https://www.youtube.com/watch?v=bEv6CCg2BC8"),
    ("Agachamento Sumô",               "Pernas",  "Barra",    "Adutores",             "Quadríceps, Glúteos", "https://www.youtube.com/watch?v=9ZuDXYJ6B0Y"),
    ("Agachamento Frontal",            "Pernas",  "Barra",    "Quadríceps",           "Core, Glúteos", "https://www.youtube.com/watch?v=uYumuL_G_V0"),
    ("Agachamento Hack",               "Pernas",  "Máquina",  "Quadríceps",           "Glúteos", "https://www.youtube.com/watch?v=0tn5K9NlCfo"),
    ("Agachamento Búlgaro",            "Pernas",  "Halteres", "Quadríceps",           "Glúteos, Isquiotibiais", "https://www.youtube.com/watch?v=2C-uNgKwPLE"),
    ("Leg Press 45°",                  "Pernas",  "Máquina",  "Quadríceps",           "Glúteos, Isquiotibiais", "https://www.youtube.com/watch?v=IZxyjW7MPJQ"),
    ("Leg Press Horizontal",           "Pernas",  "Máquina",  "Quadríceps",           "Glúteos", "https://www.youtube.com/watch?v=CHphWpQ4e2s"),
    ("Extensão de Quadríceps",         "Pernas",  "Máquina",  "Quadríceps",           None, "https://www.youtube.com/watch?v=YyvSfVjQeL0"),
    ("Flexão de Isquiotibiais Deitado","Pernas",  "Máquina",  "Isquiotibiais",        None, "https://www.youtube.com/watch?v=1Tq3EDRyKUw"),
    ("Flexão de Isquiotibiais em Pé",  "Pernas",  "Máquina",  "Isquiotibiais",        None, "https://www.youtube.com/watch?v=A8n_jFpA_6g"),
    ("Stiff (Terra Rumeno com Halteres)","Pernas","Halteres", "Isquiotibiais",        "Glúteos, Eretores", "https://www.youtube.com/watch?v=JCXUYuzwNrM"),
    ("Avanço com Halteres",            "Pernas",  "Halteres", "Quadríceps",           "Glúteos, Isquiotibiais", "https://www.youtube.com/watch?v=D7KaRcUTQeE"),
    ("Avanço Caminhando",              "Pernas",  "Halteres", "Quadríceps",           "Glúteos", "https://www.youtube.com/watch?v=L8fvypPrzzs"),
    ("Cadeira Adutora",                "Pernas",  "Máquina",  "Adutores",             None, "https://www.youtube.com/watch?v=nNk5J8z43d8"),
    ("Cadeira Abdutora",               "Pernas",  "Máquina",  "Abdutores",            "Glúteo Médio", "https://www.youtube.com/watch?v=bZg0P8Fp3vE"),
    ("Panturrilha em Pé (Máquina)",    "Pernas",  "Máquina",  "Gastrocnêmio",         "Sóleo", "https://www.youtube.com/watch?v=-M4-G8p8fmc"),
    ("Panturrilha Sentado",            "Pernas",  "Máquina",  "Sóleo",                None, "https://www.youtube.com/watch?v=JbyjNymZOt0"),
    ("Panturrilha no Leg Press",       "Pernas",  "Máquina",  "Gastrocnêmio",         None, "https://www.youtube.com/watch?v=KxEYX_cuerM"),
    ("Afundo com Barra",               "Pernas",  "Barra",    "Quadríceps",           "Glúteos", "https://www.youtube.com/watch?v=qe3lX2G67aU"),
    ("Good Morning",                   "Pernas",  "Barra",    "Isquiotibiais",        "Eretores da Espinha", "https://www.youtube.com/watch?v=YA-h3n9L4YU"),

    # ═══════════════════ GLÚTEOS ═══════════════════
    ("Hip Thrust com Barra",           "Glúteos", "Barra",    "Glúteo Máximo",        "Isquiotibiais", "https://www.youtube.com/watch?v=SEdqd1n0cvg"),
    ("Hip Thrust Unilateral",          "Glúteos", "Peso Corporal","Glúteo Máximo",    "Isquiotibiais", "https://www.youtube.com/watch?v=2r3A_5l7y9U"),
    ("Elevação Pélvica no Solo",       "Glúteos", "Peso Corporal","Glúteo Máximo",    None, "https://www.youtube.com/watch?v=wPM8icPu6H8"),
    ("Glúteo no Cabo (Kickback)",      "Glúteos", "Cabo",     "Glúteo Máximo",        "Isquiotibiais", "https://www.youtube.com/watch?v=f_VpP3ZkH8k"),
    ("Agachamento Sumô com Halter",    "Glúteos", "Halteres", "Glúteo Máximo",        "Adutores", "https://www.youtube.com/watch?v=9ZuDXYJ6B0Y"),
    ("Step Up no Banco",               "Glúteos", "Halteres", "Glúteo Máximo",        "Quadríceps", "https://www.youtube.com/watch?v=dQqApCGd5Ss"),
    ("Glúteo no Smith (Donkey Kick)",  "Glúteos", "Máquina",  "Glúteo Máximo",        None, "https://www.youtube.com/watch?v=xP3yRzHhL5g"),

    # ═══════════════════ ABDÔMEN ═══════════════════
    ("Abdominal Crunch",               "Abdômen", "Peso Corporal","Reto Abdominal",   None, "https://www.youtube.com/watch?v=5ER5Of4MOPI"),
    ("Abdominal Remador",              "Abdômen", "Peso Corporal","Reto Abdominal",   "Oblíquos", "https://www.youtube.com/watch?v=kYJ-iXkZk_g"),
    ("Prancha Abdominal",              "Abdômen", "Peso Corporal","Core",             "Transverso Abdominal", "https://www.youtube.com/watch?v=ASdvN_XEl_c"),
    ("Prancha Lateral",                "Abdômen", "Peso Corporal","Oblíquos",         "Core", "https://www.youtube.com/watch?v=NXr4FwHNKYw"),
    ("Elevação de Pernas Deitado",     "Abdômen", "Peso Corporal","Reto Abdominal",   "Iliopsoas", "https://www.youtube.com/watch?v=JB2oyawG9KI"),
    ("Elevação de Pernas na Barra",    "Abdômen", "Peso Corporal","Reto Abdominal",   "Iliopsoas", "https://www.youtube.com/watch?v=hdng3Nm1x_E"),
    ("Abdominal no Cabo",              "Abdômen", "Cabo",     "Reto Abdominal",       None, "https://www.youtube.com/watch?v=2fO5Nl5B4Xg"),
    ("Rotação Russa",                  "Abdômen", "Peso Corporal","Oblíquos",         "Reto Abdominal", "https://www.youtube.com/watch?v=wkD8rjkodUI"),
    ("Mountain Climber",               "Abdômen", "Peso Corporal","Core",             "Deltóide, Quadríceps", "https://www.youtube.com/watch?v=nmwgirgXLYM"),
    ("Dead Bug",                       "Abdômen", "Peso Corporal","Transverso Abdominal","Core", "https://www.youtube.com/watch?v=g_BYB0R-4Ws"),
    ("Roda Abdominal",                 "Abdômen", "Equipamento","Reto Abdominal",     "Latíssimo, Ombros", "https://www.youtube.com/watch?v=rqiTPdK1c_I"),
    ("Abdominal Bicicleta",            "Abdômen", "Peso Corporal","Oblíquos",         "Reto Abdominal", "https://www.youtube.com/watch?v=9FGilxCbdz8"),
    ("Superman",                       "Abdômen", "Peso Corporal","Eretores da Espinha","Glúteos", "https://www.youtube.com/watch?v=z6PJMT2y8GQ"),

    # ═══════════════════ CARDIO / FUNCIONAL ═══════════════════
    ("Burpee",                         "Funcional","Peso Corporal","Full Body",        None, "https://www.youtube.com/watch?v=TU8QYVW0gDU"),
    ("Polichinelo",                    "Funcional","Peso Corporal","Deltóide",        "Gastrocnêmio", "https://www.youtube.com/watch?v=iSSAk4XCsRA"),
    ("Agachamento com Salto",          "Funcional","Peso Corporal","Quadríceps",      "Glúteos", "https://www.youtube.com/watch?v=U4s4mEQ5VqU"),
    ("Corrida Estacionária",           "Cardio",  "Peso Corporal","Gastrocnêmio",     "Quadríceps", "https://www.youtube.com/watch?v=1xN8gK_Lp7w"),
    ("Corda Battle Rope",              "Cardio",  "Equipamento","Full Body",          None, "https://www.youtube.com/watch?v=uK1f_8xM2Wc"),
    ("Kettlebell Swing",               "Funcional","Kettlebell","Glúteos",            "Isquiotibiais, Core", "https://www.youtube.com/watch?v=YSxHifyI6s8"),
    ("Kettlebell Clean and Press",     "Funcional","Kettlebell","Full Body",          None, "https://www.youtube.com/watch?v=3gXG_gWq_c8"),
    ("Kettlebell Goblet Squat",        "Pernas",  "Kettlebell","Quadríceps",          "Glúteos, Core", "https://www.youtube.com/watch?v=MeIiIdhvXT4"),
    ("Caminhar na Esteira (Inclinado)","Cardio",  "Máquina",  "Gastrocnêmio",         "Glúteos", "https://www.youtube.com/watch?v=7c_B9l9V1rA"),
    ("Bicicleta Ergométrica",          "Cardio",  "Máquina",  "Quadríceps",           "Isquiotibiais", "https://www.youtube.com/watch?v=wX5yP2uW6oM"),
    ("Elíptico",                       "Cardio",  "Máquina",  "Full Body",            None, "https://www.youtube.com/watch?v=f1n0iW8p_0Q"),
    ("Remo Ergométrico",               "Cardio",  "Máquina",  "Costas",               "Pernas, Bíceps", "https://www.youtube.com/watch?v=zQ82RYIFLN8"),
    ("Corda de Pular",                 "Cardio",  "Equipamento","Gastrocnêmio",       "Core", "https://www.youtube.com/watch?v=u3zgHI8QnqE"),

    # ═══════════════════ MOBILIDADE / ALONGAMENTO ═══════════════════
    ("Alongamento de Isquiotibiais",   "Mobilidade","Peso Corporal","Isquiotibiais",  None, "https://www.youtube.com/watch?v=FDwpXzmvYvA"),
    ("Alongamento de Quadríceps em Pé","Mobilidade","Peso Corporal","Quadríceps",     None, "https://www.youtube.com/watch?v=6hL9x0C1P7g"),
    ("Alongamento de Piriforme",       "Mobilidade","Peso Corporal","Glúteo Médio",   None, "https://www.youtube.com/watch?v=7v2jQJ1rP3c"),
    ("Hip Flexor Stretch (Ajoelhado)", "Mobilidade","Peso Corporal","Iliopsoas",      None, "https://www.youtube.com/watch?v=YQmpO9VT2X4"),
    ("Cat-Cow (Gato e Vaca)",          "Mobilidade","Peso Corporal","Eretores da Espinha","Core", "https://www.youtube.com/watch?v=KpN_b_qSg7A"),
    ("Rotação Torácica",               "Mobilidade","Peso Corporal","Coluna Torácica",None, "https://www.youtube.com/watch?v=P2k_z2w8z_g"),
    ("Agachamento Profundo (Parado)",  "Mobilidade","Peso Corporal","Quadríceps",     "Tornozelo", "https://www.youtube.com/watch?v=l41SoRwyWJA"),
]


# ──────────────────────────────────────────────────────────────
# FUNÇÕES DE SINCRONIZAÇÃO DO BANCO
# ──────────────────────────────────────────────────────────────

def apagar_catalogo(session):
    """Remove todos os registros de exercicios_catalogo."""
    deletados = session.query(ExercicioCatalogo).delete()
    session.commit()
    print(f"[REMOVER] {deletados} exercicios removidos do catalogo.")


def popular_catalogo(session):
    """Insere ou atualiza todos os exercícios da lista com links de vídeo."""
    existentes = {e.nome: e for e in session.query(ExercicioCatalogo).all()}
    novos = 0
    atualizados = 0

    for i, item in enumerate(EXERCICIOS, start=1):
        nome = item[0]
        categoria = item[1]
        equipamento = item[2]
        musculo_principal = item[3]
        musculo_secundario = item[4]
        video_url = item[5] if len(item) > 5 else None

        if nome in existentes:
            # Atualiza o video_url do exercício existente se estiver vazio
            ex_existente = existentes[nome]
            if video_url and ex_existente.video_url != video_url:
                ex_existente.video_url = video_url
                atualizados += 1
            continue

        ex = ExercicioCatalogo(
            api_id=10000 + i,       # IDs locais a partir de 10000
            nome=nome,
            nome_en=None,
            descricao=None,
            categoria=categoria,
            equipamento=equipamento,
            musculo_principal=musculo_principal,
            musculo_secundario=musculo_secundario,
            video_url=video_url,
        )
        session.add(ex)
        novos += 1

    session.commit()
    print(f"[SUCESSO] {novos} novos exercícios inseridos e {atualizados} atualizados com vídeos.")


def main(recriar_tudo=False):
    Base.metadata.create_all(bind=db)
    Session = sessionmaker(bind=db)
    session = Session()

    if recriar_tudo:
        print("[AVISO] Apagando catálogo existente...")
        apagar_catalogo(session)

    print("[INFO] Sincronizando catálogo com demonstrações em vídeo...")
    popular_catalogo(session)
    session.close()
    print("\n[OK] Banco de dados de exercícios 100% atualizado com vídeos!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--recriar-tudo",
        action="store_true",
        help="Apaga os exercícios existentes e recria tudo do zero."
    )
    args = parser.parse_args()
    main(recriar_tudo=args.recriar_tudo)