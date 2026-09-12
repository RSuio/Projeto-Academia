"""
Script para popular academias e personais trainers de demonstração.

Como usar:
    python popular_personais.py                   # Insere academias/personais/vínculos se não existirem
    python popular_personais.py --recriar-tudo    # Apaga os vínculos/academias/personais de demo e recria
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
from app.database.models import db, Base, Usuario, Academia, PersonalAcademia
from app.core.security import bcrypt_context

SENHA_DEMO = "personal123"

ACADEMIAS = [
    {
        "nome": "ForgeFit Matriz",
        "endereco": "Rua das Flores, 123",
        "cidade": "São Paulo",
        "telefone": "(11) 4002-8900",
    },
    {
        "nome": "ForgeFit Unidade Norte",
        "endereco": "Av. Paulista, 1547",
        "cidade": "São Paulo",
        "telefone": "(11) 4002-8901",
    },
    {
        "nome": "ForgeFit Unidade Sul",
        "endereco": "Rua das Palmeiras, 890",
        "cidade": "São Paulo",
        "telefone": "(11) 4002-8902",
    },
]

PERSONAIS = [
    {
        "nome": "Carlos Mendonça",
        "email": "carlos.mendonca@forgefitness.com.br",
        "especialidade": "Hipertrofia e Musculação",
        "bio": "Especialista em hipertrofia com 10 anos de experiência. Monta treinos periodizados para você evoluir com segurança.",
        "vinculos": [
            {"academia": "ForgeFit Matriz", "dias_semana": "Segunda, Quarta, Sexta", "horario_inicio": "07:00", "horario_fim": "12:00"},
            {"academia": "ForgeFit Unidade Norte", "dias_semana": "Terça, Quinta", "horario_inicio": "14:00", "horario_fim": "19:00"},
        ],
    },
    {
        "nome": "Marina Souza",
        "email": "marina.souza@forgefitness.com.br",
        "especialidade": "Corrida e Condicionamento",
        "bio": "Treinadora de corrida e condicionamento cardiovascular. Atleta de rua e apaixonada por provas de longa distância.",
        "vinculos": [
            {"academia": "ForgeFit Matriz", "dias_semana": "Segunda, Quarta", "horario_inicio": "08:00", "horario_fim": "11:00"},
            {"academia": "ForgeFit Unidade Sul", "dias_semana": "Terça, Quinta, Sábado", "horario_inicio": "06:00", "horario_fim": "10:00"},
        ],
    },
    {
        "nome": "Rafael Almeida",
        "email": "rafael.almeida@forgefitness.com.br",
        "especialidade": "CrossTraining e Funcional",
        "bio": "Coach de treinamento funcional e cross. Modalidades em grupo e individual, foco em força e mobilidade.",
        "vinculos": [
            {"academia": "ForgeFit Unidade Norte", "dias_semana": "Segunda, Quarta, Sexta", "horario_inicio": "18:00", "horario_fim": "21:00"},
            {"academia": "ForgeFit Unidade Sul", "dias_semana": "Terça, Quinta, Sábado", "horario_inicio": "08:00", "horario_fim": "12:00"},
        ],
    },
]


def apagar_demo(session):
    session.query(PersonalAcademia).delete()
    session.commit()
    for academia in session.query(Academia).all():
        session.delete(academia)
    session.commit()
    for personal in session.query(Usuario).filter(Usuario.admin == True).all():
        session.delete(personal)
    session.commit()
    print("[REMOVER] Vínculos, academias e personais de demonstração removidos.")


def popular(session):
    # Academias
    academias_por_nome = {a.nome: a for a in session.query(Academia).all()}
    for dados in ACADEMIAS:
        if dados["nome"] not in academias_por_nome:
            academia = Academia(
                nome=dados["nome"],
                endereco=dados["endereco"],
                cidade=dados["cidade"],
                telefone=dados["telefone"],
            )
            session.add(academia)
            academias_por_nome[dados["nome"]] = academia
    session.commit()

    # Personais (usuários admin) + vínculos
    personais_por_email = {p.email: p for p in session.query(Usuario).all()}
    novos = 0
    for dados in PERSONAIS:
        personal = personais_por_email.get(dados["email"])
        if not personal:
            personal = Usuario(
                nome=dados["nome"],
                email=dados["email"],
                senha=bcrypt_context.hash(SENHA_DEMO),
                admin=True,
                ativo=True,
                especialidade=dados["especialidade"],
                bio=dados["bio"],
            )
            session.add(personal)
            personais_por_email[dados["email"]] = personal
            novos += 1
        else:
            personal.especialidade = dados["especialidade"]
            personal.bio = dados["bio"]

    session.commit()

    # Vínculos — evita duplicar o mesmo par (personal, academia)
    vinculos_existentes = {
        (v.personal_id, v.academia_id): v
        for v in session.query(PersonalAcademia).all()
    }
    criados = 0
    for dados in PERSONAIS:
        personal = personais_por_email[dados["email"]]
        for vinculo in dados["vinculos"]:
            academia = academias_por_nome[vinculo["academia"]]
            chave = (personal.id, academia.id)
            if chave not in vinculos_existentes:
                session.add(PersonalAcademia(
                    personal_id=personal.id,
                    academia_id=academia.id,
                    dias_semana=vinculo["dias_semana"],
                    horario_inicio=vinculo["horario_inicio"],
                    horario_fim=vinculo["horario_fim"],
                ))
                criados += 1

    session.commit()
    print(f"[SUCESSO] {novos} personais criados e {criados} vínculos adicionados.")

    # Alunos de demonstração: vincula cada aluno sem personal a um personal, na ordem
    alunos_sem_personal = (
        session.query(Usuario)
        .filter(Usuario.admin == False, Usuario.personal_id.is_(None))
        .order_by(Usuario.id)
        .all()
    )
    personais_demo = [personais_por_email[d["email"]] for d in PERSONAIS]
    vinculados = 0
    for i, aluno in enumerate(alunos_sem_personal):
        if personais_demo:
            aluno.personal_id = personais_demo[i % len(personais_demo)].id
            vinculados += 1
    if vinculados:
        session.commit()
        print(f"[SUCESSO] {vinculados} alunos vinculados a personais de demonstração.")
    else:
        print("[INFO] Nenhum aluno novo para vincular.")


def main(recriar_tudo=False):
    Base.metadata.create_all(bind=db)
    Session = sessionmaker(bind=db)
    session = Session()

    if recriar_tudo:
        apagar_demo(session)

    print("[INFO] Sincronizando academias e personais de demonstração...")
    popular(session)
    session.close()
    print("\n[OK] Academias e personais prontos!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--recriar-tudo",
        action="store_true",
        help="Apaga academias/personais de demo existentes e recria tudo do zero."
    )
    args = parser.parse_args()
    main(recriar_tudo=args.recriar_tudo)