import os
import re
import asyncio
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from yt_dlp import YoutubeDL

from config import DIR_PDFS, DIR_ANKI, DIR_MAPAS, DIR_AUDIO, DIR_TRANSCRICOES, BANCAS_DISPONIVEIS
from storage import carregar_dados, salvar_dados, atualizar_progresso, salvar_playlist
from downloader import sanitizar_nome
from transcriber import transcrever_audio
from ai_processor import gerar_analise_pedagogica
from pdf_builder import gerar_pdf_aula
from anki_exporter import exportar_para_anki
from mindmap_generator import gerar_mapa_mental_interativo, construir_arvore_padrao

import sys
app = FastAPI(title="Plataforma Concursos - Papiro Reverso")

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

STATIC_DIR = BASE_DIR / "static"
OUTPUT_DIR = BASE_DIR / "output"

# Monta diretórios estáticos
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")

class PlaylistRequest(BaseModel):
    url: str

class ProgressoRequest(BaseModel):
    video_id: str
    segundos: float
    duracao: float

class ConfigRequest(BaseModel):
    tema: str = "dark"
    intervalo_questoes: int = 30
    questoes_durante_aula: bool = True
    questoes_final_aula: bool = True
    tamanho_mapa_mental: str = "quarto"
    banca_preferida: str = "CEBRASPE (Certo/Errado)"

def extrair_info_playlist_rapido(url: str):
    """Extrai lista de vídeos da playlist de forma ágil sem baixar mídia."""
    ydl_opts = {
        'extract_flat': 'in_playlist',
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        if not info:
            raise ValueError("Não foi possível carregar a URL informada.")

        aulas = []
        if 'entries' in info:
            titulo_playlist = info.get('title', 'Playlist de Estudos')
            for idx, entry in enumerate(info['entries'], 1):
                if not entry:
                    continue
                v_id = entry.get('id')
                v_title = entry.get('title', f'Aula {idx}')
                v_duracao = entry.get('duration') or 0
                
                # Checa se já existe download local em audios
                nome_sanit = sanitizar_nome(v_title)
                caminho_local_audio = list(DIR_AUDIO.glob(f"*{nome_sanit[:25]}*.mp3"))
                arquivo_local = f"/output/audios/{caminho_local_audio[0].name}" if caminho_local_audio else None

                aulas.append({
                    "id": v_id,
                    "indice": idx,
                    "titulo": v_title,
                    "duracao": v_duracao,
                    "url_youtube": f"https://www.youtube.com/watch?v={v_id}" if v_id else url,
                    "arquivo_local": arquivo_local,
                    "baixado": bool(arquivo_local)
                })
        else:
            v_id = info.get('id')
            v_title = info.get('title', 'Aula do YouTube')
            v_duracao = info.get('duration') or 0
            nome_sanit = sanitizar_nome(v_title)
            caminho_local_audio = list(DIR_AUDIO.glob(f"*{nome_sanit[:25]}*.mp3"))
            arquivo_local = f"/output/audios/{caminho_local_audio[0].name}" if caminho_local_audio else None

            titulo_playlist = v_title
            aulas.append({
                "id": v_id,
                "indice": 1,
                "titulo": v_title,
                "duracao": v_duracao,
                "url_youtube": f"https://www.youtube.com/watch?v={v_id}" if v_id else url,
                "arquivo_local": arquivo_local,
                "baixado": bool(arquivo_local)
            })

        return titulo_playlist, aulas

@app.get("/")
def index():
    return FileResponse(str(STATIC_DIR / "index.html"))

@app.post("/api/playlist/carregar")
def carregar_playlist(req: PlaylistRequest):
    try:
        titulo_pl, aulas = extrair_info_playlist_rapido(req.url)
        salvar_playlist(req.url, titulo_pl, aulas)
        dados = carregar_dados()
        return {
            "status": "sucesso",
            "titulo": titulo_pl,
            "total_aulas": len(aulas),
            "aulas": aulas,
            "progresso": dados.get("progresso_aulas", {}),
            "configuracoes": dados.get("configuracoes", {})
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/playlist/dados")
def obter_dados():
    dados = carregar_dados()
    return dados

@app.post("/api/progresso")
def salvar_progresso_aula(req: ProgressoRequest):
    res = atualizar_progresso(req.video_id, req.segundos, req.duracao)
    return {"status": "ok", "progresso": res}

@app.post("/api/configuracoes")
def salvar_config(cfg: ConfigRequest):
    dados = carregar_dados()
    dados["configuracoes"] = cfg.dict()
    salvar_dados(dados)
    return {"status": "ok", "configuracoes": dados["configuracoes"]}

@app.get("/api/aula/{video_id}/conteudo")
def obter_conteudo_aula(video_id: str, banca: str = "CEBRASPE (Certo/Errado)"):
    """
    Retorna o mapa mental e as questoes interativas da aula.
    Gera dados estruturados alinhados com o tempo do video para pausar e exibir na tela!
    """
    dados = carregar_dados()
    
    # Procura a aula nos dados salvos
    aula_encontrada = None
    for pl in dados.get("playlists", {}).values():
        for a in pl.get("aulas", []):
            if a.get("id") == video_id:
                aula_encontrada = a
                break
        if aula_encontrada:
            break

    titulo_aula = aula_encontrada["titulo"] if aula_encontrada else f"Aula {video_id}"
    duracao = (aula_encontrada.get("duracao") or 600) if aula_encontrada else 600

    # Gera análise pedagógica adaptada à banca
    res_pedagogico = gerar_analise_pedagogica(
        f"Conteúdo completo da aula {titulo_aula} com tópicos e conceitos para concurso.",
        titulo_aula,
        banca=banca
    )

    # Associa timestamps específicos no vídeo para disparo das questões pop-up durante a aula!
    questoes = res_pedagogico.get("questoes", [])
    intervalo = dados.get("configuracoes", {}).get("intervalo_questoes", 30)

    # Distribui as questões ao longo do tempo do vídeo
    timestamps_questoes = []
    for idx, q in enumerate(questoes, 1):
        tempo_disparo = idx * intervalo
        if tempo_disparo >= duracao:
            tempo_disparo = max(15, duracao - (len(questoes) - idx + 1) * 15)
        timestamps_questoes.append({
            "tempo_segundos": tempo_disparo,
            "questao": q
        })

    # Constrói a árvore de nós do mapa mental com timestamps sincronizados com o vídeo
    arvore_mapa = res_pedagogico.get("mapa_mental")
    if not arvore_mapa or not isinstance(arvore_mapa, dict) or "filhos" not in arvore_mapa:
        arvore_mapa = construir_arvore_padrao(titulo_aula, res_pedagogico.get("conceitos", []))

    # Atribui timestamps ordenados aos nós do mapa mental para expansão durante o vídeo
    def atribuir_timestamps_mapa(no, tempo_base, passo):
        no["timestamp"] = tempo_base
        tempo_atual = tempo_base + passo
        if "filhos" in no and no["filhos"]:
            passo_filho = passo / len(no["filhos"])
            for f in no["filhos"]:
                tempo_atual = atribuir_timestamps_mapa(f, tempo_atual, passo_filho)
        return tempo_atual

    passo_inicial = max(10, duracao / max(1, len(arvore_mapa.get("filhos", [1])) + 1))
    atribuir_timestamps_mapa(arvore_mapa, 5, passo_inicial)

    return {
        "video_id": video_id,
        "titulo": titulo_aula,
        "banca": banca,
        "mapa_mental": arvore_mapa,
        "questoes_timeline": timestamps_questoes,
        "questoes_finais": questoes,
        "resumo_geral": res_pedagogico.get("resumo_geral", "")
    }

@app.post("/api/aula/{video_id}/gerar_pdf")
def endpoint_gerar_pdf_aula(video_id: str, banca: str = "CEBRASPE (Certo/Errado)"):
    dados = carregar_dados()
    titulo_aula = f"Aula_{video_id}"
    for pl in dados.get("playlists", {}).values():
        for a in pl.get("aulas", []):
            if a.get("id") == video_id:
                titulo_aula = a.get("titulo", titulo_aula)
                break

    nome_sanit = sanitizar_nome(titulo_aula)
    nome_pdf = f"Apostila_{nome_sanit}.pdf"
    caminho_pdf = DIR_PDFS / nome_pdf

    # Gera análise docente com foco na banca
    res_pedagogico = gerar_analise_pedagogica(
        f"Conteúdo completo da aula {titulo_aula} com conceitos e simulado.",
        titulo_aula,
        banca=banca
    )
    gerar_pdf_aula(res_pedagogico, nome_pdf)

    return {
        "status": "sucesso",
        "url_pdf": f"/output/apostilas_pdf/{nome_pdf}",
        "nome_arquivo": nome_pdf
    }

@app.post("/api/aula/{video_id}/gerar_anki")
def endpoint_gerar_anki_aula(video_id: str, banca: str = "CEBRASPE (Certo/Errado)"):
    dados = carregar_dados()
    titulo_aula = f"Aula_{video_id}"
    for pl in dados.get("playlists", {}).values():
        for a in pl.get("aulas", []):
            if a.get("id") == video_id:
                titulo_aula = a.get("titulo", titulo_aula)
                break

    nome_sanit = sanitizar_nome(titulo_aula)
    res_pedagogico = gerar_analise_pedagogica(
        f"Conteúdo completo da aula {titulo_aula} para flashcards de concurso.",
        titulo_aula,
        banca=banca
    )
    resultado_anki = exportar_para_anki(res_pedagogico, f"Flashcards_{nome_sanit}")

    return {
        "status": "sucesso",
        "url_apkg": f"/output/anki/Flashcards_{nome_sanit}.apkg",
        "total_cards": resultado_anki["total_cards"]
    }

def tarefa_baixar_aula_local(video_id: str, titulo: str):
    print(f"[Download Local] Iniciando download do vídeo/áudio: {titulo}")
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(DIR_AUDIO / f"{sanitizar_nome(titulo)}.%(ext)s"),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
        'quiet': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print(f"[Download Local] Concluído para {titulo}!")

@app.post("/api/aula/{video_id}/baixar")
def endpoint_baixar_aula_local(video_id: str, background_tasks: BackgroundTasks):
    dados = carregar_dados()
    titulo = f"Aula_{video_id}"
    for pl in dados.get("playlists", {}).values():
        for a in pl.get("aulas", []):
            if a.get("id") == video_id:
                titulo = a.get("titulo", titulo)
                break
    background_tasks.add_task(tarefa_baixar_aula_local, video_id, titulo)
    return {"status": "iniciado", "mensagem": f"Download de '{titulo}' em segundo plano."}

class DownloadPersonalizadoRequest(BaseModel):
    tipo: str = "video"  # "video" ou "audio"
    resolucao: str = "720p"  # "1080p", "720p", "480p"
    qualidade_audio: str = "192k"  # "192k", "64k"

def tarefa_download_custom(video_id: str, titulo: str, tipo: str, resolucao: str, qualidade: str):
    from downloader import baixar_video_personalizado, baixar_audio_personalizado
    url = f"https://www.youtube.com/watch?v={video_id}"
    if tipo == "video":
        baixar_video_personalizado(url, titulo, resolucao=resolucao)
    else:
        baixar_audio_personalizado(url, titulo, qualidade=qualidade)

@app.post("/api/aula/{video_id}/baixar_personalizado")
def baixar_personalizado_endpoint(video_id: str, req: DownloadPersonalizadoRequest, background_tasks: BackgroundTasks):
    dados = carregar_dados()
    titulo = f"Aula_{video_id}"
    for pl in dados.get("playlists", {}).values():
        for a in pl.get("aulas", []):
            if a.get("id") == video_id:
                titulo = a.get("titulo", titulo)
                break
    background_tasks.add_task(tarefa_download_custom, video_id, titulo, req.tipo, req.resolucao, req.qualidade_audio)
    return {
        "status": "iniciado",
        "mensagem": f"Download de '{titulo}' ({req.tipo} - {req.resolucao if req.tipo == 'video' else req.qualidade_audio}) iniciado em segundo plano!"
    }

class TecConcursosRequest(BaseModel):
    nome_aula: str
    conteudo_html: str

@app.post("/api/tec/gerar_pdf")
def gerar_pdf_tec_endpoint(req: TecConcursosRequest):
    from tec_parser import gerar_apostila_tec_concursos
    if not req.nome_aula or not req.conteudo_html:
        raise HTTPException(status_code=400, detail="Nome da aula e código HTML são obrigatórios.")
    
    caminho_pdf = gerar_apostila_tec_concursos(req.conteudo_html, req.nome_aula)
    nome_arquivo = Path(caminho_pdf).name
    return {
        "status": "sucesso",
        "url_pdf": f"/output/apostilas_pdf/{nome_arquivo}",
        "nome_arquivo": nome_arquivo
    }
