import os
import re
from pathlib import Path
import whisper
from config import DIR_TRANSCRICOES, WHISPER_MODEL

def limpar_vtt_srt(caminho_legenda: Path) -> str:
    """Converte arquivo VTT/SRT em texto limpo e legível."""
    with open(caminho_legenda, 'r', encoding='utf-8', errors='ignore') as f:
        linhas = f.readlines()

    texto_filtrado = []
    linha_anterior = ""
    for linha in linhas:
        linha_limpa = linha.strip()
        # Ignora cabeçalhos WebVTT e timestamps
        if not linha_limpa or "-->" in linha_limpa or linha_limpa.isdigit() or linha_limpa.startswith("WEBVTT"):
            continue
        # Remove tags HTML simples tipo <c> ou <00:00:01.000>
        linha_limpa = re.sub(r'<[^>]+>', '', linha_limpa).strip()
        if linha_limpa and linha_limpa != linha_anterior:
            texto_filtrado.append(linha_limpa)
            linha_anterior = linha_limpa

    return " ".join(texto_filtrado)

def transcrever_audio(caminho_audio: str, titulo: str) -> str:
    """
    Transcreve o arquivo de áudio usando Whisper local (ou reaproveita legenda VTT).
    Salva e retorna o texto completo.
    """
    caminho_p = Path(caminho_audio)
    
    # 1. Verifica se existe arquivo de legenda baixado junto
    pasta = caminho_p.parent
    legendas = list(pasta.glob(f"{caminho_p.stem}*.vtt")) + list(pasta.glob(f"{caminho_p.stem}*.srt"))
    
    if legendas:
        print(f"[Transcricao] Legenda oficial/automatica encontrada: {legendas[0].name}")
        texto = limpar_vtt_srt(legendas[0])
        if len(texto) > 100:
            salvar_transcricao(titulo, texto)
            return texto

    # 2. Transcrição com Whisper Local
    print(f"[Whisper] Carregando modelo '{WHISPER_MODEL}'...")
    modelo = whisper.load_model(WHISPER_MODEL)
    
    print(f"[Whisper] Transcrevendo audio: {caminho_p.name} ...")
    resultado = modelo.transcribe(str(caminho_p), language="pt")
    texto = resultado.get("text", "").strip()

    salvar_transcricao(titulo, texto)
    return texto

def salvar_transcricao(titulo: str, texto: str) -> Path:
    nome_arquivo = re.sub(r'[\\/*?:"<>|]', "", titulo).strip()[:80] + ".txt"
    caminho_txt = DIR_TRANSCRICOES / nome_arquivo
    with open(caminho_txt, "w", encoding="utf-8") as f:
        f.write(texto)
    print(f"[Sucesso] Transcricao salva em: {caminho_txt}")
    return caminho_txt
