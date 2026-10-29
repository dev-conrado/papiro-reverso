import os
import re
from pathlib import Path
from fpdf import FPDF
from config import DIR_PDFS

class ApostilaConcursoProfissionalPDF(FPDF):
    def __init__(self, materia="DIREITO CONSTITUCIONAL", titulo_aula="AULA", banca="CEBRASPE"):
        super().__init__()
        self.materia = materia
        self.titulo_aula = titulo_aula
        self.banca = banca
        self.set_auto_page_break(auto=True, margin=16)

    def header(self):
        # Faixa superior azul marinho
        self.set_fill_color(15, 23, 42)  # Azul Escuro Profundo
        self.rect(0, 0, 210, 13, 'F')
        
        self.set_xy(12, 3)
        self.set_font('Helvetica', 'B', 8.5)
        self.set_text_color(248, 250, 252)
        self.cell(self.epw, 7, f"PAPIRO REVERSO | {self.materia.upper()} | FOCO: {self.banca.upper()}", 0, 0, 'L')
        self.set_xy(self.l_margin, 17)

    def footer(self):
        self.set_y(-12)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(148, 163, 184)
        self.cell(self.epw, 8, f"Aula: {self.titulo_aula[:50]}  |  Pagina {self.page_no()}/{{nb}}", 0, 0, 'C')

    def sanitizar(self, texto: str) -> str:
        if not texto:
            return ""
        mapa = {
            "“": '"', "”": '"', "‘": "'", "’": "'", "–": "-", "—": "-", "…": "...",
            "•": "*", "→": "->", "←": "<-", "§": "Art.", "°": "o", "ª": "a", "✔": "[OK]", "❌": "[X]"
        }
        for k, v in mapa.items():
            texto = texto.replace(k, v)
        return texto.encode('latin-1', 'replace').decode('latin-1')

    def titulo_secao(self, texto: str, subtitulo: str = ""):
        self.ln(2)
        self.set_x(self.l_margin)
        self.set_fill_color(238, 242, 255)
        self.set_draw_color(37, 99, 235)
        self.set_line_width(1.0)
        self.set_font('Helvetica', 'B', 11.5)
        self.set_text_color(30, 58, 138)
        self.cell(self.epw, 8.5, f"  {self.sanitizar(texto)}", border='L', fill=True, new_x="LMARGIN", new_y="NEXT")
        
        if subtitulo:
            self.set_font('Helvetica', 'I', 8.5)
            self.set_text_color(100, 116, 139)
            self.cell(self.epw, 5, f"   {self.sanitizar(subtitulo)}", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def caixa_alerta(self, titulo_caixa: str, conteudo: str, tipo="pegadinha"):
        self.set_x(self.l_margin)
        if tipo == "pegadinha":
            self.set_fill_color(255, 251, 235)  # Amarelo/Dourado Suave
            self.set_draw_color(217, 119, 6)    # Âmbar Alerta
            cor_titulo = (180, 83, 9)
        elif tipo == "lei":
            self.set_fill_color(239, 246, 255)  # Azul Suave
            self.set_draw_color(37, 99, 235)
            cor_titulo = (29, 78, 216)
        else:
            self.set_fill_color(240, 253, 244)  # Verde Suave
            self.set_draw_color(22, 163, 74)
            cor_titulo = (21, 128, 61)

        self.set_line_width(0.8)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(*cor_titulo)
        self.cell(self.epw, 6, f"  [!] {self.sanitizar(titulo_caixa)}", border='L', fill=True, new_x="LMARGIN", new_y="NEXT")
        
        self.set_x(self.l_margin)
        self.set_font('Helvetica', '', 8.8)
        self.set_text_color(51, 65, 85)
        self.multi_cell(self.epw, 4.6, f"   {self.sanitizar(conteudo)}", border='L', fill=True)
        self.ln(2.5)

    def tabela_comparativa(self, regra_geral: str, excecao_pegadinha: str):
        largura_col = (self.epw - 4) / 2
        
        self.set_x(self.l_margin)
        self.set_font('Helvetica', 'B', 8.5)
        self.set_fill_color(224, 231, 255)
        self.set_text_color(30, 58, 138)
        self.cell(largura_col, 6, "  REGRA GERAL (O QUE A NORMA DIZ)", border=1, fill=True)
        self.set_x(self.l_margin + largura_col + 4)
        self.set_fill_color(254, 226, 226)
        self.set_text_color(153, 27, 27)
        self.cell(largura_col, 6, "  EXCECAO OU PEGADINHA DA BANCA", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

        # Conteúdo das colunas
        self.set_font('Helvetica', '', 8.3)
        self.set_text_color(51, 65, 85)
        y_antes = self.get_y()
        self.multi_cell(largura_col, 4.4, self.sanitizar(regra_geral), border=1)
        y_depois1 = self.get_y()

        self.set_xy(self.l_margin + largura_col + 4, y_antes)
        self.multi_cell(largura_col, 4.4, self.sanitizar(excecao_pegadinha), border=1)
        y_depois2 = self.get_y()

        self.set_y(max(y_depois1, y_depois2) + 2)

def gerar_pdf_aula(dados_aula: dict, nome_arquivo_saida: str) -> str:
    materia = dados_aula.get("materia", "DIREITO PUBLICO")
    topico = dados_aula.get("topico", "AULA DE CONCURSO")
    banca = dados_aula.get("banca", "CEBRASPE")

    pdf = ApostilaConcursoProfissionalPDF(materia=materia, titulo_aula=topico, banca=banca)
    pdf.alias_nb_pages()
    pdf.add_page()

    # Capa Editorial / Cabeçalho Principal
    pdf.set_font('Helvetica', 'B', 15)
    pdf.set_text_color(15, 23, 42)
    pdf.multi_cell(pdf.epw, 7, pdf.sanitizar(topico.upper()))
    pdf.ln(1)

    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(pdf.epw, 5, pdf.sanitizar(f"GUIA DE REVISAO ESQUEMATIZADO | BANCA: {banca.upper()}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # 1. Visão Geral e Fundamentação
    pdf.titulo_secao("1. RESUMO EXECUTIVO & MAPA COGNITIVO DA MATERIA", "Visao panoramica para fixacao rapida de conteudo")
    resumo = dados_aula.get("resumo_geral", "")
    pdf.set_font('Helvetica', '', 9.2)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(pdf.epw, 4.8, pdf.sanitizar(resumo))
    pdf.ln(2)

    # 2. Esquematização dos Conceitos com Dicas de Professor
    pdf.titulo_secao("2. CONCEITOS-CHAVE ESQUEMATIZADOS & PEGADINHAS DE PROVA", "Analise pontual do que e cobrado nas provas")
    conceitos = dados_aula.get("conceitos", [])
    for idx, c in enumerate(conceitos, 1):
        nome_c = c.get("nome", f"Topico {idx}")
        explicacao = c.get("explicacao", "")
        pegadinha = c.get("pegadinha_banca", "")

        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(pdf.epw, 6, pdf.sanitizar(f"2.{idx}. {nome_c}"), new_x="LMARGIN", new_y="NEXT")

        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(71, 85, 105)
        pdf.multi_cell(pdf.epw, 4.6, pdf.sanitizar(explicacao))
        pdf.ln(1)

        if pegadinha:
            pdf.caixa_alerta("CUIDADO CONCURSEIRO! (COMO A BANCA TENTA TE DERRUBAR):", pegadinha, tipo="pegadinha")
        pdf.ln(1)

    # 3. Tabela Comparativa de Confronto
    pdf.titulo_secao("3. QUADRO COMPARATIVO: REGRA GERAL vs. PEGADINHA", "Tabela de memorizacao visual")
    pdf.tabela_comparativa(
        "A interpretacao das normas exige analise contextual. Os atos da administracao subordinam-se estritamente a previsao legal, preservando os direitos dos administrados.",
        "A banca examinadora frequentemente substitui termos como 'discricionario' por 'vinculado', ou omite excecoes legais para tornar assertivas incorretas."
    )
    pdf.ln(2)

    # 4. Questões de Concurso no Padrão Exato da Banca
    pdf.titulo_secao(f"4. SIMULADO DIRECIONADO - ESTILO {banca.upper()}", "Treinamento pratico com foco no gabarito")
    questoes = dados_aula.get("questoes", [])
    for q in questoes:
        num = q.get("numero", 1)
        enunciado = q.get("enunciado", "")
        alternativas = q.get("alternativas", {})

        pdf.set_font('Helvetica', 'B', 9.5)
        pdf.set_text_color(15, 23, 42)
        pdf.multi_cell(pdf.epw, 5, pdf.sanitizar(f"QUESTAO {num} ({banca}): {enunciado}"))
        pdf.ln(1)

        pdf.set_font('Helvetica', '', 8.8)
        ordem = ["C", "E"] if ("C" in alternativas and "E" in alternativas) else ["A", "B", "C", "D", "E"]
        for letra in ordem:
            if letra in alternativas:
                pdf.multi_cell(pdf.epw, 4.4, pdf.sanitizar(f"   ({letra}) {alternativas[letra]}"))
        pdf.ln(2)

    # 5. Gabarito Comentado com Rigor Docente
    pdf.titulo_secao("5. GABARITO COMENTADO ALTERNATIVA POR ALTERNATIVA", "Justificativa minuciosa com indicacao de erro e acerto")
    for q in questoes:
        num = q.get("numero", 1)
        gab = str(q.get("gabarito", "")).upper()
        comentarios = q.get("comentarios", {})

        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(pdf.epw, 5.5, pdf.sanitizar(f"Questao {num} - Gabarito Oficial: Alternativa ({gab})"), new_x="LMARGIN", new_y="NEXT")

        ordem_c = ["C", "E"] if ("C" in comentarios and "E" in comentarios) else ["A", "B", "C", "D", "E"]
        for letra in ordem_c:
            if letra in comentarios:
                coment = comentarios[letra]
                eh_gab = (letra == gab or (letra == "C" and gab in ["C", "CERTO"]))

                pdf.set_font('Helvetica', 'B', 8.5)
                if eh_gab:
                    pdf.set_text_color(22, 163, 74)
                    pdf.cell(pdf.epw, 4.5, f"   -> Item ({letra}) [GABARITO / ASSERTIVA CORRETA]:", new_x="LMARGIN", new_y="NEXT")
                else:
                    pdf.set_text_color(220, 38, 38)
                    pdf.cell(pdf.epw, 4.5, f"   -> Item ({letra}) [INCORRETA / ERRO DA ASSERTIVA]:", new_x="LMARGIN", new_y="NEXT")

                pdf.set_font('Helvetica', '', 8.4)
                pdf.set_text_color(71, 85, 105)
                pdf.multi_cell(pdf.epw, 4.2, pdf.sanitizar(f"      {coment}"))
                pdf.ln(0.8)
        pdf.ln(2)

    caminho_final = DIR_PDFS / nome_arquivo_saida
    pdf.output(str(caminho_final))
    print(f"[PDF Docente] Gerado com excelencia em:\n   {caminho_final}")
    return str(caminho_final)
