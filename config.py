import os
import sys
from pathlib import Path

# Diretórios base
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "output"

DIR_AUDIO = OUTPUT_DIR / "audios"
DIR_VIDEOS = OUTPUT_DIR / "videos"
DIR_TRANSCRICOES = OUTPUT_DIR / "transcricoes"
DIR_PDFS = OUTPUT_DIR / "apostilas_pdf"
DIR_ANKI = OUTPUT_DIR / "anki"
DIR_MAPAS = OUTPUT_DIR / "mapas_mentais"

for d in [DIR_AUDIO, DIR_VIDEOS, DIR_TRANSCRICOES, DIR_PDFS, DIR_ANKI, DIR_MAPAS]:
    d.mkdir(parents=True, exist_ok=True)

# Bancas suportadas
BANCAS_DISPONIVEIS = [
    "CEBRASPE (Certo/Errado)",
    "FGV (Casos Práticos - A a E)",
    "FCC (Letra de Lei e Súmulas - A a E)",
    "VUNESP (Objetiva e Direta - A a E)",
    "GERAL (Múltipla Escolha - A a D)"
]
BANCA_PADRAO = "CEBRASPE (Certo/Errado)"

# Configurações do Whisper
WHISPER_MODEL = "base"  # tiny, base, small

# Configurações de IA para Análise Pedagógica
# Provedor: 'ollama' (offline/gratuito) ou 'gemini' (API)
AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
