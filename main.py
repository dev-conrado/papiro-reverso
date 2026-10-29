import os
import sys
import re
from pathlib import Path
from config import DIR_PDFS, DIR_TRANSCRICOES, DIR_AUDIO, DIR_ANKI, BANCAS_DISPONIVEIS, BANCA_PADRAO
from downloader import obter_info_e_baixar_audio, sanitizar_nome
from transcriber import transcrever_audio
from ai_processor import gerar_analise_pedagogica
from pdf_builder import gerar_pdf_aula
from anki_exporter import exportar_para_anki

def processar_aula(aula_info: dict, idx: int, total: int, banca: str):
    titulo = aula_info["titulo"]
    print(f"\n==================================================")
    print(f"[{idx}/{total}] Processando: {titulo}")
    print(f"Banca Selecionada: {banca}")
    print(f"==================================================")

    caminho_audio = aula_info.get("caminho_audio")
    if not caminho_audio or not os.path.exists(caminho_audio):
        print(f"[Aviso] Audio nao encontrado para '{titulo}'. Pulando transcricao...")
        return None

    # 1. Transcrição / Legenda
    print(f"\n[Passo 1/4] Obtendo transcricao e legenda...")
    texto_transcricao = transcrever_audio(caminho_audio, titulo)
    print(f"[Sucesso] Transcricao pronta com {len(texto_transcricao.split())} palavras.")

    # 2. IA Pedagógica: Conceitos + 3 Questões com Gabarito Comentado
    print(f"\n[Passo 2/4] Processando analise pedagogica com a banca '{banca}'...")
    dados_pedagogicos = gerar_analise_pedagogica(texto_transcricao, titulo, banca=banca)

    # 3. Geração do PDF
    print(f"\n[Passo 3/4] Diagramando apostila em PDF...")
    nome_limpo = sanitizar_nome(titulo)
    nome_pdf = f"Apostila_{nome_limpo}.pdf"
    caminho_pdf = gerar_pdf_aula(dados_pedagogicos, nome_pdf)

    # 4. Exportação para Flashcards no Anki (.apkg e .tsv)
    print(f"\n[Passo 4/5] Gerando Flashcards para o Anki...")
    resultado_anki = exportar_para_anki(dados_pedagogicos, f"Flashcards_{nome_limpo}")

    # 5. Geração do Mapa Mental Interativo (Navegável por Setinhas do Teclado e Mouse)
    print(f"\n[Passo 5/5] Gerando Mapa Mental Interativo (Animado)...")
    from mindmap_generator import gerar_mapa_mental_interativo
    caminho_mapa = gerar_mapa_mental_interativo(dados_pedagogicos, f"MapaMental_{nome_limpo}.html")

    return {
        "titulo": titulo,
        "pdf": caminho_pdf,
        "anki_apkg": resultado_anki["apkg"],
        "anki_tsv": resultado_anki["tsv"],
        "mapa_mental": caminho_mapa,
        "total_cards": resultado_anki["total_cards"]
    }

def selecionar_banca_interativa() -> str:
    print("\nEscolha a Banca Examinadora desejada:")
    for idx, b in enumerate(BANCAS_DISPONIVEIS, 1):
        print(f"  [{idx}] {b}")
    opcao = input(f"Digite o numero (Padrao = 1 para {BANCA_PADRAO}): ").strip()
    
    if opcao.isdigit():
        num = int(opcao)
        if 1 <= num <= len(BANCAS_DISPONIVEIS):
            return BANCAS_DISPONIVEIS[num - 1]
    return BANCA_PADRAO

def main():
    print("=" * 65)
    print("SISTEMA AULA2CONCURSO - GERADOR DE APOSTILAS & ANKI")
    print("Baixa Audio -> Transcreve -> Conceitos -> PDF -> Flashcards")
    print("=" * 65)

    if len(sys.argv) > 1:
        url = sys.argv[1]
        banca = sys.argv[2] if len(sys.argv) > 2 else BANCA_PADRAO
    else:
        url = input("\nCole a URL da aula ou da playlist do YouTube: ").strip()
        banca = selecionar_banca_interativa()

    if not url:
        print("[Erro] Nenhuma URL fornecida. Encerrando.")
        return

    try:
        aulas = obter_info_e_baixar_audio(url)
        if not aulas:
            print("[Aviso] Nenhuma aula encontrada para processamento.")
            return

        print(f"\n[Total] Videos encontrados para processar: {len(aulas)}")

        materiais_gerados = []
        for i, aula in enumerate(aulas, 1):
            res = processar_aula(aula, i, len(aulas), banca=banca)
            if res:
                materiais_gerados.append(res)

        print("\n" + "=" * 65)
        print("PROCESSAMENTO CONCLUIDO COM SUCESSO!")
        print("=" * 65)
        print(f"Diretorio dos PDFs:   {DIR_PDFS}")
        print(f"Diretorio do Anki:    {DIR_ANKI}")
        print(f"Diretorio Mapas:      {DIR_MAPAS}")
        print("\nResumo dos Materiais Produzidos:")
        for m in materiais_gerados:
            print(f"\n  * Aula: {m['titulo']}")
            print(f"    - PDF:         {m['pdf']}")
            print(f"    - Anki:        {m['anki_apkg']} ({m['total_cards']} cards)")
            print(f"    - Mapa Mental: {m['mapa_mental']}")

    except Exception as e:
        print(f"\n[Erro] Ocorreu um erro durante a execucao: {e}")

if __name__ == "__main__":
    main()
