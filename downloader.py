import os
import re
from pathlib import Path
from yt_dlp import YoutubeDL
from config import DIR_AUDIO

def sanitizar_nome(nome: str) -> str:
    """Remove caracteres inválidos para nomes de arquivos no Windows."""
    nome_limpo = re.sub(r'[\\/*?:"<>|]', "", nome)
    return nome_limpo.strip()[:80]

def obter_info_e_baixar_audio(url: str):
    """
    Processa uma URL de vídeo ou playlist do YouTube.
    Baixa somente o áudio e tenta extrair legendas automáticas/nativas caso existam.
    Retorna uma lista de dicionários com os metadados de cada aula baixada.
    """
    print(f"\n[Downloader] Consultando informacoes da URL: {url}")

    # Configuração do yt-dlp para download de áudio
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(DIR_AUDIO / '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['pt', 'pt-BR', 'en'],
        'subtitlesformat': 'vtt/srt/best',
        'quiet': False,
        'no_warnings': True,
        'ignoreerrors': True,
    }

    aulas_processadas = []

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        
        if not info:
            raise ValueError("Não foi possível obter dados da URL fornecida.")

        # Se for uma playlist
        if 'entries' in info:
            entries = [e for e in info['entries'] if e]
            print(f"[Playlist] Detectada com {len(entries)} videos.")
            for idx, entry in enumerate(entries, 1):
                titulo = entry.get('title', f"Aula_{idx}")
                titulo_sanitizado = sanitizar_nome(titulo)
                caminho_mp3 = DIR_AUDIO / f"{titulo_sanitizado}.mp3"
                
                # Procura se há arquivo com nome similar caso yt-dlp tenha salvo
                if not caminho_mp3.exists():
                    arquivos_audio = list(DIR_AUDIO.glob(f"*{titulo_sanitizado[:30]}*.mp3"))
                    if arquivos_audio:
                        caminho_mp3 = arquivos_audio[0]

                aulas_processadas.append({
                    "id": entry.get("id"),
                    "titulo": titulo,
                    "url": entry.get("webpage_url", url),
                    "duracao_segundos": entry.get("duration", 0),
                    "caminho_audio": str(caminho_mp3) if caminho_mp3.exists() else None,
                    "canal": entry.get("uploader", "Canal Concurso"),
                })
        else:
            # Vídeo único
            titulo = info.get('title', "Aula_YouTube")
            titulo_sanitizado = sanitizar_nome(titulo)
            caminho_mp3 = DIR_AUDIO / f"{titulo_sanitizado}.mp3"
            
            if not caminho_mp3.exists():
                arquivos_audio = list(DIR_AUDIO.glob(f"*{titulo_sanitizado[:30]}*.mp3"))
                if arquivos_audio:
                    caminho_mp3 = arquivos_audio[0]

            aulas_processadas.append({
                "id": info.get("id"),
                "titulo": titulo,
                "url": info.get("webpage_url", url),
                "duracao_segundos": info.get("duration", 0),
                "caminho_audio": str(caminho_mp3) if caminho_mp3.exists() else None,
                "canal": info.get("uploader", "Canal Concurso"),
            })

    return aulas_processadas

def baixar_video_personalizado(url: str, titulo: str, resolucao: str = "720p") -> str:
    """
    Baixa vídeo com áudio em uma das 3 resoluções selecionadas:
    - '1080p' (Full HD)
    - '720p' (HD Padrão)
    - '480p' (Econômico / Compacto)
    """
    from config import DIR_VIDEOS
    nome_sanit = sanitizar_nome(titulo)
    caminho_saida = DIR_VIDEOS / f"{nome_sanit}_{resolucao}.mp4"

    limite_altura = "1080" if "1080" in resolucao else ("480" if "480" in resolucao else "720")
    
    ydl_opts = {
        'format': f'bestvideo[height<={limite_altura}]+bestaudio/best[height<={limite_altura}]/best',
        'outtmpl': str(DIR_VIDEOS / f"{nome_sanit}_{resolucao}.%(ext)s"),
        'merge_output_format': 'mp4',
        'quiet': False,
        'no_warnings': True,
    }

    print(f"[Download Vídeo] Baixando em {resolucao}: {titulo}")
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return str(caminho_saida)

def baixar_audio_personalizado(url: str, titulo: str, qualidade: str = "192k") -> str:
    """
    Baixa áudio em uma das 2 qualidades/tamanhos:
    - '192k' (Alta Fidelidade)
    - '64k' (Super Leve / Econômico)
    """
    nome_sanit = sanitizar_nome(titulo)
    bitrate = "64" if "64" in qualidade else "192"
    caminho_saida = DIR_AUDIO / f"{nome_sanit}_{bitrate}k.mp3"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(DIR_AUDIO / f"{nome_sanit}_{bitrate}k.%(ext)s"),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': bitrate,
        }],
        'quiet': False,
        'no_warnings': True,
    }

    print(f"[Download Áudio] Baixando em {bitrate}kbps: {titulo}")
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return str(caminho_saida)
