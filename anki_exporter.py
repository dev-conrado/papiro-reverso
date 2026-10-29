import os
import re
import csv
import random
from pathlib import Path
import genanki
from config import DIR_ANKI

# Modelo de Flashcard Personalizado para Concursos
ANKI_CSS = """
.card {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 16px;
    text-align: left;
    color: #24292f;
    background-color: #ffffff;
    padding: 18px;
    line-height: 1.5;
}
.tag-materia {
    display: inline-block;
    background-color: #1b365d;
    color: #ffffff;
    font-size: 11px;
    font-weight: bold;
    padding: 3px 8px;
    border-radius: 4px;
    margin-bottom: 10px;
    text-transform: uppercase;
}
.pergunta-titulo {
    font-size: 17px;
    font-weight: bold;
    color: #1b365d;
    margin-bottom: 12px;
}
.caixa-pegadinha {
    background-color: #fff8e6;
    border-left: 4px solid #d98324;
    padding: 10px 14px;
    margin-top: 14px;
    border-radius: 2px;
    font-size: 14px;
}
.pegadinha-label {
    font-weight: bold;
    color: #b4500a;
    display: block;
    margin-bottom: 4px;
}
.gabarito-badge {
    display: inline-block;
    padding: 5px 12px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 15px;
    margin-bottom: 12px;
}
.badge-certo { background-color: #e6f6eb; color: #1a7f37; border: 1px solid #1a7f37; }
.badge-errado { background-color: #ffebe9; color: #cf222e; border: 1px solid #cf222e; }
.item-comentario {
    margin-top: 6px;
    margin-bottom: 6px;
    font-size: 14px;
}
.alt-correta { color: #1a7f37; font-weight: bold; }
.alt-incorreta { color: #cf222e; font-weight: bold; }
"""

CONCEITO_MODEL = genanki.Model(
    1607392319,
    'Concurso - Conceito Chave',
    fields=[
        {'name': 'Materia'},
        {'name': 'Topico'},
        {'name': 'Frente'},
        {'name': 'Verso'},
        {'name': 'Pegadinha'},
    ],
    templates=[
        {
            'name': 'Card Conceito',
            'qfmt': '''
                <span class="tag-materia">{{Materia}} | {{Topico}}</span>
                <div class="pergunta-titulo">{{Frente}}</div>
            ''',
            'afmt': '''
                {{FrontSide}}
                <hr id="answer">
                <div>{{Verso}}</div>
                {{#Pegadinha}}
                <div class="caixa-pegadinha">
                    <span class="pegadinha-label">ATENCAO CONCURSEIRO / PEGADINHA:</span>
                    {{Pegadinha}}
                </div>
                {{/Pegadinha}}
            ''',
        },
    ],
    css=ANKI_CSS
)

QUESTAO_MODEL = genanki.Model(
    1607392320,
    'Concurso - Questao Comentada',
    fields=[
        {'name': 'Materia'},
        {'name': 'Topico'},
        {'name': 'Enunciado'},
        {'name': 'Alternativas'},
        {'name': 'Gabarito'},
        {'name': 'Comentarios'},
    ],
    templates=[
        {
            'name': 'Card Questao',
            'qfmt': '''
                <span class="tag-materia">{{Materia}} | {{Topico}}</span>
                <div class="pergunta-titulo">{{Enunciado}}</div>
                <div style="margin-top: 10px; font-size: 15px;">{{Alternativas}}</div>
            ''',
            'afmt': '''
                {{FrontSide}}
                <hr id="answer">
                <div style="margin-bottom: 8px;">
                    <strong>GABARITO:</strong> 
                    <span class="gabarito-badge {{#GabaritoCorreta}}badge-certo{{/GabaritoCorreta}}">{{Gabarito}}</span>
                </div>
                <div style="margin-top: 10px;">
                    <strong>ANALISE DAS ALTERNATIVAS:</strong><br>
                    {{Comentarios}}
                </div>
            ''',
        },
    ],
    css=ANKI_CSS
)

def gerar_id_deck(nome_materia: str) -> int:
    """Gera um ID numérico estável para o deck do Anki baseado no nome."""
    return abs(hash(nome_materia)) % (10 ** 9)

def exportar_para_anki(dados_aula: dict, nome_base_arquivo: str) -> dict:
    """
    Gera arquivo de flashcards .apkg e .tsv a partir dos conceitos e questões da aula.
    """
    materia = dados_aula.get("materia", "Concursos Publicos")
    topico = dados_aula.get("topico", "Aula")
    deck_id = gerar_id_deck(f"{materia}_{topico}")
    nome_deck = f"Concursos::{materia}::{topico}"

    deck = genanki.Deck(deck_id, nome_deck)
    linhas_tsv = []

    # 1. Cards Conceituais
    conceitos = dados_aula.get("conceitos", [])
    for idx, c in enumerate(conceitos, 1):
        nome_c = c.get("nome", f"Conceito {idx}")
        explicacao = c.get("explicacao", "").replace("\n", "<br>")
        pegadinha = c.get("pegadinha_banca", "").replace("\n", "<br>")
        frente = f"Qual a definição e regra essencial sobre: <b>{nome_c}</b>?"

        card_nota = genanki.Note(
            model=CONCEITO_MODEL,
            fields=[materia, topico, frente, explicacao, pegadinha]
        )
        deck.add_note(card_nota)

        # Registro TSV
        verso_tsv = f"{explicacao}"
        if pegadinha:
            verso_tsv += f" [PEGADINHA: {pegadinha}]"
        linhas_tsv.append([f"[{materia} - {topico}] {frente}", verso_tsv])

    # 2. Cards de Questões
    questoes = dados_aula.get("questoes", [])
    for q in questoes:
        num = q.get("numero", 1)
        enunciado = q.get("enunciado", "").replace("\n", "<br>")
        alternativas = q.get("alternativas", {})
        gabarito = q.get("gabarito", "")
        comentarios = q.get("comentarios", {})

        # Formatação HTML das alternativas
        alt_html_list = []
        for letra in ["C", "E", "A", "B", "C", "D", "E"]:
            if letra in alternativas:
                alt_html_list.append(f"<b>({letra})</b> {alternativas[letra]}")
        alt_html = "<br>".join(alt_html_list)

        # Formatação HTML dos comentários de cada alternativa
        coment_html_list = []
        for letra, coment in comentarios.items():
            eh_correta = (letra == gabarito or (letra == "C" and gabarito in ["C", "CERTO", "Certo"]))
            classe_cor = "alt-correta" if eh_correta else "alt-incorreta"
            status_txt = "CORRETA" if eh_correta else "INCORRETA"
            coment_html_list.append(
                f"<div class='item-comentario'><span class='{classe_cor}'>({letra}) [{status_txt}]:</span> {coment}</div>"
            )
        coment_html = "".join(coment_html_list)

        card_q = genanki.Note(
            model=QUESTAO_MODEL,
            fields=[
                materia,
                topico,
                f"Questão {num}: {enunciado}",
                alt_html,
                gabarito,
                coment_html
            ]
        )
        deck.add_note(card_q)

        # Registro TSV
        linhas_tsv.append([
            f"[{materia}] Questão {num}: {enunciado} <br> {alt_html}",
            f"GABARITO: ({gabarito}) <br> {coment_html}"
        ])

    # Salva arquivo .apkg
    nome_limpo = re.sub(r'[\\/*?:"<>|]', "", nome_base_arquivo).strip()[:70]
    caminho_apkg = DIR_ANKI / f"{nome_limpo}.apkg"
    genanki.Package(deck).write_to_file(str(caminho_apkg))

    # Salva arquivo .tsv
    caminho_tsv = DIR_ANKI / f"{nome_limpo}.tsv"
    with open(caminho_tsv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        for linha in linhas_tsv:
            writer.writerow(linha)

    print(f"[Anki] Flashcards gerados:")
    print(f"   * Pacote APKG: {caminho_apkg}")
    print(f"   * Tabela TSV:  {caminho_tsv}")

    return {
        "apkg": str(caminho_apkg),
        "tsv": str(caminho_tsv),
        "total_cards": len(conceitos) + len(questoes)
    }
